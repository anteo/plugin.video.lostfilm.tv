# -*- coding: utf-8 -*-

import os
import sys
import datetime
import xbmcgui

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import lostfilm.routes
from xbmcswift2 import sleep, abort_requested, xbmc
from support.common import LocalizedError, lang, notify
from lostfilm.common import update_library, is_authorized
from support.plugin import plugin


def safe_update_library():
    try:
        if is_authorized():
            return update_library()
    except LocalizedError as e:
        e.log()
        if e.kwargs.get('dialog'):
            xbmcgui.Dialog().ok(lang(30000), *e.localized.split("|"))
        else:
            notify(e.localized)
    except Exception as e:
        plugin.log.exception(e)
        notify(lang(40410))
    finally:
        plugin.close_storages()
    return False

if __name__ == '__main__':
    sleep(5000)
    safe_update_library()
    next_run = None
    while not abort_requested():
        now = datetime.datetime.now()
        update_on_demand = plugin.get_setting('update-library', bool)
        if not next_run:
            next_run = now
            next_run += datetime.timedelta(hours=12)
            plugin.log.info("Scheduling next library update at %s" % next_run)
        elif now > next_run and not xbmc.Player().isPlaying() or update_on_demand:
            updated = safe_update_library()
            if update_on_demand:
                plugin.set_setting('update-library', False)
                if updated:
                    plugin.refresh_container()
            next_run = None
        sleep(1000)
