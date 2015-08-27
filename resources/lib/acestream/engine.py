# -*- coding: utf-8 -*-

import time
import os
import sys
import logging
import urllib

from . import State, Status
from sink import Sink
from error import Error

try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict


class Engine:
    POLL_DELAY = 0.1
    ADDON_KEY = "n51LvQoTlJzNGaFxseRK-uvnvX-sD4Vm5Axwmc4UcoD-jruxmKsuJaH0eVgE"

    DEFAULT_HOST = "127.0.0.1"
    DEFAULT_PORT = 62062

    def __init__(self, host=DEFAULT_HOST, port=DEFAULT_PORT, save_path=None, save_encrypted=False,
                 log=None, on_playback_resumed=None, on_playback_paused=None, on_poll=None):
        self.log = log or logging.getLogger(__name__)
        self.state = None
        self.host = host
        self.port = port
        self.sink = None
        self.duration = None
        self.link = None
        self.is_ad = False
        self.is_live = False
        self.can_save = []
        self.files = None
        self.key = None
        self.version = None
        self.status = None
        self.progress = 0
        self.down_speed = 0
        self.up_speed = 0
        self.peers = 0
        self.download = 0
        self.upload = 0
        self.save_path = save_path
        self.save_indexes = []
        self.save_encrypted = save_encrypted
        self.saved_files = {}
        self.on_playback_resumed = on_playback_resumed
        self.on_playback_paused = on_playback_paused
        self.error = False
        self.error_msg = None
        self.last_event = None
        self.last_event_params = None
        self.auth_level = None
        self.infohash = None
        self.ready = False
        self.on_poll = on_poll or time.sleep

    def on_start(self, duration):
        self.duration = duration * 1000
        self.sink.send("DUR %s %s" % (self.link, self.duration))
        self.sink.send("PLAYBACK %s 0" % self.link)

    def on_pause(self):
        self.sink.send("EVENT pause")

    def on_resume(self):
        self.sink.send("EVENT play")

    def on_stop(self):
        self.sink.send("EVENT stop")
        self.sink.send("STOP")

    def on_seek(self, _time):
        self.sink.send("EVENT seek position=%s" % int(_time / 1000))

    def on_end(self):
        self.sink.send("PLAYBACK %s 100" % self.link)
        self.sink.send("EVENT stop")
        self.sink.send("STOP")

    def close(self):
        self.log.info("Closing AceStream engine")
        if self.sink:
            if self.state > 0:
                self.on_stop()
            self.sink.send("SHUTDOWN")

    def shutdown(self):
        if self.sink:
            self.sink.end()

    def _start(self):
        if not self._is_local():
            return True
        if self.save_path and not os.path.isdir(self.save_path):
            raise Error("Invalid download path (%s)" % self.save_path, Error.INVALID_DOWNLOAD_PATH)
        if sys.platform.startswith("win"):
            return self._start_windows()
        else:
            try:
                self._start_linux()
            except Error:
                self._start_android()

    def connect(self, timeout=20):
        if not self.sink:
            self.sink = Sink(self.host, on_receive=self.track_sink_event)
        start = time.time()
        connected = False
        started = False
        error = None
        while time.time() - start < timeout and not self.is_ready():
            if not connected:
                try:
                    self.sink.connect(self._get_ace_port())
                    self.sink.send("HELLOBG")
                    connected = True
                except Error as error:
                    if not started:
                        self._start()
                        started = True
            self.on_poll(self.POLL_DELAY)
        if not self.is_ready():
            self.sink = None
            raise error

    @staticmethod
    def _unique_id():
        import random
        return random.randint(0, 0x7fffffff)

    def _files(self, timeout=20):
        start = time.time()
        while time.time() - start < timeout and self.files is None and not self.error:
            self.on_poll(self.POLL_DELAY)
        if self.error:
            raise Error(self.error_msg, Error.CANT_LOAD_TORRENT)
        elif self.files is not None:
            return self.files
        else:
            raise Error("Timeout while getting files list", Error.TIMEOUT)

    def load_torrent(self, url, developer_id=0, offiliate_id=0, zone_id=0, timeout=20):
        self.sink.send("LOADASYNC %d TORRENT %s %d %d %d" % (self._unique_id(), url,
                                                             developer_id, offiliate_id, zone_id))
        return self._files(timeout)

    def load_infohash(self, infohash, developer_id=0, offiliate_id=0, zone_id=0, timeout=20):
        self.sink.send("LOADASYNC %d INFOHASH %s %d %d %d" % (self._unique_id(), infohash,
                                                              developer_id, offiliate_id, zone_id))
        return self._files(timeout)

    def load_data(self, data, developer_id=0, offiliate_id=0, zone_id=0, timeout=20):
        import base64
        self.sink.send("LOADASYNC %d RAW %s %d %d %d" % (self._unique_id(), base64.b64encode(data),
                                                         developer_id, offiliate_id, zone_id))
        return self._files(timeout)

    def load_pid(self, content_id, timeout=20):
        self.sink.send("LOADASYNC %d PID %d" % (self._unique_id(), content_id))
        return self._files(timeout)

    def _start_play(self, timeout=20):
        start = time.time()
        while time.time() - start < timeout and not self.state and not self.error:
            self.on_poll(self.POLL_DELAY)
        if self.error:
            raise Error(self.error_msg, Error.CANT_PLAY_TORRENT)
        elif self.state:
            return
        else:
            raise Error("Timeout while starting playback", Error.TIMEOUT)

    def play_torrent(self, url, indexes=None, developer_id=0, offiliate_id=0, zone_id=0, stream_id=0, timeout=20):
        indexes = indexes or [0]
        self.saved_files = {}
        self.save_indexes = indexes
        self.sink.send("START TORRENT %s %s %d %d %d %d" % (url, ",".join(str(index) for index in indexes),
                                                            developer_id, offiliate_id, zone_id, stream_id))
        self._start_play(timeout)

    def play_infohash(self, infohash, indexes=None, developer_id=0, offiliate_id=0, zone_id=0, timeout=20):
        indexes = indexes or [0]
        self.saved_files = {}
        self.save_indexes = indexes
        self.sink.send("START INFOHASH %s %s %d %d %d" % (infohash, ",".join(str(index) for index in indexes),
                                                          developer_id, offiliate_id, zone_id))
        self._start_play(timeout)

    def play_pid(self, content_id, indexes=None, timeout=20):
        indexes = indexes or [0]
        self.saved_files = {}
        self.save_indexes = indexes
        self.sink.send("START PID %d %s" % (content_id, ",".join(str(index) for index in indexes)))
        self._start_play(timeout)

    def play_data(self, data, indexes=None, developer_id=0, offiliate_id=0, zone_id=0, timeout=20):
        indexes = indexes or [0]
        self.saved_files = {}
        self.save_indexes = indexes
        import base64
        self.sink.send("START RAW %s %s %d %d %d" % (base64.b64encode(data), ",".join(str(index) for index in indexes),
                                                     developer_id, offiliate_id, zone_id))
        self._start_play(timeout)

    def play_url(self, url, indexes=None, developer_id=0, offiliate_id=0, zone_id=0, timeout=20):
        indexes = indexes or [0]
        self.saved_files = {}
        self.save_indexes = indexes
        self.sink.send("START URL %s %s %d %d %d" % (url, ",".join(str(index) for index in indexes),
                                                     developer_id, offiliate_id, zone_id))
        self._start_play(timeout)

    def play_efile(self, url, timeout=20):
        self.sink.send("START EFILE %s" % url)
        self._start_play(timeout)

    def get_status(self):
        return Status(state=self.state, status=self.status, progress=self.progress, down_speed=self.down_speed,
                      up_speed=self.up_speed, peers=self.peers, url=self.link, error=self.error_msg,
                      download=self.download, upload=self.upload)

    def _start_windows(self):
        import _winreg
        try:
            key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software\\AceStream")
            path = _winreg.QueryValueEx(key, "EnginePath")[0]
        except _winreg.error:
            # trying previous version
            try:
                import _winreg
                key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software\\TorrentStream")
                path = _winreg.QueryValueEx(key, "EnginePath")[0]
            except _winreg.error:
                raise Error("Can't find AceStream executable", Error.CANT_FIND_EXECUTABLE)
        try:
            self.log.info("Starting AceStream engine for Windows: %s" % path)
            os.startfile(path)
        except:
            raise Error("Can't start AceStream engine", Error.CANT_START_ENGINE)

    def _start_linux(self):
        import subprocess
        try:
            self.log.info("Starting AceStream engine for Linux")
            subprocess.Popen(["acestreamengine", "--client-console"])
        except OSError:
            try:
                subprocess.Popen('acestreamengine-client-console')
            except OSError:
                raise Error("AceStream engine is not installed", Error.CANT_START_ENGINE)

    def _start_android(self):
        try:
            import xbmc
            self.log.info("Starting AceStream engine for Android")
            xbmc.executebuiltin('XBMC.StartAndroidActivity("org.acestream.engine")')
        except:
            raise Error("AceStream engine is not installed", Error.CANT_START_ENGINE)

    def _get_ace_port(self):
        if not self._is_local() or not sys.platform.startswith("win"):
            return self.port
        import _winreg
        try:
            key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software\\AceStream")
            engine_exe = _winreg.QueryValueEx(key, "EnginePath")[0]
            path = engine_exe.replace("ace_engine.exe", "")
        except _winreg.error:
            # trying previous version
            try:
                key = _winreg.OpenKey(_winreg.HKEY_CURRENT_USER, "Software\\TorrentStream")
                engine_exe = _winreg.QueryValueEx(key, "EnginePath")[0]
                path = engine_exe.replace("tsengine.exe", "")
            except _winreg.error:
                return self.port
        pfile = os.path.join(path, "acestream.port")
        try:
            hfile = open(pfile, "r")
            return int(hfile.read())
        except IOError:
            return self.port

    def is_ready(self):
        return self.state >= 0

    def track_sink_event(self, event, params):
        self.last_event = event
        self.last_event_params = params

        if event == "STATUS":
            self._update_status(params)

        elif event == "START" or event == "PLAY":
            parts = params.split(" ")
            self.link = parts[0].replace(self.DEFAULT_HOST, self.host)

            if len(parts) > 1:
                if "ad=1" in parts:
                    self.is_ad = True
                    self.sink.send("PLAYBACK %s 100" % self.link)
                    self.link = None
                else:
                    self.is_ad = False

                if "stream=1" in parts:
                    self.is_live = True

        elif event == "AUTH":
            self.auth_level = int(params)
            self.state = State.IDLE

        elif event == "STATE":
            self.state = int(params)

        elif event == "EVENT":
            parts = params.split(" ")
            if len(parts) > 1 and "cansave" in parts:
                if self.save_path:
                    self._save_file(int(parts[1].split("=")[1]), parts[2].split("=")[1], parts[3].split("=")[1])

        elif event == "RESUME":
            if self.on_playback_resumed is not None:
                self.on_playback_resumed()

        elif event == "PAUSE":
            if self.on_playback_paused is not None:
                self.on_playback_paused()

        elif event == "HELLOTS":
            parts = params.split(" ")
            for part in parts:
                k, v = part.split("=")
                if k == "key":
                    self.key = v
                elif k == "version":
                    self.version = v
            cmd = "READY"
            if self.key:
                import hashlib
                sha1 = hashlib.sha1()

                sha1.update(self.key + self.ADDON_KEY)
                cmd = "READY key=%s-%s" % (self.ADDON_KEY.split("-")[0], sha1.hexdigest())

            self.sink.send(cmd)

        elif event == "LOADRESP":
            import json
            resp_json = json.loads(params[params.find("{"):len(params)])
            if resp_json["status"] == 100:
                self.error_msg = resp_json["message"]
                self.error = True
            else:
                self.infohash = resp_json["infohash"]
                if resp_json["status"] > 0:
                    self.files = OrderedDict((f[1], urllib.unquote(f[0])) for f in resp_json["files"])
                else:
                    self.files = OrderedDict()
        elif event == "SHUTDOWN":
            self.shutdown()

    def _save_file(self, index, infohash, _format):
        import urllib

        index = int(index)
        if self.save_path and index in self.save_indexes:
            filename = self.files and self.files[index] or infohash
            if _format == "encrypted":
                if not self.save_encrypted:
                    return
                filename += ".acemedia"
            path = os.path.join(self.save_path, filename)
            if not os.path.exists(path):
                dir_name = os.path.dirname(path)
                if not os.path.exists(dir_name):
                    os.mkdir(dir_name)
                self.sink.send("SAVE infohash=%s index=%s path=%s" % (infohash, index, urllib.quote(path)))
            self.saved_files[index] = path

    def _update_status(self, status_string):
        import re

        ss = re.compile("main:[a-z]+", re.S)
        s1 = re.findall(ss, status_string)[0]
        self.status = s1.split(":")[1]

        if self.status == "starting":
            self.progress = 0
        if self.status == "loading":
            self.progress = 0
        if self.status == "prebuf":
            parts = status_string.split(";")
            self.progress = int(parts[1])
            self.down_speed = int(parts[5])
            self.up_speed = int(parts[7])
            self.peers = int(parts[8])
            self.download = int(parts[10])
            self.upload = int(parts[12])
        if self.status == "buf":
            parts = status_string.split(";")
            self.progress = int(parts[1])
            self.down_speed = int(parts[5])
            self.up_speed = int(parts[7])
            self.peers = int(parts[8])
            self.download = int(parts[10])
            self.upload = int(parts[12])
        if self.status == "dl":
            parts = status_string.split(";")
            self.progress = int(parts[1])
            self.down_speed = int(parts[3])
            self.up_speed = int(parts[5])
            self.peers = int(parts[6])
            self.download = int(parts[8])
            self.upload = int(parts[10])
        if self.status == "check":
            self.progress = int(status_string.split(";")[1])
        if self.status == "idle":
            self.progress = 0
        if self.status == "wait":
            self.progress = 0
        if self.status == "err":
            parts = status_string.split(";")
            self.error = True
            self.error_id = parts[1]
            self.error_msg = parts[2]

    def _is_local(self):
        return self.host == self.DEFAULT_HOST
