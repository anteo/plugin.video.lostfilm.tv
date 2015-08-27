# @package xbmcaddon
# A class to access addon properties.
#

import os
from xbmcswift2.logger import log
from xbmcswift2.mockxbmc import utils


def _get_env_setting(name):
    return os.getenv('XBMCSWIFT2_%s' % name.upper())


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class Addon(object):
    def __init__(self, id=None):
        """Creates a new Addon class.

        id: string - id of the addon (autodetected in XBMC Eden)

        Example:
            self.Addon = xbmcaddon.Addon(id='script.recentlyadded')
        """
        # In CLI mode, xbmcswift2 must be run from the root of the addon
        # directory, so we can rely on getcwd() being correct.
        addonxml = os.path.join(os.getcwd(), 'addon.xml')
        self._info = {
            'id': id or utils.get_addon_id(addonxml),
            'name': utils.get_addon_name(addonxml),
        }
        self._strings = {}
        self._settings = {}

    def getAddonInfo(self, id):
        """Returns the value of an addon property as a string.

        id: string - id of the property that the module needs to access.

        Note:
            Choices are (author, changelog, description, disclaimer, fanart, icon, id, name, path
            profile, stars, summary, type, version)

        Example:
            version = self.Addon.getAddonInfo('version')
        """
        properties = ['author', 'changelog', 'description', 'disclaimer',
                      'fanart', 'icon', 'id', 'name', 'path', 'profile', 'stars', 'summary',
                      'type', 'version']
        assert id in properties, '%s is not a valid property.' % id
        return self._info.get(id, 'Unavailable')

    def getLocalizedString(self, id):
        """Returns an addon's localized 'unicode string'.

        id: integer - id# for string you want to localize.

        Example:
            locstr = self.Addon.getLocalizedString(id=6)
        """
        key = str(id)
        assert key in self._strings, 'id not found in English/strings.xml.'
        return self._strings[key]

    def getSetting(self, id):
        """Returns the value of a setting as a unicode string.

        id: string - id of the setting that the module needs to access.

        Example:
        apikey = self.Addon.getSetting('apikey')
        """
        log.warning('xbmcaddon.Addon.getSetting() has not been implemented in '
                    'CLI mode.')
        try:
            value = self._settings[id]
        except KeyError:
            # see if we have an env var
            value = _get_env_setting(id)
            if _get_env_setting(id) is None:
                value = raw_input('* Please enter a temporary value for %s: ' %
                                  id)
            self._settings[id] = value
        return value

    def setSetting(self, id, value):
        """Sets a script setting.

        id: string - id of the setting that the module needs to access.
        value: string or unicode - value of the setting.

        Example:
            self.Settings.setSetting(id='username', value='teamxbmc')
        """
        self._settings[id] = value

    def openSettings(self):
        """Opens this scripts settings dialog."""
        pass
