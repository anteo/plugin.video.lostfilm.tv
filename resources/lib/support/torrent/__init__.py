# -*- coding: utf-8 -*-
import hashlib
import urllib
import os
import urlparse
from collections import namedtuple
from datetime import datetime
from contextlib import closing

import requests
import requests.exceptions
from support.abstract.player import AbstractPlayer
from support.common import LocalizedEnum, LocalizedError
from util.bencode import bdecode, BTFailure
from util.encoding import ensure_str

__all__ = ['Torrent', 'TorrentStatus', 'TorrentFile', 'TorrentInfo', 'TorrentStream',
           'TorrentClient', 'TorrentClientError', 'TorrentStreamError', 'TorrentError']


class TorrentClientError(LocalizedError):
    pass


class TorrentStreamError(LocalizedError):
    pass


class TorrentStatus(LocalizedEnum):
    QUEUED = 0
    STOPPED = 1
    DOWNLOADING_METADATA = 2
    CHECK_PENDING = 3
    CHECKING = 4
    DOWNLOAD_PENDING = 5
    DOWNLOADING = 6
    SEED_PENDING = 7
    SEEDING = 8
    ALLOCATING = 9
    PREBUFFERING = 10
    STARTING_ENGINE = 11

    @property
    def lang_id(self):
        return 32020 + self.value

    def __cmp__(self, other):
        return cmp(self.value, other.value)


TorrentInfo = namedtuple('TorrentInfo', 'torrent_id, status, name, size, progress, downloaded, uploaded, upload_rate, '
                                        'download_rate, ratio, eta, peers, seeds, leeches, added, finished, '
                                        'download_dir')

TorrentFile = namedtuple('TorrentFile', 'index, path, length, md5sum')


class TorrentClient:
    addon_id = None
    addon_name = None

    def __init__(self):
        pass

    def list(self):
        raise NotImplementedError()

    def remove(self, torrent_id):
        """
        :type torrent_id: int
        """
        raise NotImplementedError()

    def add(self, torrent, download_dir):
        """
        :type download_dir: str
        :type torrent: Torrent
        """
        raise NotImplementedError()


class TorrentStream:
    saved_files_needed = False

    def __init__(self):
        pass

    def list(self, torrent):
        """
        :type torrent: Torrent
        """
        raise NotImplementedError()

    def play(self, player, torrent, list_item=None, file_id=None):
        """
        :type list_item: dict
        :type file_id: int
        :type torrent: Torrent
        :type player: AbstractPlayer
        """
        raise NotImplementedError()


class TorrentError(LocalizedError):
    pass


class Torrent:
    def __init__(self, url=None, data=None, file_name=None, requests_session=None):
        """
        :type data: str
        :type url: str
        :type file_name: str
        :type requests_session: requests.Session
        """
        self._url = url
        self._data = data
        self._file_name = file_name
        self._decoded = None
        self._requests_session = requests_session or requests.Session()
        pass

    def is_magnet(self):
        return self.url.startswith("magnet:")

    def has_url(self):
        return self._url is not None

    def has_data(self):
        return self._data is not None

    def has_file_name(self):
        return self._file_name is not None

    def download_locally(self, path):
        path = os.path.join(path, hashlib.md5(self.url).hexdigest() + ".torrent")
        if not os.path.exists(path):
            f = open(path, 'wb')
            with closing(f):
                f.write(self.data)
        self._file_name = path
        self._url = None
        return path

    @property
    def url(self):
        if self._url is None:
            if self.has_file_name():
                self._url = urlparse.urljoin('file:', urllib.pathname2url(ensure_str(self.file_name)))
            else:
                raise TorrentError(32016, "Torrent URL is unknown")
        return self._url

    @url.setter
    def url(self, url):
        self._url = url

    @property
    def file_name(self):
        if self._file_name is None:
            raise TorrentError(32017, "Torrent file name is unknown")
        if not os.path.exists(self._file_name):
            raise TorrentError(32018, "Torrent file is not found (%s)", self._file_name)
        return self._file_name

    @file_name.setter
    def file_name(self, file_name):
        self._file_name = file_name

    @property
    def data(self):
        if self._data is None:
            if self.has_url():
                if self.is_magnet():
                    raise TorrentError(32013, "Can't get torrent data for magnet link (%s)", self.url)
                try:
                    res = self._requests_session.get(self.url)
                    res.raise_for_status()
                    self._data = res.content
                except requests.exceptions.RequestException as e:
                    raise TorrentError(32014, "Can't fetch torrent data (%s)", self.url, cause=e)
            else:
                try:
                    f = open(self.file_name, 'rb')
                    with closing(f):
                        self._data = f.read()
                except IOError as e:
                    raise TorrentError(32014, "Can't get torrent data (%s)", self.file_name, cause=e)
        return self._data

    @data.setter
    def data(self, data):
        self._data = data
        self._decoded = None

    @property
    def decoded(self):
        if self._decoded is None:
            data = self.data
            try:
                self._decoded = bdecode(data)
            except BTFailure as e:
                raise TorrentError(32015, "Can't decode torrent data (invalid torrent link? %s)", self.url, cause=e)
        return self._decoded

    @property
    def announce(self):
        return self.decoded['announce']

    @property
    def created_by(self):
        return self.decoded['created by'] if 'created by' in self.decoded else None

    @property
    def name(self):
        return self.info['name'] if 'name' in self.info else None

    @property
    def comment(self):
        return self.decoded['comment'] if 'comment' in self.decoded else None

    @property
    def info(self):
        return self.decoded['info']

    @property
    def creation_date(self):
        return datetime.fromtimestamp(self.decoded['creation date']) if 'creation date' in self.decoded else None

    def is_private(self):
        return bool(self.info['private']) if 'private' in self.info else False

    @property
    def files(self):
        if 'files' in self.info:
            return [TorrentFile(i, os.path.join(*f['path']), f['length'], f['md5sum'] if 'md5sum' in f else None)
                    for i, f in enumerate(self.info['files'])]
        else:
            return [TorrentFile(0, self.info['name'], self.info['length'], self.info['md5sum']
                    if 'm5sum' in self.info else None)]
