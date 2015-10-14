# -*- coding: utf-8 -*-

import os
import sys
import shutil
import logging
import threading
from contextlib import closing

from util.causedexception import CausedException
from util.enum import Enum
from util.ordereddict import OrderedDict
from xbmcswift2 import xbmc, xbmcgui, xbmcvfs, direxists, ensure_unicode, actions
from support.plugin import plugin
from xbmcswift2.common import sleep, file_size, get_dir_size


ADDON_PATH = plugin.addon.getAddonInfo('path')
RESOURCES_PATH = os.path.join(ADDON_PATH, 'resources')

LOWERCASE_LETTERS = u'abcdefghijklmnopqrstuvwxyzабвгдеёжзийклмнопрстуфхцчшщъыьэюя'
UPPERCASE_LETTERS = u'ABCDEFGHIJKLMNOPQRSTUVWXYZАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'

lang = plugin.get_string
log = logging.getLogger(__name__)


def notify(message, delay=10000):
    plugin.notify(message, lang(30000), delay, plugin.addon.getAddonInfo('icon'))


def save_path(local=False):
    path = plugin.get_setting('save-path', unicode)
    if path == plugin.get_setting('temp-path', unicode):
        raise LocalizedError(33032, "Path for downloaded files and temporary path should not be the same",
                             check_settings=True)
    if not direxists(path):
        raise LocalizedError(33031, "Invalid save path", check_settings=True)
    if local:
        path = ensure_path_local(path)
    path = path.strip("\\/")
    return ensure_unicode(path)


def ensure_path_local(path):
    path = xbmc.translatePath(path)
    if "://" in path:
        if sys.platform.startswith('win') and path.lower().startswith("smb://"):
            path = path.replace("smb:", "").replace("/", "\\")
        else:
            raise LocalizedError(33030, "Downloading to an unmounted network share is not supported",
                                 check_settings=True)
    return ensure_unicode(path)


def temp_path():
    path = ensure_path_local(plugin.get_setting('temp-path', unicode))
    if not xbmcvfs.mkdir(path):
        raise LocalizedError(33030, "Invalid temporary path", check_settings=True)
    return path


class FileCopyingThread(threading.Thread):
    def __init__(self, src, dst, delete=False):
        super(FileCopyingThread, self).__init__()
        self.src = src
        self.dst = dst
        self.delete = delete
        self.tmp = self.dst + ".part"
        self.copied = False
        self.src_size = file_size(self.src)

    def run(self):
        if xbmcvfs.exists(self.dst):
            xbmcvfs.delete(self.dst)
        xbmcvfs.mkdirs(os.path.dirname(self.dst))
        log.info("Copying %s to %s...", self.src, self.dst)
        xbmcvfs.delete(self.tmp)
        if xbmcvfs.copy(self.src, self.tmp):
            log.info("Success.")
            self.copied = True
            if xbmcvfs.rename(self.tmp, self.dst):
                if self.delete and xbmcvfs.delete(self.src):
                    log.info("File %s deleted.", self.src)
            else:
                log.info("Renaming %s to %s failed.", self.tmp, self.dst)
                xbmcvfs.delete(self.tmp)
        else:
            log.info("Failed")

    def progress(self):
        if self.copied:
            return 100
        else:
            cur_size = xbmcvfs.exists(self.tmp) and file_size(self.tmp) or 0
            return self.src_size and cur_size * 100 / self.src_size or 0


class FileCopyThread(threading.Thread):
    def __init__(self, files, delete=False, on_finish=None):
        super(FileCopyThread, self).__init__()
        self.files = files
        self.delete = delete
        self.on_finish = on_finish

    def run(self):
        progress = xbmcgui.DialogProgressBG()
        with closing(progress):
            progress.create(lang(40163))
            for src, dst in self.files.iteritems():
                progress.update(0, message=src)
                copying_thread = FileCopyingThread(src, dst, self.delete)
                copying_thread.start()
                while copying_thread.is_alive():
                    sleep(250)
                    progress.update(copying_thread.progress())
            if self.on_finish:
                self.on_finish()


def copy_files(files, delete=False, on_finish=None):
    copying_thread = FileCopyThread(files, delete, on_finish)
    copying_thread.start()


def save_files(files, rename=False, on_finish=None):
    save = plugin.get_setting('save-files', int)
    if not save:
        on_finish()
        return
    src, dst = temp_path(), save_path()
    files_dict = {}
    for old_path in files:
        old_path = ensure_unicode(old_path)
        rel_path = os.path.relpath(old_path, src)
        new_path = os.path.join(dst, rel_path)
        if xbmcvfs.exists(new_path):
            if rename:
                if xbmcvfs.delete(old_path):
                    log.info("File %s deleted.", old_path)
            continue
        files_dict[old_path] = new_path
    if not files_dict:
        if on_finish:
            on_finish()
        return
    files_to_copy = {}
    if save != 2 or xbmcgui.Dialog().yesno(lang(30000), *lang(40162).split("|")):
        for n, old_path in enumerate(files):
            old_path = ensure_unicode(old_path)
            if old_path not in files_dict:
                continue
            new_path = files_dict[old_path]
            xbmcvfs.mkdirs(os.path.dirname(new_path))
            if rename:
                log.info("Renaming %s to %s...", old_path, new_path)
                if not xbmcvfs.rename(old_path, new_path):
                    log.info("Renaming failed. Trying to copy and delete old file...")
                    files_to_copy[old_path] = new_path
                else:
                    log.info("Success.")
            else:
                files_to_copy[old_path] = new_path
    if files_to_copy:
        copy_files(files_to_copy, delete=rename, on_finish=on_finish)
    elif on_finish:
        on_finish()


def purge_temp_dir():
    path = temp_path()
    temp_size = get_dir_size(path)
    max_size = plugin.get_setting('temp-max-size', int) * 1024 * 1024 * 1024
    log.info("Current temporary folder size / Max size: %d / %d", temp_size, max_size)
    if temp_size > max_size:
        log.info("Purging temporary folder...")
        shutil.rmtree(path, True)
        if not direxists(path):
            # noinspection PyBroadException
            if xbmcvfs.mkdirs(path):
                log.info("New temporary folder size: %d", get_dir_size(path))


def str_to_date(date_string, date_format='%Y-%m-%d'):
    """
    Instead of calling datetime.strptime directly, we need this hack because of Exception raised on second XBMC run,
    See: http://forum.kodi.tv/showthread.php?tid=112916
    """
    import datetime
    import time
    return datetime.date(*(time.strptime(date_string, date_format)[0:3]))


def date_to_str(date, date_format='%d.%m.%Y'):
    return date.strftime(date_format)


def singleton(func):
    memoized = []

    def singleton_wrapper(*args, **kwargs):
        if args or kwargs:
            raise TypeError("Singleton-wrapped functions shouldn't take"
                            "any argument! (%s)" % func)
        if not memoized:
            memoized.append(func())
        return memoized[0]

    return singleton_wrapper


def batch(iterable, size=None):
    from itertools import islice, chain
    size = size or plugin.get_setting('batch-results', int)
    sourceiter = iter(iterable)
    while True:
        batchiter = islice(sourceiter, size)
        yield list(chain([batchiter.next()], batchiter))


def with_fanart(item, url=None):
    if isinstance(item, list):
        return [with_fanart(i, url) for i in item]
    elif isinstance(item, dict):
        properties = item.setdefault("properties", {})
        if not properties.get("fanart_image"):
            if not url:
                properties["fanart_image"] = plugin.addon.getAddonInfo("fanart")
            else:
                properties["fanart_image"] = url
        return item


class LocalizedEnum(Enum):
    @property
    def lang_id(self):
        raise NotImplementedError()

    @property
    def localized(self):
        return lang(self.lang_id)

    @classmethod
    def strings(cls):
        d = [(i.name, i.localized(lang)) for i in cls]
        return OrderedDict(sorted(d, key=lambda t: t[1]))

    def __lt__(self, other):
        return self.localized < other.localized

    def __str__(self):
        return self.localized


class Attribute(LocalizedEnum):
    def get_lang_base(self):
        raise NotImplementedError()

    @property
    def lang_id(self):
        return self.get_lang_base() + self.id

    @property
    def id(self):
        return self.value[0]

    @property
    def filter_val(self):
        return self.value[1]

    def __repr__(self):
        return "<%s.%s>" % (self.__class__.__name__, self._name_)

    @classmethod
    def find(cls, what):
        for i in cls.__iter__():
            if what in i.value or i.name == what:
                return i
        return None


class LocalizedError(CausedException):
    def __init__(self, lang_code, reason, *args, **kwargs):
        CausedException.__init__(self, **kwargs)
        self.reason = reason
        self.reason_args = args
        self.lang_code = lang_code

    @property
    def localized(self):
        return lang(self.lang_code) % self.reason_args

    def __str__(self):
        if isinstance(self.reason, basestring):
            return self.reason % self.reason_args
        else:
            return str(self.reason)


def translate_string(s, from_letters, to_letters):
    from_letters = [ord(char) for char in from_letters]
    trans_table = dict(zip(from_letters, to_letters))
    return s.translate(trans_table)


def uppercase(s):
    """
    Convert lowercase letters to uppercase. It's alternative to string.upper() on OpenELEC, where case altering
    doesn't affect cyrillic letters.
    :param s:
    :return: uppercase string
    """
    return translate_string(s, LOWERCASE_LETTERS, UPPERCASE_LETTERS)


def lowercase(s):
    """
    Convert uppercase letters to lowercase. It's alternative to string.lower() on OpenELEC, where case altering
    doesn't affect cyrillic letters.
    :param s:
    :return: lowercase string
    """
    return translate_string(s, UPPERCASE_LETTERS, LOWERCASE_LETTERS)


def toggle_watched_menu():
    return [(lang(40151), actions.toggle_watched())]


def refresh_menu():
    return [(lang(40152), actions.refresh())]


def download_torrent(torrent):
    from support import services
    client = services.torrent_client()
    path = plugin.get_setting('custom-save-path', unicode) \
        if plugin.get_setting('use-custom-save-path', bool) \
        else save_path(local=True)
    client.add(torrent, path)
    if plugin.has_addon(client.addon_id) and \
            xbmcgui.Dialog().yesno(lang(40160), *(lang(40161) % client.addon_name).split("|")):
        plugin.run_addon(client.addon_id)


def run_plugin():
    try:
        plugin.run()
    except LocalizedError as e:
        e.log()
        if e.kwargs.get('dialog'):
            xbmcgui.Dialog().ok(lang(30000), *e.localized.split("|"))
        else:
            notify(e.localized)
        if e.kwargs.get('check_settings'):
            plugin.open_settings()


def get_torrent(url):
    import support.services as services
    torrent = services.torrent(url)
    torrents_path = plugin.addon_data_path("torrents")
    xbmcvfs.mkdirs(torrents_path)
    torrent.download_locally(torrents_path)
    return torrent
