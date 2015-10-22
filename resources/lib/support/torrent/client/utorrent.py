# -*- coding: utf-8 -*-

import logging
import re
import urllib2
import os
import requests

from support.torrent import *


class UTorrentError(TorrentClientError):
    pass


class UTorrentClient(TorrentClient):
    addon_id = 'plugin.program.utorrent'
    addon_name = 'UTorrent'

    STATUS_MAPPING = {
        'error': TorrentStatus.STOPPED,
        'paused': TorrentStatus.STOPPED,
        'force_paused': TorrentStatus.STOPPED,
        'not_loaded': TorrentStatus.CHECK_PENDING,
        'checked': TorrentStatus.CHECKING,
        'queued': TorrentStatus.DOWNLOAD_PENDING,
        'downloading': TorrentStatus.DOWNLOADING,
        'force_downloading': TorrentStatus.DOWNLOADING,
        'finished': TorrentStatus.SEED_PENDING,
        'queued_seed': TorrentStatus.SEED_PENDING,
        'seeding': TorrentStatus.SEEDING,
        'force_seeding': TorrentStatus.SEEDING
    }

    def __init__(self, login, password, host='127.0.0.1', port=8080, log=None, requests_session=None):
        TorrentClient.__init__(self)
        self.login = login
        self.password = password
        self.log = log or logging.getLogger(__name__)
        self.url = 'http://' + host
        if port:
            self.url += ':' + str(port)
        self.url += '/gui/'
        self.requests_session = requests_session or requests.Session()

    def list(self):
        obj = self.action(list=1)

        res = []
        for r in obj.get('torrents', []):
            res.append(TorrentInfo(
                torrent_id=r[0],
                status=self.get_status(r[1], r[4] / 10),
                name=r[2],
                size=r[3],
                progress=r[4] / 10,
                downloaded=r[5],
                uploaded=r[6],
                ratio=r[7],
                upload_rate=r[8],
                download_rate=r[9],
                eta=r[10],
                peers=r[12] + r[14],
                leeches=r[12],
                seeds=r[14],
                added=r[23],
                finished=r[24],
                download_dir=r[26]
            ))

        return res

    def set_download_dir(self, download_dir):
        self.log.info("Setting download dir to %s", download_dir)
        try:
            if isinstance(download_dir, unicode):
                download_dir = download_dir.encode('windows-1251')
            return self.action(action='setsetting', s='dir_active_download', v=download_dir)
        except UTorrentError, e:
            if e.cause and isinstance(e.cause[0], urllib2.HTTPError) and e.cause[0].code == 400:
                raise UTorrentError(32009, "Can't set download dir: %s" % download_dir, cause=e, check_settings=True)
            raise e

    def get_settings(self):
        res = self.action(action='getsettings')['settings']
        self.log.info(res)
        return dict((item[0], item[2]) for item in res)

    def remove(self, torrent_id):
        self.log.info("Removing torrent %s from queue", torrent_id)
        return self.action(action='remove', hash=torrent_id)

    def _add(self, download_dir, **query):
        settings = self.get_settings()
        old_dir = settings.get('dir_active_download', None)
        download_dir = os.path.abspath(download_dir)
        self.set_download_dir(download_dir)
        try:
            return self.action(**query)
        except UTorrentError, e:
            raise UTorrentError(32008, "Can't add torrent", cause=e)
        finally:
            if old_dir:
                self.set_download_dir(old_dir)

    def add(self, torrent, download_dir):
        """
        :type torrent: Torrent
        """
        if torrent.has_data() or torrent.has_file_name():
            self.log.info("Adding torrent from data")
            return self._add(download_dir, action='add-file',
                             upload_files=[('torrent_file', ('torrent', torrent.data, 'application/x-bittorrent'))])
        elif torrent.has_url():
            self.log.info("Adding torrent from url (%s)", torrent.url)
            return self._add(download_dir, action='add-url', s=torrent.url)

    def action(self, **query):
        query['token'] = self.get_token()
        upload_files = query.pop('upload_files', None)

        try:
            response = self.requests_session.post(self.url, params=query,
                                                  auth=(self.login, self.password), files=upload_files)
            response.encoding = 'utf-8'
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise UTorrentError(32005, "Can't connect to uTorrent", cause=e, check_settings=True)

        try:
            res = response.json()
        except ValueError, e:
            raise UTorrentError(32004, "Malformed answer", cause=e)

        if 'error' in res:
            raise UTorrentError(32007, "uTorrent error: %s", res['error'])

        return res

    def get_token(self):
        try:
            response = self.requests_session.get(self.url + 'token.html', auth=(self.login, self.password))
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            if e.response is not None and e.response.status_code == 401:
                raise UTorrentError(32006, "Can't authenticate", cause=e, check_settings=True)
            raise UTorrentError(32005, "Can't connect to uTorrent", cause=e, check_settings=True)

        r = re.search("<div[^>]+id='token'[^>]*>([^<]+)</div>", response.content)
        if r:
            token = r.group(1).strip()
            if token:
                return token

        raise UTorrentError(32006, "Token not found")

    def get_status(self, status, progress):
        return self.STATUS_MAPPING[self.get_status_raw(status, progress)]

    @staticmethod
    def get_status_raw(status, progress):
        """
            Return status: not_loaded, error, checked,
                           paused, force_paused,
                           queued,
                           downloading,
                           finished, force_downloading
                           queued_seed, seeding, force_seeding
        """
        started = bool(status & 1)
        checking = bool(status & 2)
        # start_after_check = bool(status & 4)
        # checked = bool(status & 8)
        error = bool(status & 16)
        paused = bool(status & 32)
        queued = bool(status & 64)
        loaded = bool(status & 128)

        if not loaded:
            return 'not_loaded'

        if error:
            return 'error'

        if checking:
            return 'checked'

        if paused:
            if queued:
                return 'paused'
            else:
                return 'force_paused'

        if progress == 100:

            if queued:
                if started:
                    return 'seeding'
                else:
                    return 'queued_seed'

            else:
                if started:
                    return 'force_seeding'
                else:
                    return 'finished'
        else:

            if queued:
                if started:
                    return 'downloading'
                else:
                    return 'queued'

            else:
                if started:
                    return 'force_downloading'

        return 'stopped'
