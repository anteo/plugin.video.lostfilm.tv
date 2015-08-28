"""
    xbmcswift2.actions
    ------------------

    This module contains wrapper functions for XBMC built-in functions.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
"""


def background(url):
    """This action will run an addon in the background for the provided URL.

    See 'XBMC.RunPlugin()' at
    http://wiki.xbmc.org/index.php?title=List_of_built-in_functions.
    """
    return 'XBMC.RunPlugin(%s)' % url


def play_media(media, is_dir=False, preview=False, play_offset=None):
    """Plays the media. This can be a playlist, music, or video file, directory, plugin or an Url.

    See 'XBMC.PlayMedia()' at
    http://wiki.xbmc.org/index.php?title=List_of_built-in_functions.
    """
    params = media
    if is_dir:
        params += ",isdir"
    if preview:
        params += ",1"
    if play_offset:
        params += ",playoffset=%d" % play_offset
    return 'XBMC.PlayMedia(%s)' % params


def update_view(url):
    """This action will update the current container view with provided url.

    See 'XBMC.Container.Update()' at
    http://wiki.xbmc.org/index.php?title=List_of_built-in_functions.
    """
    return 'XBMC.Container.Update(%s)' % url


def refresh():
    return 'XBMC.Container.Refresh()'


def toggle_watched():
    return 'XBMC.Action(ToggleWatched)'
