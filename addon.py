# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

from support.plugin import plugin
from support.common import LocalizedError, notify, lang
from xbmcswift2 import xbmcgui

if __name__ == '__main__':
    try:
        import lostfilm.routes

        plugin.run()
    except LocalizedError as e:
        e.log()
        if e.kwargs.get('dialog'):
            xbmcgui.Dialog().ok(lang(30000), *e.localized.split("|"))
        else:
            notify(e.localized)
        if e.kwargs.get('check_settings'):
            plugin.open_settings()
