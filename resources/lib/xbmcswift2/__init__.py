"""
    xbmcswift2
    ----------

    A micro framework to enable rapid development of XBMC plugins.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
"""


try:
    import xbmc
    import xbmcgui
    import xbmcplugin
    import xbmcaddon
    import xbmcvfs
    CLI_MODE = False
except ImportError:
    CLI_MODE = True

    import sys
    from logger import log

    # Mock the XBMC modules
    from xbmcswift2.mockxbmc import xbmc, xbmcgui, xbmcplugin, xbmcaddon, xbmcvfs


from xbmcswift2.storage import Storage
from xbmcswift2.request import Request
from xbmcswift2.constants import SortMethod, VIEW_MODES
from xbmcswift2.listitem import ListItem
from xbmcswift2.logger import setup_log
from xbmcswift2.module import Module
from xbmcswift2.urls import AmbiguousUrlException, NotFoundException, UrlRule
from xbmcswift2.xbmcmixin import XBMCMixin
from xbmcswift2.plugin import Plugin
from xbmcswift2.common import (xbmc_url, enum, clean_dict, pickle_dict,
                               unpickle_args, unpickle_dict, download_page, unhex,
                               ensure_unicode, ensure_str, encode_fs, direxists,
                               decode_fs, sleep, abort_requested)
