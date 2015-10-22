# -*- coding: utf-8 -*-

from collections import namedtuple
from contextlib import closing
from support.mediadb import VideoDatabase, ScraperSettings, TvDbScraperSettings, TmDbScraperSettings
from xbmcswift2 import xbmc

# noinspection PyPep8Naming
import xml.etree.ElementTree as ET

Source = namedtuple('Source', ['type', 'path', 'label'])


class SourcesException(Exception):
    pass


class SourceAlreadyExists(SourcesException):
    def __init__(self, *args, **kwargs):
        label = kwargs.pop('label')
        super(SourceAlreadyExists, self).__init__(self, 'Source with label "%s" already exists' % label,
                                                  *args, **kwargs)


class UnknownMediaType(SourcesException):
    def __init__(self, *args, **kwargs):
        media_type = kwargs.pop('media_type')
        super(UnknownMediaType, self).__init__(self, 'Unknown media type: %s' % media_type,
                                               *args, **kwargs)


class Sources(object):
    SOURCES_XML_PATH = 'special://userdata/sources.xml'
    SOURCES_REAL_PATH = xbmc.translatePath(SOURCES_XML_PATH)

    def __init__(self):
        self.xml_tree = ET.parse(self.SOURCES_REAL_PATH)
        self.sources = None

    def get(self, media_type=None):
        if self.sources is None:
            self.sources = []
            for t in self.xml_tree.getroot():
                m_type = t.tag
                if media_type is not None and m_type != media_type:
                    continue
                for s in t.findall('source'):
                    label = s.find('name').text
                    path = s.find('path').text
                    self.sources.append(Source(m_type, path, label))
        return self.sources

    def has(self, media_type=None, label=None, path=None):
        return any((s.path == path or path is None) and (s.label == label or label is None)
                   for s in self.get(media_type))

    def add(self, media_type, path, label):
        if self.has(media_type, label):
            raise SourceAlreadyExists(label=label)
        for t in self.xml_tree.getroot():
            if t.tag == media_type:
                s = ET.SubElement(t, 'source')
                ET.SubElement(s, 'name').text = label
                ET.SubElement(s, 'path', {'pathversion': '1'}).text = path
                ET.SubElement(s, 'allowsharing').text = 'true'
                self.xml_tree.write(self.SOURCES_REAL_PATH, 'utf-8')
                return
        raise UnknownMediaType(media_type=media_type)

    def add_video(self, path, label, scraper_settings, scan_recursive=False,
                  use_folder_names=False, no_update=False):
        """
        :type scraper_settings: ScraperSettings
        """
        self.add('video', path, label)
        with closing(VideoDatabase()) as db:
            db.update_path(path, scraper_settings, scan_recursive, use_folder_names, no_update)
