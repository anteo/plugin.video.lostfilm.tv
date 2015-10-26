# -*- coding: utf-8 -*-
from contextlib import closing
from util.encoding import clean_filename, encode_fs, decode_fs
import time
import logging
import os


class Media(object):

    def __init__(self, folder, title, url, time_added=None, **payload):
        self.folder = folder
        self.title = title
        self.url = url
        self.time_added = time_added
        self.payload = payload

    def __eq__(self, other):
        d1 = self.__dict__.copy()
        d2 = other.__dict__.copy()
        del d1['payload']
        del d2['payload']
        return d1 == d2

    def __hash__(self):
        d = self.__dict__.copy()
        del d['payload']
        return hash(str(d))

    def __ne__(self, other):
        return not self == other

    @property
    def filename(self):
        return self.title

    @property
    def path(self):
        return os.path.join(clean_filename(self.folder), clean_filename(self.filename))


class Movie(Media):
    pass


class Episode(Media):
    def __init__(self, folder, title, season_number, episode_number, url, time_added=None, **payload):
        super(Episode, self).__init__(folder, title, url, time_added, **payload)
        self.season_number = season_number
        self.episode_number = episode_number

    @property
    def filename(self):
        episodes = self.episode_number if isinstance(self.episode_number, list) else [self.episode_number]
        episodes_str = "".join('x%02d' % e for e in episodes)
        return "%d%s %s" % (self.season_number, episodes_str, super(Episode, self).filename)


class StreamFile(object):
    def __init__(self, media, base_path):
        self.base_path = base_path
        self.media = media

    @property
    def path(self):
        return os.path.join(self.base_path, self.media.path + '.strm')

    @property
    def encoded_path(self):
        return encode_fs(self.path, errors='ignore')

    def create(self):
        with closing(open(self.encoded_path, 'w')) as fd:
            fd.write(self.media.url)
        self.touch()

    @property
    def timestamp(self):
        return time.mktime(self.media.time_added.timetuple()) if self.media.time_added else None

    def touch(self):
        timestamp = self.timestamp
        if timestamp:
            os.utime(self.encoded_path, (timestamp, timestamp))

    def is_updated(self):
        return self.timestamp and os.path.getmtime(self.encoded_path) != self.timestamp


class Library(object):

    def __init__(self, path):
        self.path = path
        self.log = logging.getLogger(__name__)
        self.created_medias = []
        self.added_medias = []
        self.removed_files = []
        self.updated_medias = []

        if not os.path.exists(self.encoded_path):
            os.mkdir(self.encoded_path)

    @property
    def encoded_path(self):
        return encode_fs(self.path, errors='ignore')

    def _remove_unwanted_files(self, all_files, path=None):
        if isinstance(all_files, list):
            all_files = set(all_files)
        if path is None:
            path = self.encoded_path

        files = os.listdir(path)
        existing_files = []
        for f in files:
            f = os.path.join(path, f)
            if os.path.isdir(f):
                self._remove_unwanted_files(all_files, f)
            else:
                existing_files.append(decode_fs(f))
        to_remove = [f for f in existing_files if f not in all_files]
        self.removed_files.extend(to_remove)
        for f in to_remove:
            self.log.info("'%s' has removed" % f)
            os.remove(encode_fs(f))

        files = os.listdir(path)
        if not files and self.encoded_path != path:
            self.log.info("'%s' has removed" % decode_fs(path))
            os.rmdir(path)

    def sync(self, medias):
        """
        :type medias: list[Media]
        """
        self.created_medias = []
        self.added_medias = []
        self.updated_medias = []

        created_dirs = []
        all_files = []
        self.log.info('Starting library sync...')
        for media in medias:
            f = StreamFile(media, self.path)
            path = f.path
            encoded_path = encode_fs(path, errors='ignore')
            all_files.append(path)
            if os.path.exists(encoded_path):
                if f.is_updated():
                    self.log.info("'%s' has updated" % path)
                    self.updated_medias.append(media)
                    f.touch()
            else:
                dirname = os.path.dirname(encoded_path) + "/"
                if dirname in created_dirs:
                    self.created_medias.append(f)
                    self.log.info("'%s' has created" % path)
                elif not os.path.exists(dirname):
                    os.mkdir(dirname)
                    created_dirs.append(dirname)
                    self.created_medias.append(media)
                    self.log.info("'%s' has created" % path)
                else:
                    self.added_medias.append(media)
                    self.log.info("'%s' has added" % path)
                f.create()

        self._remove_unwanted_files(all_files)
        self.log.info('Library sync finished (%d file(s) created, %d added, %d updated, %d removed)',
                      len(self.created_medias), len(self.added_medias), len(self.updated_medias),
                      len(self.removed_files))
