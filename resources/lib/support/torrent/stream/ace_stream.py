# -*- coding: utf-8 -*-

import logging
import time

# noinspection PyDeprecation
from contextlib import closing, nested
from support.torrent import *
from xbmcswift2.common import abort_requested, sleep
from support.abstract.progress import AbstractTorrentTransferProgress, DummyTorrentTransferProgress
from support.abstract.player import AbstractPlayer
from acestream import Engine, Error, State, Status


class AceStreamError(TorrentStreamError):
    pass


class AbortError(Exception):
    pass


class AceStream(TorrentStream):
    POLL_DELAY = 0.5

    def __init__(self, engine, buffering_progress=None, playing_progress=None, log=None, playback_start_timeout=5):
        """
        :type engine: Engine
        :type playing_progress: AbstractTorrentTransferProgress
        :type buffering_progress: AbstractTorrentTransferProgress
        """
        TorrentStream.__init__(self)
        self.playing_progress = playing_progress or DummyTorrentTransferProgress()
        self.buffering_progress = buffering_progress or DummyTorrentTransferProgress()
        self.playback_start_timeout = playback_start_timeout
        self.log = log or logging.getLogger(__name__)
        self.engine = engine
        self._playing_aborted = False

    @staticmethod
    def _convert_engine_error(error):
        """
        :type error: Error
        """
        if error.code in [error.CANT_CONNECT]:
            return AceStreamError(33040, error.message, cause=error, check_settings=True)
        elif error.code in [error.CANT_SEND_DATA]:
            return AceStreamError(33041, error.message, cause=error)
        elif error.code in [error.CANT_FIND_EXECUTABLE]:
            return AceStreamError(33042, error.message, cause=error)
        elif error.code in [error.CANT_START_ENGINE]:
            return AceStreamError(33043, error.message, cause=error)
        elif error.code in [error.TIMEOUT]:
            return AceStreamError(33044, error.message, cause=error)
        elif error.code in [error.CANT_LOAD_TORRENT]:
            return AceStreamError(33045, error.message, cause=error)
        elif error.code in [error.CANT_PLAY_TORRENT]:
            return AceStreamError(33046, error.message, cause=error)
        elif error.code in [error.INVALID_DOWNLOAD_PATH]:
            return AceStreamError(33047, error.message, cause=error)

    @staticmethod
    def _convert_state(status):
        """
        :type status: Status
        """
        if status.state in [State.BUFFERING, State.PREBUFFERING]:
            return TorrentStatus.PREBUFFERING
        elif status.state in [State.CHECKING]:
            return TorrentStatus.CHECKING
        elif status.state in [State.IDLE]:
            return TorrentStatus.QUEUED
        elif status.state in [State.DOWNLOADING]:
            return TorrentStatus.DOWNLOADING
        elif status.state in [State.COMPLETED]:
            return TorrentStatus.SEEDING
        elif status.state in [State.ERROR]:
            raise AceStreamError(33049, "AceStream error (%s)", status.error)

    def play(self, player, torrent, list_item=None, file_id=None):
        """
        :type list_item: dict
        :type torrent: Torrent
        :type player: AbstractPlayer
        """
        list_item = list_item or {}
        self.engine.on_playback_resumed = player.play
        self.engine.on_playback_paused = player.pause
        self.engine.on_poll = self._poll_engine

        list_item.setdefault('label', torrent.name)
        try:
            with closing(self.engine) as engine:
                with closing(self.buffering_progress) as progress:
                    progress.open()
                    self.log.info("Starting AceStream engine...")
                    progress.update_status(TorrentStatus.STARTING_ENGINE)
                    engine.connect()
                    self.log.info("Loading transport file...")
                    progress.name = torrent.name
                    progress.update_status(TorrentStatus.DOWNLOADING_METADATA)
                    files = engine.load_data(torrent.data)
                    if file_id is not None:
                        if file_id not in files:
                            raise AceStreamError(33048, "Invalid file index specified (%d)" % file_id)
                    else:
                        if not files:
                            raise AceStreamError(33050, "No playable files detected")
                        file_id = files.iterkeys().next()
                    self.log.info("Start prebuffering...")
                    engine.play_data(torrent.data, [file_id])
                    while True:
                        status = engine.get_status()
                        if status.url:
                            list_item['path'] = status.url
                            break
                        state = self._convert_state(status)
                        update_status = [state, status.download, status.down_speed, status.up_speed,
                                         0, status.peers, status.progress]
                        progress.update_status(*update_status)
                        self._poll_engine(self.POLL_DELAY)

                with closing(self.playing_progress) as progress:
                    # noinspection PyDeprecation
                    with nested(player.attached(player.PLAYBACK_PAUSED, self.playing_progress.open),
                                player.attached(player.PLAYBACK_RESUMED, self.playing_progress.close),
                                player.attached(player.PLAYBACK_STARTED, self.engine.on_start),
                                player.attached(player.PLAYBACK_PAUSED, self.engine.on_pause),
                                player.attached(player.PLAYBACK_RESUMED, self.engine.on_resume),
                                player.attached(player.PLAYBACK_STOPPED, self.engine.on_stop),
                                player.attached(player.PLAYBACK_SEEK, self.engine.on_seek)):
                        self.log.info("Starting playback...")
                        player.play(list_item)
                        progress.name = torrent.name
                        progress.size = torrent.files[file_id].length
                        start = time.time()
                        while player.is_playing() or time.time() - start < self.playback_start_timeout:
                            status = engine.get_status()
                            state = self._convert_state(status)
                            update_status = [state, int(round(progress.size * status.progress / 100.0)),
                                             status.down_speed, status.up_speed, 0, status.peers, status.progress]
                            progress.update_status(*update_status)
                            player.get_percent()
                            self._poll_engine(self.POLL_DELAY)

                        # handling PLAYBACK_STOPPED and PLAYBACK_ENDED events
                        sleep(1000)
        except AbortError:
            self.log.info("Playback aborted.")
        except Error as err:
            raise self._convert_engine_error(err)
        if file_id in self.engine.saved_files:
            return [self.engine.saved_files[file_id]]
        return []

    def _poll_engine(self, delay):
        sleep(int(delay * 1000))
        if self._aborted():
            raise AbortError()

    def _aborted(self):
        return abort_requested() or self.buffering_progress.is_cancelled() or self.playing_progress.is_cancelled()

    def list(self, torrent):
        """
        :type torrent: Torrent
        """
        try:
            with closing(self.engine) as engine:
                engine.connect()
                files = engine.load_data(torrent.data)
        except Error as err:
            raise self._convert_engine_error(err)
        return [f for f in torrent.files if f.index in files]
