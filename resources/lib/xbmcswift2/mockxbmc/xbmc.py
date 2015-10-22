# @package xbmc
# Various classes and functions to interact with XBMC.
#

import tempfile
import os
import errno

from xbmcswift2 import log
from xbmcswift2.cli.create import get_value

CAPTURE_FLAG_CONTINUOUS = 1
CAPTURE_FLAG_IMMEDIATELY = 2
CAPTURE_STATE_DONE = 3
CAPTURE_STATE_FAILED = 4
CAPTURE_STATE_WORKING = 0
DRIVE_NOT_READY = 1
ENGLISH_NAME = 2
ISO_639_1 = 0
ISO_639_2 = 1
LOGDEBUG = 0
LOGERROR = 4
LOGFATAL = 6
LOGINFO = 1
LOGNONE = 7
LOGNOTICE = 2
LOGSEVERE = 5
LOGWARNING = 3
PLAYER_CORE_AUTO = 0
PLAYER_CORE_DVDPLAYER = 1
PLAYER_CORE_MPLAYER = 2
PLAYER_CORE_PAPLAYER = 3
PLAYLIST_MUSIC = 0
PLAYLIST_VIDEO = 1
SERVER_AIRPLAYSERVER = 2
SERVER_EVENTSERVER = 6
SERVER_JSONRPCSERVER = 3
SERVER_UPNPRENDERER = 4
SERVER_UPNPSERVER = 5
SERVER_WEBSERVER = 1
SERVER_ZEROCONF = 7
TRAY_CLOSED_MEDIA_PRESENT = 96
TRAY_CLOSED_NO_MEDIA = 64
TRAY_OPEN = 16

__author__ = 'Team XBMC <http://xbmc.org>'
__credits__ = 'Team XBMC'
__date__ = 'Sun Aug 18 16:43:16 CEST 2013'
__platform__ = 'ALL'
__version__ = '2.0'
abortRequested = False

TEMP_DIR = os.path.join(tempfile.gettempdir(), 'xbmcswift2_debug')
log.info('Using temp directory %s', TEMP_DIR)


def _create_dir(path):
    """Creates necessary directories for the given path or does nothing
    if the directories already exist.
    """
    try:
        os.makedirs(path)
    except OSError, exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
def translatePath(path):
    """Creates folders in the OS's temp directory. Doesn't touch any
    possible XBMC installation on the machine. Attempting to do as
    little work as possible to enable this function to work seamlessly.
    """
    valid_dirs = ['xbmc', 'home', 'temp', 'masterprofile', 'profile',
                  'subtitles', 'userdata', 'database', 'thumbnails', 'recordings',
                  'screenshots', 'musicplaylists', 'videoplaylists', 'cdrips', 'skin']

    assert path.startswith('special://'), 'Not a valid special:// path.'
    parts = path.split('/')[2:]
    assert len(parts) > 1, 'Need at least a single root directory'
    assert parts[0] in valid_dirs, '%s is not a valid root dir.' % parts[0]

    # We don't want to swallow any potential IOErrors here, so only makedir for
    # the root dir, the user is responsible for making any further child dirs
    _create_dir(os.path.join(TEMP_DIR, parts[0]))

    return os.path.join(TEMP_DIR, *parts)


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class Keyboard(object):
    def __init__(self, default='', heading='', hidden=False):
        """Creates a new Keyboard object with default text heading and hidden input flag if supplied.

        default: string - default text entry.
        heading: string - keyboard heading.
        hidden: boolean - True for hidden text entry.

        Example:
            kb = xbmc.Keyboard('default', 'heading', True)
            kb.setDefault('password') # optional
            kb.setHeading('Enter password') # optional
            kb.setHiddenInput(True) # optional
            kb.doModal()
            if (kb.isConfirmed()):
                text = kb.getText()
        """
        self._heading = heading
        self._default = default
        self._hidden = hidden
        self._confirmed = False
        self._input = None

    def setDefault(self, default):
        """Set the default text entry.

        default: string - default text entry.

        Example:
            kb.setDefault('password')
        """
        self._default = default

    def setHeading(self, heading):
        """Set the keyboard heading.

        heading: string - keyboard heading.

        Example:
            kb.setHeading('Enter password')
        """
        self._heading = heading

    def setHiddenInput(self, hidden):
        """Allows hidden text entry.

        hidden: boolean - True for hidden text entry.

        Example:
            kb.setHiddenInput(True)
        """
        self._hidden = hidden

    def doModal(self):
        """Show keyboard and wait for user action.

        autoclose: integer - milliseconds to autoclose dialog.

        Note:
            autoclose = 0 - This disables autoclose

        Example:
            kb.doModal(30000)
        """
        self._confirmed = False
        try:
            self._input = get_value(self._heading, self._default, hidden=self._hidden)
            self._confirmed = True
        except (KeyboardInterrupt, EOFError):
            pass

    def isConfirmed(self):
        """Returns False if the user cancelled the input.
        example:
        - if (kb.isConfirmed()):"""
        return self._confirmed

    def getText(self):
        """Returns the user input as a string.

        Note:
            This will always return the text entry even if you cancel the keyboard.
            Use the isConfirmed() method to check if user cancelled the keyboard.
        """
        return self._input


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class Player(object):
    def __init__(self, core=None):
        """Creates a new Player with as default the xbmc music playlist.

        Args:
            core: Use a specified playcore instead of letting xbmc decide the playercore to use.
                - xbmc.PLAYER_CORE_AUTO
                - xbmc.PLAYER_CORE_DVDPLAYER
                - xbmc.PLAYER_CORE_MPLAYER
                - xbmc.PLAYER_CORE_PAPLAYER
        """
        pass

    def play(self, item=None, listitem=None, windowed=False, statrpos=-1):
        """
        play([item, listitem, windowed, startpos]) -- Play this item.

        item : [opt] string - filename, url or playlist.
        listitem : [opt] listitem - used with setInfo() to set different infolabels.
        windowed : [opt] bool - true=play video windowed, false=play users preference.(default)
        startpos : [opt] int - starting position when playing a playlist. Default = -1

        *Note, If item is not given then the Player will try to play the current item
        in the current playlist.

        You can use the above as keywords for arguments and skip certain optional arguments.
        Once you use a keyword, all following arguments require the keyword.

        example:
        - listitem = xbmcgui.ListItem('Ironman')
        - listitem.setInfo('video', {'Title': 'Ironman', 'Genre': 'Science Fiction'})
        - xbmc.Player().play(url, listitem, windowed)
        - xbmc.Player().play(playlist, listitem, windowed, startpos)
        """
        pass

    def stop(self):
        """Stop playing."""
        pass

    def pause(self):
        """Pause playing."""
        pass

    def playnext(self):
        """Play next item in playlist."""
        pass

    def playprevious(self):
        """Play previous item in playlist."""
        pass

    def playselected(self):
        """Play a certain item from the current playlist."""
        pass

    def onPlayBackStarted(self):
        """Will be called when xbmc starts playing a file."""
        pass

    def onPlayBackEnded(self):
        """Will be called when xbmc stops playing a file."""
        pass

    def onPlayBackStopped(self):
        """Will be called when user stops xbmc playing a file."""

    def onPlayBackPaused(self):
        """Will be called when user pauses a playing file."""
        pass

    def onPlayBackResumed(self):
        """Will be called when user resumes a paused file."""
        pass

    def onPlayBackSeek(self, time, seekOffset):
        """
        onPlayBackSeek(time, seekOffset) -- onPlayBackSeek method.

         time           : integer - time to seek to.
         seekOffset     : integer - ?.

         Will be called when user seeks to a time
        """
        pass

    def onPlayBackSeekChapter(self, chapter):
        """
        onPlayBackSeekChapter(chapter) -- onPlayBackSeekChapter method.

         chapter        : integer - chapter to seek to.

         Will be called when user performs a chapter seek
        """
        pass

    def onPlayBackSpeedChanged(self, speed):
        """
        onPlayBackSpeedChanged(speed) -- onPlayBackSpeedChanged method.

         speed          : integer - current speed of player.

         *Note, negative speed means player is rewinding, 1 is normal playback speed.

         Will be called when players speed changes. (eg. user FF/RW)
        """
        pass

    def onQueueNextItem(self):
        """
        onQueueNextItem() -- onQueueNextItem method.

        Will be called when player requests next item
        """
        pass

    def isPlaying(self):
        """Returns True is xbmc is playing a file."""
        return False

    def isPlayingAudio(self):
        """Returns True is xbmc is playing an audio file."""
        return False

    def isPlayingVideo(self):
        """Returns True if xbmc is playing a video."""
        return False

    def getPlayingFile(self):
        """Returns the current playing file as a string.

        Raises:
            Exception: If player is not playing a file.
        """
        return ""

    def getVideoInfoTag(self):
        """Returns the VideoInfoTag of the current playing Movie.

        Raises:
            Exception: If player is not playing a file or current file is not a movie file.

        Note:
            This doesn't work yet, it's not tested.
        """
        return None

    def getMusicInfoTag(self):
        """Returns the MusicInfoTag of the current playing 'Song'.

        Raises:
            Exception: If player is not playing a file or current file is not a music file.
        """
        return None

    def getTotalTime(self):
        """Returns the total time of the current playing media in seconds.

        This is only accurate to the full second.

        Raises:
            Exception: If player is not playing a file.
        """
        return 0.0

    def getTime(self):
        """Returns the current time of the current playing media as fractional seconds.

        Raises:
            Exception: If player is not playing a file.
        """
        return 0.0

    def seekTime(self, pTime):
        """Seeks the specified amount of time as fractional seconds.

        The time specified is relative to the beginning of the currently playing media file.

        Raises:
            Exception: If player is not playing a file.
        """
        pass

    def setSubtitles(self, path):
        """Set subtitle file and enable subtitles.

        path: string or unicode - Path to subtitle.

        Example:
            setSubtitles('/path/to/subtitle/test.srt')
        """
        pass

    def getSubtitles(self):
        """Get subtitle stream name."""
        return ""

    def disableSubtitles(self):
        """Disable subtitles."""
        pass

    def getAvailableAudioStreams(self):
        """Get audio stream names."""
        return []

    def getAvailableSubtitleStreams(self):
        """
        getAvailableSubtitleStreams() -- get Subtitle stream names
        """
        return []

    def setAudioStream(self, stream):
        """Set audio stream.

        stream: int
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class PlayList(object):
    def __init__(self, playlist):
        """Retrieve a reference from a valid xbmc playlist

        playlist: int - can be one of the next values:
            0: xbmc.PLAYLIST_MUSIC
            1: xbmc.PLAYLIST_VIDEO

        Use PlayList[int position] or __getitem__(int position) to get a PlayListItem.
        """
        pass

    def __getitem__(self, item):
        return None

    def __len__(self):
        return 0

    def add(self, url, listitem=None, index=-1):
        """Adds a new file to the playlist.

        url: string or unicode - filename or url to add.
        listitem: listitem - used with setInfo() to set different infolabels.
        index: integer - position to add playlist item.

        Example:
            playlist = xbmc.PlayList(xbmc.PLAYLIST_VIDEO)
            video = 'F:\\movies\\Ironman.mov'
            listitem = xbmcgui.ListItem('Ironman', thumbnailImage='F:\\movies\\Ironman.tbn')
            listitem.setInfo('video', {'Title': 'Ironman', 'Genre': 'Science Fiction'})
            playlist.add(url=video, listitem=listitem, index=7)
        """
        pass

    def load(self, filename):
        """Load a playlist.

        Clear current playlist and copy items from the file to this Playlist filename can be like .pls or .m3u ...

        Returns False if unable to load playlist, True otherwise.
        """
        return False

    def remove(self, filename):
        """Remove an item with this filename from the playlist."""
        pass

    def clear(self):
        """Clear all items in the playlist."""
        pass

    def shuffle(self):
        """Shuffle the playlist."""
        pass

    def unshuffle(self):
        """Unshuffle the playlist."""
        pass

    def size(self):
        """Returns the total number of PlayListItems in this playlist."""
        return 0

    def getposition(self):
        """Returns the position of the current song in this playlist."""
        return 0


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class PlayListItem(object):
    """Creates a new PlaylistItem which can be added to a PlayList."""

    def getdescription(self):
        """Returns the description of this PlayListItem."""
        return ""

    def getduration(self):
        """Returns the duration of this PlayListItem."""
        return 0

    def getfilename(self):
        """Returns the filename of this PlayListItem."""
        return ""


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class InfoTagMusic(object):
    def getURL(self):
        """Returns a string."""
        return ""

    def getTitle(self):
        """Returns a string."""
        return ""

    def getArtist(self):
        """Returns a string."""
        return ""

    def getAlbumArtist(self):
        """Returns a string."""
        return ""

    def getAlbum(self):
        """Returns a string."""
        return ""

    def getGenre(self):
        """Returns a string."""
        return ""

    def getDuration(self):
        """Returns an integer."""
        return 0

    def getTrack(self):
        """Returns an integer."""
        return 0

    def getDisc(self):
        """Returns an integer."""
        return 0

    def getTrackAndDisc(self):
        """Returns an integer."""
        return 0

    def getReleaseDate(self):
        """Returns a string."""
        return ""

    def getListeners(self):
        """Returns an integer."""
        return 0

    def getPlayCount(self):
        """Returns an integer."""
        return 0

    def getLastPlayed(self):
        """Returns a string."""
        return ""

    def getComment(self):
        """Returns a string."""
        return ""

    def getLyrics(self):
        """Returns a string."""
        return ""


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class InfoTagVideo(object):
    def getDirector(self):
        """Returns a string."""
        return ""

    def getWritingCredits(self):
        """Returns a string."""
        return ""

    def getGenre(self):
        """Returns a string."""
        return ""

    def getTagLine(self):
        """Returns a string."""
        return ""

    def getPlotOutline(self):
        """Returns a string."""
        return ""

    def getPlot(self):
        """Returns a string."""
        return ""

    def getPictureURL(self):
        """Returns a string."""
        return ""

    def getTitle(self):
        """Returns a string."""
        return ""

    def getOriginalTitle(self):
        """Returns a string."""
        return ""

    def getVotes(self):
        """Returns a string."""
        return ""

    def getCast(self):
        """Returns a string."""
        return ""

    def getFile(self):
        """Returns a string."""
        return ""

    def getPath(self):
        """Returns a string."""
        return ""

    def getIMDBNumber(self):
        """Returns a string."""
        return ""

    def getYear(self):
        """Returns an integer."""
        return 0

    def getPremiered(self):
        """Returns a string."""
        return ""

    def getFirstAired(self):
        """Returns a string."""
        return ""

    def getRating(self):
        """Returns a float."""
        return 0.0

    def getPlayCount(self):
        """Returns an integer."""
        return 0

    def getLastPlayed(self):
        """Returns a string."""
        return ""


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class Monitor(object):
    """
    Monitor class.
    Monitor() -- Creates a new Monitor to notify addon about changes.
    """

    def onAbortRequested(self):
        """
        Deprecated!
        """
        pass

    def onDatabaseUpdated(self, database):
        """
        Deprecated!
        """
        pass

    def onScreensaverActivated(self):
        """
        onScreensaverActivated() -- onScreensaverActivated method.
        Will be called when screensaver kicks in
        """
        pass

    def onScreensaverDeactivated(self):
        """
        onScreensaverDeactivated() -- onScreensaverDeactivated method.
        Will be called when screensaver goes off
        """
        pass

    def onSettingsChanged(self):
        """
        onSettingsChanged() -- onSettingsChanged method.
        Will be called when addon settings are changed
        """
        pass

    def onDatabaseScanStarted(self, database):
        """
        Deprecated!
        """
        pass

    def onNotification(self, sender, method, data):
        """
        onNotification(sender, method, data)--onNotification method.

        sender : sender of the notification
        method : name of the notification
        data : JSON-encoded data of the notification

        Will be called when XBMC receives or sends a notification
        """
        pass

    def onCleanStarted(self, library=''):
        """
        onCleanStarted(library)--onCleanStarted method.

        library : video/music as string

        Will be called when library clean has started
        and return video or music to indicate which library is being cleaned
        """
        pass

    def onCleanFinished(self, library=''):
        """
        onCleanFinished(library)--onCleanFinished method.

        library : video/music as string

        Will be called when library clean has ended
        and return video or music to indicate which library has been cleaned
        """
        pass

    def onDPMSActivated(self):
        """
        onDPMSActivated() --onDPMSActivated method.

        Will be called when energysaving/DPMS gets active
        """
        pass

    def onDPMSDeactivated(self):
        """
        onDPMSDeactivated() --onDPMSDeactivated method.

        Will be called when energysaving/DPMS is turned off
        """
        pass

    def onScanFinished(self, library=''):
        """
        onScanFinished(library)--onScanFinished method.

        library : video/music as string

        Will be called when library scan has ended
        and return video or music to indicate which library has been scanned
        """
        pass

    def onScanStarted(self, library=''):
        """
        onScanStarted(library)--onScanStarted method.

        library : video/music as string

        Will be called when library scan has started
        and return video or music to indicate which library is being scanned
        """
        pass

    def waitForAbort(self, timeout):
        """
        waitForAbort([timeout]) -- Block until abort is requested, or until timeout occurs. If an
        abort requested have already been made, return immediately.
        Returns True when abort have been requested, False if a timeout is given and the operation times out.

        :param timeout: float - (optional) timeout in seconds. Default: no timeout.
        :return: bool
        """
        return False


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class RenderCapture(object):
    def capture(self, width, height, flags=None):
        """
        capture(width, height [, flags])--issue capture request.
        width : Width capture image should be rendered to
        height : Height capture image should should be rendered to
        flags : Optional. Flags that control the capture processing.
        The value for 'flags' could be or'ed from the following constants:
        - xbmc.CAPTURE_FLAG_CONTINUOUS : after a capture is done, issue a new capture request immediately
        - xbmc.CAPTURE_FLAG_IMMEDIATELY : read out immediately whencapture() is called, this can cause a busy wait
        """
        pass

    def getAspectRatio(self):
        """
        getAspectRatio() --returns aspect ratio of currently displayed video as a float number.
        """
        return 0.0

    def getCaptureState(self):
        """
        getCaptureState() --returns processing state of capture request.
        The returned value could be compared against the following constants:
         - xbmc.CAPTURE_STATE_WORKING : Capture request in progress.
         - xbmc.CAPTURE_STATE_DONE : Capture request done. The image could be retrieved withgetImage()
         - xbmc.CAPTURE_STATE_FAILED : Capture request failed.
        """
        return 0

    def getHeight(self):
        """
        getHeight() --returns height of captured image.
        """
        return 0

    def getImage(self):
        """
        getImage() --returns captured image as a bytearray.
        The size of the image isgetWidth() *getHeight() * 4
        """
        return bytearray()

    def getImageFormat(self):
        """
        getImageFormat() --returns format of captured image: 'BGRA' or 'RGBA'.
        """
        return ""

    def getWidth(self):
        """
        getWidth() --returns width of captured image.
        """
        return 0

    def waitForCaptureStateChangeEvent(self, msec):
        """
        waitForCaptureStateChangeEvent([msecs])--wait for capture state change event.
        msecs : Milliseconds to wait. Waits forever if not specified.
        The method will return 1 if the Event was triggered. Otherwise it will return 0.
        """
        return 0


# noinspection PyPep8Naming
def audioResume():
    """
    audioResume()--Resume Audio engine.

    example: xbmc.audioResume()
    """
    pass


# noinspection PyPep8Naming
def audioSuspend():
    """
    audioSuspend()--Suspend Audio engine.

     example:
         - xbmc.audioSuspend()
    """
    pass


# noinspection PyPep8Naming,PyUnusedLocal
def convertLanguage(language, format_):
    """
    convertLanguage(language, format)--Returns the given language converted to the given format as a string.

    language: string either as name in English, two letter code (ISO 639-1), or three letter code (ISO 639-2/T(B)

    format: format of the returned language string
    xbmc.ISO_639_1: two letter code as defined in ISO 639-1
    xbmc.ISO_639_2: three letter code as defined in ISO 639-2/T or ISO 639-2/B
    xbmc.ENGLISH_NAME: full language name in English (default)
    example:
     - language = xbmc.convertLanguage(English, xbmc.ISO_639_2)
     """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def enableNavSounds(yesNo):
    """
    enableNavSounds(yesNo)--Enables/Disables nav sounds
    yesNo : integer - enable (True) or disable (False) nav sounds
    example:
     - xbmc.enableNavSounds(True)
    """
    pass


# noinspection PyPep8Naming,PyUnusedLocal
def executeJSONRPC(jsonrpccommand):
    """
    executeJSONRPC(jsonrpccommand)--Execute an JSONRPC command.
    jsonrpccommand : string - jsonrpc command to execute.
    List of commands - http://wiki.xbmc.org/?title=JSON-RPC_API
    example:
    - response = xbmc.executeJSONRPC('{ "jsonrpc": "2.0", "method": "JSONRPC.Introspect", "id": 1 }')
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def executebuiltin(function):
    """
    executebuiltin(function)--Execute a built in XBMC function.
    function : string - builtin function to execute.
    List of functions - http://wiki.xbmc.org/?title=List_of_Built_In_Functions
    example:
     - xbmc.executebuiltin('XBMC.RunXBE(c:\avalaunch.xbe)')
    """
    pass


# noinspection PyPep8Naming,PyUnusedLocal
def executescript(script):
    """
    executescript(script)--Execute a python script.
    script : string - script filename to execute.
    example:
    - xbmc.executescript('special://home/scripts/update.py')
    """
    pass


# noinspection PyPep8Naming,PyUnusedLocal
def getCacheThumbName(path):
    """
    getCacheThumbName(path)--Returns a thumb cache filename.

    path : string or unicode - path to file

    example:
    - thumb = xbmc.getCacheThumbName('f:\videos\movie.avi')
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def getCleanMovieTitle(path, usefoldername):
    """
    getCleanMovieTitle(path[, usefoldername])--Returns a clean movie title and year string if available.

    path : string or unicode - String to clean
    bool : [opt] bool - use folder names (defaults to false)

    example:
    - title, year = xbmc.getCleanMovieTitle('/path/to/moviefolder/test.avi', True)
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def getCondVisibility(condition):
    """
    getCondVisibility(condition)--Returns True (1) or False (0) as a bool.

    condition : string - condition to check.

    List of Conditions -http://wiki.xbmc.org/?title=List_of_Boolean_Conditions

    *Note, You can combine two (or more) of the above settings by using "+" as an AND operator,
    "|" as an OR operator, "!" as a NOT operator, and "[" and "]" to bracket expressions.

    example:
    - visible = xbmc.getCondVisibility('[Control.IsVisible(41) + !Control.IsVisible(12)]')
    """
    return False


# noinspection PyPep8Naming,PyUnusedLocal
def getDVDState():
    """
    getDVDState()--Returns the dvd state as an integer.

    return values are:
     - 1 : xbmc.DRIVE_NOT_READY
     - 16 : xbmc.TRAY_OPEN
     - 64 : xbmc.TRAY_CLOSED_NO_MEDIA
     - 96 : xbmc.TRAY_CLOSED_MEDIA_PRESENT
    example:
     - dvdstate = xbmc.getDVDState()
     """
    return 0


# noinspection PyPep8Naming,PyUnusedLocal
def getFreeMem():
    """
    getFreeMem()--Returns the amount of free memory in MB as an integer.

    example:
     - freemem = xbmc.getFreeMem()
     """
    return 0


# noinspection PyPep8Naming,PyUnusedLocal
def getGlobalIdleTime():
    """
    getGlobalIdleTime()--Returns the elapsed idle time in seconds as an integer.

    example:
    - t = xbmc.getGlobalIdleTime()
    """
    return 0


# noinspection PyPep8Naming,PyUnusedLocal
def getIPAddress():
    """
    getIPAddress()--Returns the current ip address as a string.

    example:
    - ip = xbmc.getIPAddress()
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def getInfoImage(infotag):
    """
    getInfoImage(infotag)--Returns a filename including path to the InfoImage's thumbnail as a string.

    infotag : string - infotag for value you want returned.

    List of InfoTags -http://wiki.xbmc.org/?title=InfoLabels

    example:
    - filename = xbmc.getInfoImage('Weather.Conditions')
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def getInfoLabel(infotag):
    """
    getInfoLabel(infotag)--Returns an InfoLabel as a string.

    infotag : string - infoTag for value you want returned.

    List of InfoTags -http://wiki.xbmc.org/?title=InfoLabels

    example:
    - label = xbmc.getInfoLabel('Weather.Conditions')
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def getLanguage(format_, region=None):
    """
    getLanguage([format], [region])--Returns the active language as a string.

    format: [opt] format of the returned language string
    - xbmc.ISO_639_1: two letter code as defined in ISO 639-1
    - xbmc.ISO_639_2: three letter code as defined in ISO 639-2/T or ISO 639-2/B
    - xbmc.ENGLISH_NAME: full language name in English (default)


    region: [opt] append the region delimited by "-" of the language (setting) to the returned language string

    example:
    - language = xbmc.getLanguage(xbmc.ENGLISH_NAME)
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def getLocalizedString(id_):
    """
    getLocalizedString(id)--Returns a localized 'unicode string'.

    id : integer - id# for string you want to localize.

    *Note, See strings.po in language folders for which id
    you need for a string.

    example:
    - locstr = xbmc.getLocalizedString(6)
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def getRegion(id_):
    """
    getRegion(id)--Returns your regions setting as a string for the specified id.

    id : string - id of setting to return

    *Note, choices are (dateshort, datelong, time, meridiem, tempunit, speedunit)You can use the above as keywords for
    arguments.

    example:
    - date_long_format = xbmc.getRegion('datelong')
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def getSkinDir():
    """
    getSkinDir()--Returns the active skin directory as a string.

    *Note, This is not the full path like 'special://home/addons/MediaCenter', but only 'MediaCenter'.

    example:
    - skindir = xbmc.getSkinDir()
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def getSupportedMedia(media):
    """
    getSupportedMedia(media)--Returns the supported file types for the specific media as a string.

    media : string - media type

    *Note, media type can be (video, music, picture).The return value is a pipe separated string of filetypes
    (eg. '.mov|.avi').

    You can use the above as keywords for arguments.

    example:
    - mTypes = xbmc.getSupportedMedia('video')
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def log(msg, level=LOGNOTICE):
    """
    log(msg[, level])--Write a string to XBMC's log file and the debug window.
    msg : string - text to output.
    level : [opt] integer - log level to ouput at. (default=LOGNOTICE)

    *Note, You can use the above as keywords for arguments and skip certain optional arguments.
    Once you use a keyword, all following arguments require the keyword.

    Text is written to the log for the following conditions.
    XBMC loglevel == -1 (NONE, nothing at all is logged)
    XBMC loglevel == 0 (NORMAL, shows LOGNOTICE, LOGERROR, LOGSEVERE and LOGFATAL) * XBMC loglevel == 1(DEBUG,shows all)
    See pydocs for valid values for level.

    example:
    - xbmc.output(msg='This is a test string.', level=xbmc.LOGDEBUG));
    """
    pass


# noinspection PyPep8Naming,PyUnusedLocal
def makeLegalFilename(filename, fatX):
    """
    makeLegalFilename(filename[, fatX])--Returns a legal filename or path as a string.

    filename : string or unicode - filename/path to make legal
    fatX : [opt] bool - True=Xbox file system(Default)


    *Note, If fatX is true you should pass a full path. If fatX is false only pass the basename of the path.

    You can use the above as keywords for arguments and skip certain optional arguments.
    Once you use a keyword, all following arguments require the keyword.

    example:
    - filename = xbmc.makeLegalFilename('F: Age: The Meltdown.avi')
    """
    return ""


# noinspection PyPep8Naming,PyUnusedLocal
def playSFX(filename, useCached=False):
    """
    playSFX(filename,[useCached])--Plays a wav file by filename

    filename : string - filename of the wav file to play.
    useCached : [opt] bool - False = Dump any previously cached wav associated with filename

    example:
    - xbmc.playSFX('special://xbmc/scripts/dingdong.wav')

    - xbmc.playSFX('special://xbmc/scripts/dingdong.wav',False)
    """
    pass


# noinspection PyPep8Naming,PyUnusedLocal
def stopSFX():
    """
    stopSFX() -- Stops wav file

    example:
    - xbmc.stopSFX()
    """


# noinspection PyPep8Naming,PyUnusedLocal
def restart():
    """
    restart()--Restart the htpc. example:
    - xbmc.restart()
    """
    pass


# noinspection PyPep8Naming,PyUnusedLocal
def shutdown():
    """
    Shutdown()--Shutdown the htpc.

    example:
    - xbmc.shutdown()
    """
    pass


# noinspection PyPep8Naming,PyUnusedLocal
def skinHasImage(image):
    """
    skinHasImage(image)--Returns True if the image file exists in the skin.

    image : string - image filename

    *Note, If the media resides in a subfolder include it.
    (eg. home-myfiles\home-myfiles2.png)You can use the above as keywords for arguments.

    example:
    - exists = xbmc.skinHasImage('ButtonFocusedTexture.png')
    """
    return False


# noinspection PyPep8Naming,PyUnusedLocal
def sleep(time):
    """
    sleep(time)--Sleeps for 'time' msec.

    time : integer - number of msec to sleep.

    *Note, This is useful if you have for example aPlayer class that is waiting
    for onPlayBackEnded() calls.


    Throws: PyExc_TypeError, if time is not an integer.

    example:
    - xbmc.sleep(2000) # sleeps for 2 seconds
    """
    pass


# noinspection PyPep8Naming,PyUnusedLocal
def startServer(typ, bStart, bWait):
    """
    startServer(typ, bStart, bWait)--start or stop a server.

    typ : integer - use SERVER_* constants
    bStart : bool - start (True) or stop (False) a server
    bWait : [opt] bool - wait on stop before returning (not supported by all servers)
    returnValue : bool - True or False


    example:
    - xbmc.startServer(xbmc.SERVER_AIRPLAYSERVER, False)
    """
    pass


# noinspection PyPep8Naming,PyUnusedLocal
def validatePath(path):
    """
    validatePath(path)--Returns the validated path.

    path : string or unicode - Path to format

    *Note, Only useful if you are coding for both Linux and Windows for fixing slash problems.
    e.g. Corrects 'Z://something' -> 'Z:'

    example:
    - fpath = xbmc.validatePath(somepath)
    """
    return ""
