# -*- coding: utf-8 -*-

from xbmcswift2 import xbmcvfs, xbmc, encode_fs
# noinspection PyPep8Naming
import xml.etree.ElementTree as ET
import sqlite3
import os


class ScraperSettings(object):
    content = ""
    scraper_addon_id = ""

    def __init__(self, **settings):
        self.settings = settings

    @property
    def default_language(self):
        return xbmc.getLanguage(xbmc.ISO_639_1)

    @property
    def settings_xml(self):
        root = ET.Element('settings')
        for k, v in self.settings.iteritems():
            if isinstance(v, bool):
                v = "true" if v else "false"
            else:
                v = unicode(v)
            setting = ET.SubElement(root, 'setting')
            setting.set('id', k)
            setting.set('value', v)
        return ET.tostring(root, 'utf-8')


class MoviesScraperSettings(ScraperSettings):
    content = "movies"


class TvShowsScraperSettings(ScraperSettings):
    content = "tvshows"


class TvDbScraperSettings(TvShowsScraperSettings):
    scraper_addon_id = "metadata.tvdb.com"

    # noinspection PyPep8Naming
    def __init__(self, RatingS='TheTVDB', absolutenumber=False, dvdorder=False,
                 fallback=True, fanart=True, language=None):
        super(TvDbScraperSettings, self).__init__(RatingS=RatingS, absolutenumber=absolutenumber,
                                                  dvdorder=dvdorder, fallback=fallback, fanart=fanart,
                                                  language=language or self.default_language)


class TmDbScraperSettings(MoviesScraperSettings):
    scraper_addon_id = "metadata.themoviedb.org"

    # noinspection PyPep8Naming
    def __init__(self, RatingS='TMDb', TrailerQ='720p', certprefix='Rated ', fanart=True, keeporiginaltitle=False,
                 language=None, tmdbcertcountry=None, trailer=True):
        super(TmDbScraperSettings, self).__init__(RatingS=RatingS, TrailerQ=TrailerQ, certprefix=certprefix,
                                                  fanart=fanart, keeporiginaltitle=keeporiginaltitle,
                                                  language=language or self.default_language,
                                                  tmdbcertcountry=tmdbcertcountry,
                                                  trailer=trailer)


class MediaDatabaseException(Exception):
    pass


class MediaDatabase(object):
    BASE_PATH = 'special://database'

    def __init__(self, name, version=None):
        self.name = name
        self.version = version or self.find_last_version(name)
        self.conn = None
        if not xbmcvfs.exists(self.full_path):
            raise MediaDatabaseException("KODI database '%s', %s not found" %
                                         (self.name, "version %d" % self.version if self.version else "last version"))

    def find_last_version(self, name):
        dirs, files = xbmcvfs.listdir(self.BASE_PATH)
        matched_files = [f for f in files if f.startswith(name)]
        versions = [int(os.path.splitext(f[len(name):])[0]) for f in matched_files]
        if not versions:
            return 0
        return max(versions)

    def connect(self):
        path = encode_fs(self.fs_path)
        self.conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES, isolation_level=None)

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None

    def ensure_connected(self):
        if not self.conn:
            self.connect()

    @property
    def fs_path(self):
        return xbmc.translatePath(self.full_path)

    @property
    def full_path(self):
        return os.path.join(self.BASE_PATH, "%s%d.db" % (self.name, self.version))


class VideoDatabase(MediaDatabase):
    def __init__(self, version=None):
        super(VideoDatabase, self).__init__("MyVideos", version)

    def get_path(self, path):
        self.ensure_connected()
        c = self.conn.cursor()
        c.execute("SELECT * FROM path WHERE strPath=?", (path,))
        return c.fetchone()

    def path_exists(self, path):
        return bool(self.get_path(path))

    def update_path(self, path, scraper_settings, scan_recursive=False, use_folder_names=False, no_update=False):
        """
        :type scraper_settings: ScraperSettings
        """
        ss = scraper_settings
        scan_recursive = 2147483647 if scan_recursive else 0
        if self.path_exists(path):
            self.conn.execute(
                "UPDATE path SET strContent=?, strScraper=?, scanRecursive=?, "
                "useFolderNames=?, strSettings=?, noUpdate=?, exclude=0 WHERE strPath=?",
                (ss.content, ss.scraper_addon_id, scan_recursive, use_folder_names, ss.settings_xml, no_update, path))
        else:
            self.conn.execute(
                "INSERT INTO path (strPath, strContent, strScraper, scanRecursive, "
                "useFolderNames, strSettings, noUpdate, exclude, dateAdded) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, 0, DATETIME('now'))",
                (path, ss.content, ss.scraper_addon_id, scan_recursive, use_folder_names, ss.settings_xml, no_update))
