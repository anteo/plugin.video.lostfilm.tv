# @package xbmcgui
# Classes and functions to work with XBMC GUI.
#


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ListItem(object):
    def __init__(self, label=None, label2=None, iconImage=None, thumbnailImage=None, path=None):
        """
        label: string or unicode - label1 text.
        label2: string or unicode - label2 text.
        iconImage: string - icon filename.
        thumbnailImage: string - thumbnail filename.
        path: string or unicode - listitem's path.

        Example:
        listitem = xbmcgui.ListItem('Casino Royale', '[PG-13]', 'blank-poster.tbn', 'poster.tbn',
        path='f:\\movies\\casino_royale.mov')
        """
        self.label = label
        self.label2 = label2
        self.iconImage = iconImage
        self.thumbnailImage = thumbnailImage
        self.path = path
        self.properties = {}
        self.stream_info = {}
        self.selected = False
        self.context_menu_items = []
        self.infolabels = {}

    def setSubtitles(self, subtitles=None):
        """
        setSubtitles() --Sets subtitles for this listitem.

        example:
        - listitem.setSubtitles(['special://temp/example.srt', 'http://example.com/example.srt' ])
        """
        pass

    def addContextMenuItems(self, items, replaceItems=False):
        """Adds item(s) to the context menu for media lists.

        items: list - [(label, action)] A list of tuples consisting of label and action pairs.
            label: string or unicode - item's label.
            action: string or unicode - any built-in function to perform.
        replaceItems: bool - True=only your items will show/False=your items will be added to context menu.

        List of functions: http://wiki.xbmc.org/?title=List_of_Built_In_Functions

        Example:
            listitem.addContextMenuItems([('Theater Showtimes',
            'XBMC.RunScript(special://home/scripts/showtimes/default.py,Iron Man)')])
        """
        self.context_menu_items = items

    def getLabel(self):
        """Returns the listitem label."""
        return self.label

    def getLabel2(self):
        """Returns the listitem's second label."""
        return self.label2

    def getProperty(self, key):
        """Returns a listitem property as a string, similar to an infolabel.

        key: string - property name.

        Note:
            Key is NOT case sensitive.
        """
        return self.properties[key.lower()]

    def isSelected(self):
        """Returns the listitem's selected status."""
        return self.selected

    def select(self, selected):
        """Sets the listitem's selected status.

        selected: bool - True=selected/False=not selected.
        """
        self.selected = selected

    def setIconImage(self, icon):
        """Sets the listitem's icon image.

        icon: string or unicode - image filename.
        """
        self.iconImage = icon

    def setInfo(self, type, infoLabels):
        """Sets the listitem's infoLabels.

        type: string - type of media(video/music/pictures).
        infoLabels: dictionary - pairs of { label: value }.

        Note:
            To set pictures exif info, prepend 'exif:' to the label. Exif values must be passed
            as strings, separate value pairs with a comma. (eg. {'exif:resolution': '720,480'}
            See CPictureInfoTag::TranslateString in PictureInfoTag.cpp for valid strings.

        General Values that apply to all types:
            count: integer (12) - can be used to store an id for later, or for sorting purposes
            size: long (1024) - size in bytes
            date: string (%d.%m.%Y / 01.01.2009) - file date

        Video Values:
            genre: string (Comedy)
            year: integer (2009)
            episode: integer (4)
            season: integer (1)
            top250: integer (192)
            tracknumber: integer (3)
            rating: float (6.4) - range is 0..10
            watched: depreciated - use playcount instead
            playcount: integer (2) - number of times this item has been played
            overlay: integer (2) - range is 0..8.  See GUIListItem.h for values
            cast: list (Michal C. Hall)
            castandrole: list (Michael C. Hall|Dexter)
            director: string (Dagur Kari)
            mpaa: string (PG-13)
            plot: string (Long Description)
            plotoutline: string (Short Description)
            title: string (Big Fan)
            originaltitle: string (Big Fan)
            duration: string - duration in minutes (95)
            studio: string (Warner Bros.)
            tagline: string (An awesome movie) - short description of movie
            writer: string (Robert D. Siegel)
            tvshowtitle: string (Heroes)
            premiered: string (2005-03-04)
            status: string (Continuing) - status of a TVshow
            code: string (tt0110293) - IMDb code
            aired: string (2008-12-07)
            credits: string (Andy Kaufman) - writing credits
            lastplayed: string (%Y-%m-%d %h:%m:%s = 2009-04-05 23:16:04)
            album: string (The Joshua Tree)
            votes: string (12345 votes)
            trailer: string (/home/user/trailer.avi)

        Music Values:
            tracknumber: integer (8)
            duration: integer (245) - duration in seconds
            year: integer (1998)
            genre: string (Rock)
            album: string (Pulse)
            artist: string (Muse)
            title: string (American Pie)
            rating: string (3) - single character between 0 and 5
            lyrics: string (On a dark desert highway...)
            playcount: integer (2) - number of times this item has been played
            lastplayed: string (%Y-%m-%d %h:%m:%s = 2009-04-05 23:16:04)

        Picture Values:
            title: string (In the last summer-1)
            picturepath: string (/home/username/pictures/img001.jpg)
            exif*: string (See CPictureInfoTag::TranslateString in PictureInfoTag.cpp for valid strings)

        Example:
            self.list.getSelectedItem().setInfo('video', { 'Genre': 'Comedy' })
        """
        assert type in ['video', 'music', 'pictures']
        self.infolabels.update(infoLabels)

    def setLabel(self, label):
        """Sets the listitem's label.

        label: string or unicode - text string.
        """
        self.label = label

    def setLabel2(self, label2):
        """Sets the listitem's second label.

        label2: string or unicode - text string.
        """
        self.label2 = label2

    def setPath(self, path):
        """
        setPath(path) -- Sets the listitem's path.
        path           : string or unicode - path, activated when item is clicked.
        *Note, You can use the above as keywords for arguments.

        example:
        - self.list.getSelectedItem().setPath(path='ActivateWindow(Weather)')
        """
        self.path = path

    def setProperty(self, key, value):
        """Sets a listitem property, similar to an infolabel.

        key: string - property name.
        value: string or unicode - value of property.

        Note:
            Key is NOT case sensitive.

        Some of these are treated internally by XBMC, such as the 'StartOffset' property, which is
        the offset in seconds at which to start playback of an item.  Others may be used in the skin
        to add extra information, such as 'WatchedCount' for tvshow items

        Example:
            self.list.getSelectedItem().setProperty('AspectRatio', '1.85 : 1')
            self.list.getSelectedItem().setProperty('StartOffset', '256.4')
        """
        self.properties[key.lower()] = value

    def addStreamInfo(self, stream_type, stream_values):
        """
        addStreamInfo(type, values) -- Add a stream with details.

        type              : string - type of stream(video/audio/subtitle).
        values            : dictionary - pairs of { label: value }.

        Video Values:
        codec         : string (h264)
        aspect        : float (1.78)
        width         : integer (1280)
        height        : integer (720)
        duration      : integer (seconds)

        Audio Values:
        codec         : string (dts)
        language      : string (en)
        channels      : integer (2)

        Subtitle Values:
        language      : string (en)

        example:
        - self.list.getSelectedItem().addStreamInfo('video', { 'Codec': 'h264', 'Width' : 1280 })
        """
        self.stream_info.update({stream_type: stream_values})

    def setThumbnailImage(self, thumb):
        """Sets the listitem's thumbnail image.

        thumb: string or unicode - image filename.
        """
        self.thumbnailImage = thumb


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class Window(object):
    """Create a new Window to draw on."""

    def __init__(self, windowId=-1):
        """
        Create a new Window to draw on.

        Specify an id to use an existing window.

        Raises:
        ValueError: If supplied window Id does not exist.
        Exception: If more then 200 windows are created.

        Deleting this window will activate the old window that was active
        and resets (not delete) all controls that are associated with this window.
        """
        pass

    def show(self):
        """Show this window.

        Shows this window by activating it, calling close() after it wil activate the current window again.

        Note:
            If your script ends this window will be closed to. To show it forever,
            make a loop at the end of your script and use doModal() instead.
        """
        pass

    def close(self):
        """Closes this window.

        Closes this window by activating the old window.
        The window is not deleted with this method.
        """
        pass

    def onAction(self, action):
        """onAction method.

        This method will recieve all actions that the main program will send to this window.
        By default, only the PREVIOUS_MENU action is handled.
        Overwrite this method to let your script handle all actions.
        Don't forget to capture ACTION_PREVIOUS_MENU, else the user can't close this window.
        """
        pass

    def onClick(self, control):
        """onClick method.

        This method will recieve all click events that the main program will send to this window.
        """
        pass

    def onDoubleClick(self):
        pass

    def onControl(self, control):
        """
        onControl method.
        This method will recieve all control events that the main program will send to this window.
        'control' is an instance of a Control object.
        """
        pass

    def onFocus(self, control):
        """onFocus method.

        This method will recieve all focus events that the main program will send to this window.
        """
        pass

    def onInit(self):
        """onInit method.

        This method will be called to initialize the window.
        """
        pass

    def doModal(self):
        """Display this window until close() is called."""
        pass

    def addControl(self, control):
        """Add a Control to this window.

        Raises:
            TypeError: If supplied argument is not a Control type.
            ReferenceError: If control is already used in another window.
            RuntimeError: Should not happen :-)

        The next controls can be added to a window atm:
            ControlLabel
            ControlFadeLabel
            ControlTextBox
            ControlButton
            ControlCheckMark
            ControlList
            ControlGroup
            ControlImage
            ControlRadioButton
            ControlProgress
        """
        pass

    def addControls(self, controls):
        """
        addControls(self, List)--Add a list of Controls to this window.

        *Throws:
        - TypeError, if supplied argument is not ofList type, or a control is not ofControl type
        - ReferenceError, if control is already used in another window
        - RuntimeError, should not happen :-)
        """
        pass

    def getControl(self, controlId):
        """Get's the control from this window.

        Raises:
            Exception: If Control doesn't exist

        controlId doesn't have to be a python control, it can be a control id
        from a xbmc window too (you can find id's in the xml files).

        Note:
            Not python controls are not completely usable yet.
            You can only use the Control functions.
        """
        return None

    def setFocus(self, control):
        """Give the supplied control focus.

        Raises:
            TypeError: If supplied argument is not a Control type.
            SystemError: On Internal error.
            RuntimeError: If control is not added to a window.
        """
        pass

    def setFocusId(self, int):
        """Gives the control with the supplied focus.

        Raises:
            SystemError: On Internal error.
            RuntimeError: If control is not added to a window.
        """
        pass

    def getFocus(self):
        """Returns the control which is focused.

        Raises:
            SystemError: On Internal error.
            RuntimeError: If no control has focus.
        """
        return None

    def getFocusId(self):
        """Returns the id of the control which is focused.

        Raises:
            SystemError: On Internal error.
            RuntimeError: If no control has focus.
        """
        return 0

    def removeControl(self, control):
        """Removes the control from this window.

        Raises:
            TypeError: If supplied argument is not a Control type.
            RuntimeError: If control is not added to this window.

        This will not delete the control. It is only removed from the window.
        """
        pass

    def removeControls(self, controls):
        pass

    def getHeight(self):
        """Returns the height of this screen."""
        return 0

    def getWidth(self):
        """Returns the width of this screen."""
        return 0

    def getResolution(self):
        """Returns the resolution of the screen.

        The returned value is one of the following:
            0 - 1080i      (1920x1080)
            1 - 720p       (1280x720)
            2 - 480p 4:3   (720x480)
            3 - 480p 16:9  (720x480)
            4 - NTSC 4:3   (720x480)
            5 - NTSC 16:9  (720x480)
            6 - PAL 4:3    (720x576)
            7 - PAL 16:9   (720x576)
            8 - PAL60 4:3  (720x480)
            9 - PAL60 16:9 (720x480)
        Note: this info is outdated. XBMC 12+ returns different vaulues.
        """
        return 0

    def setCoordinateResolution(self, resolution):
        """Sets the resolution that the coordinates of all controls are defined in.

        Allows XBMC to scale control positions and width/heights to whatever resolution
        XBMC is currently using.

        resolution is one of the following:
            0 - 1080i      (1920x1080)
            1 - 720p       (1280x720)
            2 - 480p 4:3   (720x480)
            3 - 480p 16:9  (720x480)
            4 - NTSC 4:3   (720x480)
            5 - NTSC 16:9  (720x480)
            6 - PAL 4:3    (720x576)
            7 - PAL 16:9   (720x576)
            8 - PAL60 4:3  (720x480)
            9 - PAL60 16:9 (720x480)

        Note: default is 720p (1280x720)
        Note 2: this is not an actual display resulution. This is the resolution of the coordinate grid
        all controls are placed on.
        """
        pass

    def setProperty(self, key, value):
        """Sets a window property, similar to an infolabel.

        key: string - property name.
        value: string or unicode - value of property.

        Note:
            key is NOT case sensitive. Setting value to an empty string is equivalent to clearProperty(key).

        Example:
            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            win.setProperty('Category', 'Newest')
        """
        pass

    def getProperty(self, key):
        """Returns a window property as a string, similar to an infolabel.

        key: string - property name.

        Note:
            key is NOT case sensitive.

        Example:
            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            category = win.getProperty('Category')
        """
        return ""

    def clearProperty(self, key):
        """Clears the specific window property.

        key: string - property name.

        Note:
            key is NOT case sensitive. Equivalent to setProperty(key,'').

        Example:
            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            win.clearProperty('Category')
        """
        pass

    def clearProperties(self):
        """Clears all window properties.

        Example:
            win = xbmcgui.Window(xbmcgui.getCurrentWindowId())
            win.clearProperties()
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming,PyMissingConstructor
class WindowDialog(Window):
    """
    Create a new WindowDialog with transparent background, unlike Window.
    WindowDialog always stays on top of XBMC UI.
    """

    def __init__(self):
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming,PyMissingConstructor
class WindowXML(Window):
    """Create a new WindowXML script."""

    def __init__(self, xmlFilename, scriptPath, defaultSkin='Default', defaultRes='720p'):
        """
        xmlFilename: string - the name of the xml file to look for.
        scriptPath: string - path to script. used to fallback to if the xml doesn't exist in the current skin.
        (eg os.getcwd())
        defaultSkin: string - name of the folder in the skins path to look in for the xml.
        defaultRes: string - default skins resolution.

        Note:
        Skin folder structure is eg(resources/skins/Default/720p).

        Example:
        ui = GUI('script-Lyrics-main.xml', os.getcwd(), 'LCARS', 'PAL')
        ui.doModal()
        del ui
        """
        pass

    def removeItem(self, position):
        """Removes a specified item based on position, from the Window List.

        position: integer - position of item to remove.
        """
        pass

    def addItem(self, item, position=32767):
        """Add a new item to this Window List.

        item: string, unicode or ListItem - item to add.
        position: integer - position of item to add. (NO Int = Adds to bottom,0 adds to top, 1 adds to one below from
                  top,-1 adds to one above from bottom etc etc)
                  If integer positions are greater than list size, negative positions will add to top of list, positive
                  positions will add to bottom of list.
        Example:
            self.addItem('Reboot XBMC', 0)
        """
        pass

    def clearList(self):
        """Clear the Window List."""
        pass

    def setCurrentListPosition(self, position):
        """Set the current position in the Window List.

        position: integer - position of item to set.
        """
        pass

    def getCurrentListPosition(self):
        """Gets the current position in the Window List."""
        return 0

    def getListItem(self, position):
        """Returns a given ListItem in this Window List.

        position: integer - position of item to return.
        """
        return ListItem()

    def getListSize(self):
        """Returns the number of items in this Window List."""
        return 0

    def setProperty(self, key, value):
        """Sets a container property, similar to an infolabel.

        key: string - property name.
        value: string or unicode - value of property.

        Note:
            Key is NOT case sensitive.

        Example:
            self.setProperty('Category', 'Newest')
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming,PyMissingConstructor
class WindowXMLDialog(WindowXML):
    """Create a new WindowXMLDialog script."""

    def __init__(self, xmlFilename, scriptPath, defaultSkin="Default", defaultRes="720p"):
        """
        xmlFilename: string - the name of the xml file to look for.
        scriptPath: string - path to script. used to fallback to if the xml doesn't exist in the current skin.
            (eg os.getcwd())
        defaultSkin: string - name of the folder in the skins path to look in for the xml.
        defaultRes: string - default skins resolution.

        Note:
        Skin folder structure is eg(resources/skins/Default/720p).

        Example:
        ui = GUI('script-Lyrics-main.xml', os.getcwd(), 'LCARS', 'PAL')
        ui.doModal()
        del ui
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming,PyMissingConstructor
class Control(object):
    """
    Parent for control classes. The problem here is that Python uses references to this class in a dynamic typing way.
    For example, you will find this type of python code frequently:
    window.getControl( 100 ).setLabel( "Stupid Dynamic Type")
    Notice that the 'getControl' call returns a 'Control ' object.
    In a dynamically typed language, the subsequent call to setLabel works if the specific type of control has the
    method.
    The script writer is often in a position to know more than the code about the specificControl type
    (in the example, that control id 100 is a 'ControlLabel ') where the C++ code is not.
    SWIG doesn't support this type of dynamic typing. The 'Control ' wrapper that's returned will wrap aControlLabel
    but will not have the 'setLabel' method on it. The only way to handle this is to add all possible subclass methods
    to the parent class. This is ugly but the alternative is nearly as ugly.
    It's particularly ugly here because the majority of the methods are unique to the particular subclass.
    If anyone thinks they have a solution then let me know. The alternative would be to have a set of 'getContol'
    methods, each one coresponding to a type so that the downcast can be done in the native code.
    IOW rather than a simple 'getControl' there would be a 'getControlLabel', 'getControlRadioButton',
    'getControlButton', etc.
    TODO:This later solution should be implemented for future scripting languages
    while the former will remain as deprecated functionality for Python.
    """

    def addItem(self):
        pass

    def addItems(self):
        pass

    def canAcceptMessages(self):
        pass

    def controlDown(self, control=None):
        """
        controlDown(control)--Set's the controls down navigation.
        control : control object - control to navigate to on down.
        *Note, You can also usesetNavigation() . Set to self to disable navigation.

        Throws:
         - TypeError, if one of the supplied arguments is not a control type.
         - ReferenceError, if one of the controls is not added to a window.
        example:
         - self.button.controlDown(self.button1)
        """
        pass

    def controlLeft(self, control=None):
        """
        controlLeft(control)--Set's the controls left navigation.

        control : control object - control to navigate to on left.

        *Note, You can also usesetNavigation() . Set to self to disable navigation.

        Throws:
        - TypeError, if one of the supplied arguments is not a control type.
        - ReferenceError, if one of the controls is not added to a window.


        example:
        - self.button.controlLeft(self.button1)
        """
        pass

    def controlRight(self, control=None):
        """
        controlRight(control)--Set's the controls right navigation.

        control : control object - control to navigate to on right.

        *Note, You can also usesetNavigation() . Set to self to disable navigation.

        Throws:
        - TypeError, if one of the supplied arguments is not a control type.
        - ReferenceError, if one of the controls is not added to a window.

        example:
        - self.button.controlRight(self.button1)
        """
        pass

    def controlUp(self, control=None):
        """
        controlUp(control)--Set's the controls up navigation.

        control : control object - control to navigate to on up.

        *Note, You can also usesetNavigation() . Set to self to disable navigation.

        Throws:
        - TypeError, if one of the supplied arguments is not a control type.
        - ReferenceError, if one of the controls is not added to a window.
        example:
         - self.button.controlUp(self.button1)
         """
        pass

    def getHeight(self):
        """
        getHeight() --Returns the control's current height as an integer.

        example:
        - height = self.button.getHeight()
        """
        return 0

    def getId(self):
        """
        getId() --Returns the control's current id as an integer.

        example:
        - id = self.button.getId()
        """
        return 0

    def getPosition(self):
        """
        getPosition() --Returns the control's current position as a x,y integer tuple.

        example:
        - pos = self.button.getPosition()
        """
        return 0, 0

    def getWidth(self):
        """
        getWidth() --Returns the control's current width as an integer.

        example:
        - width = self.button.getWidth()
        """
        return 0

    def getX(self):
        """
        Get X coordinate of a control as an integer.
        """
        return 0

    def getY(self):
        """
        Get Y coordinate of a control as an integer.
        """
        return 0

    def setAnimations(self, event_attr=None):
        """
        setAnimations([(event, attr,)*])--Set's the control's animations.

        [(event,attr,)*] : list - A list of tuples consisting of event and attributes pairs.
        - event : string - The event to animate.
        - attr : string - The whole attribute string separated by spaces.


        Animating your skin -http://wiki.xbmc.org/?title=Animating_Your_Skin

        example:
        - self.button.setAnimations([('focus', 'effect=zoom end=90,247,220,56 time=0',)])
        """
        pass

    def setEnableCondition(self, enable):
        """
        setEnableCondition(enable)--Set's the control's enabled condition.
        Allows XBMC to control the enabled status of the control.

        enable : string - Enable condition.

        List of Conditions -http://wiki.xbmc.org/index.php?title=List_of_Boolean_Conditions

        example:
        - self.button.setEnableCondition('System.InternetState')
        """
        pass

    def setEnabled(self, enabled=True):
        """
        setEnabled(enabled)--Set's the control's enabled/disabled state.

        enabled : bool - True=enabled / False=disabled.

        example:
        - self.button.setEnabled(False)
        """
        pass

    def setHeight(self, height):
        """
        setHeight(height)--Set's the controls height.

        height : integer - height of control.

        example:
        - self.image.setHeight(100)
        """
        pass

    def setNavigation(self, up=None, down=None, left=None, right=None):
        """
        setNavigation(up, down, left, right)--Set's the controls navigation.

        up : control object - control to navigate to on up.
        down : control object - control to navigate to on down.
        left : control object - control to navigate to on left.
        right : control object - control to navigate to on right.

        *Note, Same ascontrolUp() ,controlDown() ,controlLeft() ,controlRight() . Set to self to disable navigation for
        that direction.

        Throws:
        - TypeError, if one of the supplied arguments is not a control type.
        - ReferenceError, if one of the controls is not added to a window.


        example:
        - self.button.setNavigation(self.button1, self.button2, self.button3, self.button4)
        """
        pass

    def setPosition(self, x, y):
        """
        setPosition(x, y)--Set's the controls position.

        x : integer - x coordinate of control.
        y : integer - y coordinate of control.

        *Note, You may use negative integers. (e.g sliding a control into view)

        example:
        - self.button.setPosition(100, 250)
        """
        pass

    def setVisible(self, visible):
        """
        setVisible(visible)--Set's the control's visible/hidden state.

        visible : bool - True=visible / False=hidden.

        example:
        - self.button.setVisible(False)
        """
        pass

    def setVisibleCondition(self, condition, allowHiddenFocus=False):
        """
        setVisibleCondition(visible[,allowHiddenFocus])--Set's the control's visible condition.
        Allows XBMC to control the visible status of the control.

        visible : string - Visible condition.
        allowHiddenFocus : bool - True=gains focus even if hidden.

        List of Conditions -http://wiki.xbmc.org/index.php?title=List_of_Boolean_Conditions

        example:
        - self.button.setVisibleCondition('[Control.IsVisible(41) + !Control.IsVisible(12)]', True)
        """
        pass

    def setWidth(self, width):
        """
        setWidth(width)--Set's the controls width.

        width : integer - width of control.

        example:
        - self.image.setWidth(100)
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ControlLabel(Control):
    """
    ControlLabel class.
    Creates a text label.
    """

    def __init__(self, x, y, width, height, label, font=None, textColor=None, disabledColor=None, alignment=None,
                 hasPath=None, angle=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        label: string or unicode - text string.
        font: string - font used for label text. (e.g. 'font13')
        textColor: hexstring - color of enabled label's label. (e.g. '0xFFFFFFFF')
        disabledColor: hexstring - color of disabled label's label. (e.g. '0xFFFF3300')
        alignment: integer - alignment of label - *Note, see xbfont.h
        hasPath: bool - True=stores a path / False=no path.
        angle: integer - angle of control. (+ rotates CCW, - rotates CW)"

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
            self.label = xbmcgui.ControlLabel(100, 250, 125, 75, 'Status', angle=45)
        """
        pass

    def setLabel(self, label):
        """Set's text for this label.

        label: string or unicode - text string.
        """
        pass

    def getLabel(self):
        """Returns the text value for this label."""
        return ""


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ControlFadeLabel(Control):
    """Control which scrolls long label text."""

    def __init__(self, x, y, width, height, font=None, textColor=None, _alignment=None):
        """
         x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        font: string - font used for label text. (e.g. 'font13')
        textColor: hexstring - color of fadelabel's labels. (e.g. '0xFFFFFFFF')
        _alignment: integer - alignment of label - *Note, see xbfont.h

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
        self.fadelabel = xbmcgui.ControlFadeLabel(100, 250, 200, 50, textColor='0xFFFFFFFF')
        """
        pass

    def addLabel(self, label):
        """Add a label to this control for scrolling.

        label: string or unicode - text string.
        """
        pass

    def reset(self):
        """Clears this fadelabel."""
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ControlTextBox(Control):
    """
    ControlTextBox class.
    Creates a box for multi-line text.
    """

    def __init__(self, x, y, width, height, font=None, textColor=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        font: string - font used for text. (e.g. 'font13')
        textColor: hexstring - color of textbox's text. (e.g. '0xFFFFFFFF')

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
            self.textbox = xbmcgui.ControlTextBox(100, 250, 300, 300, textColor='0xFFFFFFFF')
        """
        pass

    def setText(self, text):
        """Set's the text for this textbox.

        text: string or unicode - text string.
        """
        pass

    def scroll(self, position):
        """Scrolls to the given position.

        id: integer - position to scroll to.
        """
        pass

    def reset(self):
        """Clear's this textbox."""
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ControlButton(Control):
    """
    ControlButton class.
    Creates a clickable button.
    """

    def __init__(self, x, y, width, height, label, focusTexture=None, noFocusTexture=None, textOffsetX=None,
                 textOffsetY=None, alignment=None, font=None, textColor=None, disabledColor=None, angle=None,
                 shadowColor=None, focusedColor=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        label: string or unicode - text string.
        focusTexture: string - filename for focus texture.
        noFocusTexture: string - filename for no focus texture.
        textOffsetX: integer - x offset of label.
        textOffsetY: integer - y offset of label.
        alignment: integer - alignment of label - *Note, see xbfont.h
        font: string - font used for label text. (e.g. 'font13')
        textColor: hexstring - color of enabled button's label. (e.g. '0xFFFFFFFF')
        disabledColor: hexstring - color of disabled button's label. (e.g. '0xFFFF3300')
        angle: integer - angle of control. (+ rotates CCW, - rotates CW)
        shadowColor: hexstring - color of button's label's shadow. (e.g. '0xFF000000')
        focusedColor: hexstring - color of focused button's label. (e.g. '0xFF00FFFF')

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
            self.button = xbmcgui.ControlButton(100, 250, 200, 50, 'Status', font='font14')
        """
        pass

    def setDisabledColor(self, disabledColor):
        """Set's this buttons disabled color.

        disabledColor: hexstring - color of disabled button's label. (e.g. '0xFFFF3300')
        """
        pass

    def setLabel(self, label=None, font=None, textColor=None, disabledColor=None, shadowColor=None, focusedColor=None):
        """Set's this buttons text attributes.

        label: string or unicode - text string.
        font: string - font used for label text. (e.g. 'font13')
        textColor: hexstring - color of enabled button's label. (e.g. '0xFFFFFFFF')
        disabledColor: hexstring - color of disabled button's label. (e.g. '0xFFFF3300')
        shadowColor: hexstring - color of button's label's shadow. (e.g. '0xFF000000')
        focusedColor: hexstring - color of focused button's label. (e.g. '0xFFFFFF00')
        label2: string or unicode - text string.

        Example:
            self.button.setLabel('Status', 'font14', '0xFFFFFFFF', '0xFFFF3300', '0xFF000000')
        """
        pass

    def getLabel(self):
        """Returns the buttons label as a unicode string."""
        return ""

    def getLabel2(self):
        """Returns the buttons label2 as a unicode string."""
        return ""


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ControlCheckMark(Control):
    """
    ControlCheckMark class.
    Creates a checkmark with 2 states.
    """

    def __init__(self, x, y, width, height, label, focusTexture=None, noFocusTexture=None, checkWidth=None,
                 checkHeight=None, _alignment=None, font=None, textColor=None, disabledColor=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        label: string or unicode - text string.

        focusTexture: string - filename for focus texture.
        noFocusTexture: string - filename for no focus texture.
        checkWidth: integer - width of checkmark.
        checkHeight: integer - height of checkmark.
        _alignment: integer - alignment of label - *Note, see xbfont.h
        font: string - font used for label text. (e.g. 'font13')
        textColor: hexstring - color of enabled checkmark's label. (e.g. '0xFFFFFFFF')
        disabledColor: hexstring - color of disabled checkmark's label. (e.g. '0xFFFF3300')

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
            self.checkmark = xbmcgui.ControlCheckMark(100, 250, 200, 50, 'Status', font='font14')
        """
        pass

    def setDisabledColor(self, disabledColor):
        """Set's this controls disabled color.

        disabledColor: hexstring - color of disabled checkmark's label. (e.g. '0xFFFF3300')
        """
        pass

    def setLabel(self, label, font=None, textColor=None, disabledColor=None):
        """Set's this controls text attributes.

        label: string or unicode - text string.
        font: string - font used for label text. (e.g. 'font13')
        textColor: hexstring - color of enabled checkmark's label. (e.g. '0xFFFFFFFF')
        disabledColor: hexstring - color of disabled checkmark's label. (e.g. '0xFFFF3300')

        Example:
            self.checkmark.setLabel('Status', 'font14', '0xFFFFFFFF', '0xFFFF3300')
        """
        pass

    def getSelected(self):
        """Returns the selected status for this checkmark as a bool."""
        return False

    def setSelected(self, isOn):
        """Sets this checkmark status to on or off.

        isOn: bool - True=selected (on) / False=not selected (off)
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming,PyMethodOverriding
class ControlList(Control):
    """
    ControlList class.
    Creates a list of items.
    """

    def __init__(self, x, y, width, height, font=None, textColor=None, buttonTexture=None, buttonFocusTexture=None,
                 selectedColor=None, _imageWidth=None, _imageHeight=None, _itemTextXOffset=None, _itemTextYOffset=None,
                 _itemHeight=None, _space=None, _alignmentY=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        font: string - font used for items label. (e.g. 'font13')
        textColor: hexstring - color of items label. (e.g. '0xFFFFFFFF')
        buttonTexture: string - filename for no focus texture.
        buttonFocusTexture: string - filename for focus texture.
        selectedColor: integer - x offset of label.
        _imageWidth: integer - width of items icon or thumbnail.
        _imageHeight: integer - height of items icon or thumbnail.
        _itemTextXOffset: integer - x offset of items label.
        _itemTextYOffset: integer - y offset of items label.
        _itemHeight: integer - height of items.
        _space: integer - space between items.
        _alignmentY: integer - Y-axis alignment of items label - *Note, see xbfont.h

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
            self.cList = xbmcgui.ControlList(100, 250, 200, 250, 'font14', space=5)
        """
        pass

    def addItem(self, item):
        """Add a new item to this list control.

        item: string, unicode or ListItem - item to add.
        """
        pass

    def addItems(self, items):
        """Adds a list of listitems or strings to this list control.

        items: List - list of strings, unicode objects or ListItems to add.
        """
        pass

    def selectItem(self, item):
        """Select an item by index number.

        item: integer - index number of the item to select.
        """
        pass

    def reset(self):
        """Clear all ListItems in this control list."""
        pass

    def getSpinControl(self):
        """Returns the associated ControlSpin object.

        Note:
            Not working completely yet -
            After adding this control list to a window it is not possible to change
            the settings of this spin control.
        """
        return None

    def setImageDimensions(self, imageWidth=None, imageHeight=None):
        """Sets the width/height of items icon or thumbnail.

        imageWidth: integer - width of items icon or thumbnail.
        imageHeight: integer - height of items icon or thumbnail.
        """
        pass

    def setItemHeight(self, itemHeight):
        """Sets the height of items.

        itemHeight: integer - height of items.
        """
        pass

    def setPageControlVisible(self, visible):
        """Sets the spin control's visible/hidden state.

        visible: boolean - True=visible / False=hidden.
        """
        pass

    def setSpace(self, space=None):
        """Set's the space between items.

        space: integer - space between items.
        """
        pass

    def getSelectedPosition(self):
        """Returns the position of the selected item as an integer.

        Note:
            Returns -1 for empty lists.
        """
        return 0

    def getSelectedItem(self):
        """Returns the selected item as a ListItem object.

        Note:
            Same as getSelectedPosition(), but instead of an integer a ListItem object is returned. Returns None for
            empty lists.
            See windowexample.py on how to use this.
        """
        return ListItem()

    def size(self):
        """Returns the total number of items in this list control as an integer."""
        return 0

    def getListItem(self, index):
        """Returns a given ListItem in this List.

        index: integer - index number of item to return.

        Raises:
            ValueError: If index is out of range.
        """
        return ListItem()

    def getItemHeight(self):
        """Returns the control's current item height as an integer."""
        return 0

    def getSpace(self):
        """Returns the control's space between items as an integer."""
        return 0

    def setStaticContent(self, items):
        """Fills a static list with a list of listitems.

        items: List - list of listitems to add.
        """
        pass

    def removeItem(self, index):
        """
        Remove an item by index number.
        index : integer - index number of the item to remove.
        example:
        my_list.removeItem(12)
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ControlImage(Control):
    """
    ControlImage class.
    Displays an image from a file.
    """

    def __init__(self, x, y, width, height, filename, colorKey=None, aspectRatio=None, colorDiffuse=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        filename: string - image filename.
        colorKey: hexString - (example, '0xFFFF3300')
        aspectRatio: integer - (values 0 = stretch (default), 1 = scale up (crops), 2 = scale down (black bars)
        colorDiffuse: hexString - (example, '0xC0FF0000' (red tint)).

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
            self.image = xbmcgui.ControlImage(100, 250, 125, 75, aspectRatio=2)
        """
        pass

    def setImage(self, filename):
        """Changes the image.

        filename: string - image filename.
        """
        pass

    def setColorDiffuse(self, colorDiffuse):
        """Changes the images color.

        colorDiffuse: hexString - (example, '0xC0FF0000' (red tint)).
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ControlProgress(Control):
    """
    ControlProgress class.
    """

    def __init__(self, x, y, width, height, texturebg=None, textureleft=None, texturemid=None, textureright=None,
                 textureoverlay=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        texturebg: string - image filename.
        textureleft: string - image filename.
        texturemid: string - image filename.
        textureright: string - image filename.
        textureoverlay: string - image filename.

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
            self.progress = xbmcgui.ControlProgress(100, 250, 125, 75)
        """
        pass

    def setPercent(self, percent):
        """Sets the percentage of the progressbar to show.

        percent: float - percentage of the bar to show.

        Note:
            Valid range for percent is 0-100.
        """
        pass

    def getPercent(self):
        """Returns a float of the percent of the progress."""
        return 0


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ControlSlider(Control):
    """
    ControlSlider class.
    Creates a slider.
    """

    def __init__(self, x, y, width, height, textureback=None, texture=None, texturefocus=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        textureback: string - image filename.
        texture: string - image filename.
        texturefocus: string - image filename.

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
            self.slider = xbmcgui.ControlSlider(100, 250, 350, 40)
        """
        pass

    def getPercent(self):
        """Returns a float of the percent of the slider."""
        return float

    def setPercent(self, percent):
        """Sets the percent of the slider."""
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ControlGroup(Control):
    """ControlGroup class."""

    def __init__(self, x, y, width, height):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.

        Example:
        self.group = xbmcgui.ControlGroup(100, 250, 125, 75)
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ControlEdit(Control):
    """
    ControlEdit class.
    ControlEdit(x, y, width, height, label[, font, textColor,
                                                    disabledColor, alignment, focusTexture, noFocusTexture])
    """

    def __init__(self, x, y, width, height, label, font=None, textColor=None, disabledColor=None, alignment=None,
                 focusTexture=None, noFocusTexture=None):
        """
        x              : integer - x coordinate of control.
        y              : integer - y coordinate of control.
        width          : integer - width of control.
        height         : integer - height of control.
        label          : string or unicode - text string.
        font           : [opt] string - font used for label text. (e.g. 'font13')
        textColor      : [opt] hexstring - color of enabled label's label. (e.g. '0xFFFFFFFF')
        disabledColor  : [opt] hexstring - color of disabled label's label. (e.g. '0xFFFF3300')
        _alignment      : [opt] integer - alignment of label - *Note, see xbfont.h
        focusTexture   : [opt] string - filename for focus texture.
        noFocusTexture : [opt] string - filename for no focus texture.
        isPassword     : [opt] bool - if true, mask text value.

        *Note, You can use the above as keywords for arguments and skip certain optional arguments.
        Once you use a keyword, all following arguments require the keyword.
        After you create the control, you need to add it to the window with addControl().

        example:
        - self.edit = xbmcgui.ControlEdit(100, 250, 125, 75, 'Status')
        """
        pass

    def getLabel(self):
        """
        getLabel() -- Returns the text heading for this edit control.

        example:
        - label = self.edit.getLabel()
        """
        return ""

    def getText(self):
        """
        getText() -- Returns the text value for this edit control.

        example:
        - value = self.edit.getText()
        """
        return ""

    def setLabel(self, label):
        """
        setLabel(label) -- Set's text heading for this edit control.

        label          : string or unicode - text string.
        example:
        - self.edit.setLabel('Status')
        """
        pass

    def setText(self, value):
        """
        setText(value) -- Set's text value for this edit control.

        value          : string or unicode - text string.
        example:
        - self.edit.setText('online')
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class ControlRadioButton(Control):
    """
    ControlRadioButton class.
    Creates a radio-button with 2 states.
    """

    def __init__(self, x, y, width, height, label, focusTexture=None, noFocusTexture=None, textOffsetX=None,
                 textOffsetY=None, _alignment=None, font=None, textColor=None, disabledColor=None, angle=None,
                 shadowColor=None, focusedColor=None, focusOnTexture=None, noFocusOnTexture=None,
                 focusOffTexture=None, noFocusOffTexture=None):
        """
        x: integer - x coordinate of control.
        y: integer - y coordinate of control.
        width: integer - width of control.
        height: integer - height of control.
        label: string or unicode - text string.
        focusTexture: string - filename for focus texture.
        noFocusTexture: string - filename for no focus texture.
        textOffsetX: integer - x offset of label.
        textOffsetY: integer - y offset of label.
        _alignment: integer - alignment of label - *Note, see xbfont.h
        font: string - font used for label text. (e.g. 'font13')
        textColor: hexstring - color of enabled radio button's label. (e.g. '0xFFFFFFFF')
        disabledColor: hexstring - color of disabled radio button's label. (e.g. '0xFFFF3300')
        angle: integer - angle of control. (+ rotates CCW, - rotates CW)
        shadowColor: hexstring - color of radio button's label's shadow. (e.g. '0xFF000000')
        focusedColor: hexstring - color of focused radio button's label. (e.g. '0xFF00FFFF')
        focusOnTexture: string - filename for radio focused/checked texture.
        noFocusOnTexture: string - filename for radio not focused/checked texture.
        focusOffTexture: string - filename for radio focused/unchecked texture.
        noFocusOffTexture: string - filename for radio not focused/unchecked texture.
        Note: To customize RadioButton all 4 abovementioned textures need to be provided.
        focus and noFocus textures can be the same.

        Note:
            After you create the control, you need to add it to the window with addControl().

        Example:
            self.radiobutton = xbmcgui.ControlRadioButton(100, 250, 200, 50, 'Status', font='font14')
        """
        pass

    def setSelected(self, selected):
        """Sets the radio buttons's selected status.

        selected: bool - True=selected (on) / False=not selected (off)
        """
        pass

    def isSelected(self):
        """Returns the radio buttons's selected status."""
        return False

    def setLabel(self, label, font=None, textColor=None, disabledColor=None, shadowColor=None, focusedColor=None):
        """Set's the radio buttons text attributes.

        label: string or unicode - text string.
        font: string - font used for label text. (e.g. 'font13')
        textColor: hexstring - color of enabled radio button's label. (e.g. '0xFFFFFFFF')
        disabledColor: hexstring - color of disabled radio button's label. (e.g. '0xFFFF3300')
        shadowColor: hexstring - color of radio button's label's shadow. (e.g. '0xFF000000')
        focusedColor: hexstring - color of focused radio button's label. (e.g. '0xFFFFFF00')

        Example:
            self.radiobutton.setLabel('Status', 'font14', '0xFFFFFFFF', '0xFFFF3300', '0xFF000000')
        """
        pass

    def setRadioDimension(self, x, y, width, height):
        """Sets the radio buttons's radio texture's position and size.

        x: integer - x coordinate of radio texture.
        y: integer - y coordinate of radio texture.
        width: integer - width of radio texture.
        height: integer - height of radio texture.

        Example:
            self.radiobutton.setRadioDimension(x=100, y=5, width=20, height=20)
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class Dialog(object):
    def browse(self, type, heading, s_shares, mask=None, useThumbs=False, treatAsFolder=False, default=None,
               enableMultiple=False):
        """Show a 'Browse' dialog.

        type: integer - the type of browse dialog.
        heading: string or unicode - dialog heading.
        s_shares: string or unicode - from sources.xml. (i.e. 'myprograms')
        mask: string or unicode - '|' separated file mask. (i.e. '.jpg|.png')
        useThumbs: boolean - if True autoswitch to Thumb view if files exist.
        treatAsFolder: boolean - if True playlists and archives act as folders.
        default: string - default path or file.
        enableMultiple: boolean - if True multiple file selection is enabled.

        Types:
            0: ShowAndGetDirectory
            1: ShowAndGetFile
            2: ShowAndGetImage
            3: ShowAndGetWriteableDirectory

        Note:
            If enableMultiple is False (default): returns filename and/or path as a string
            to the location of the highlighted item, if user pressed 'Ok' or a masked item
            was selected. Returns the default value if dialog was canceled.
            If enableMultiple is True: returns tuple of marked filenames as a string,
            if user pressed 'Ok' or a masked item was selected. Returns empty tuple if dialog was canceled.

            If type is 0 or 3 the enableMultiple parameter is ignored.

        Example:
            dialog = xbmcgui.Dialog()
            fn = dialog.browse(3, 'XBMC', 'files', '', False, False, False,
                'special://masterprofile/script_data/XBMC Lyrics')
        """
        return str

    def browseMultiple(self, type, heading, shares, mask=None, useThumbs=None, treatAsFolder=None, default=None):
        """
        browse(type, heading, shares[, mask, useThumbs, treatAsFolder, default])--Show a 'Browse' dialog.

        type : integer - the type of browse dialog.
        heading : string or unicode - dialog heading.
        shares : string or unicode - from sources.xml. (i.e. 'myprograms')
        mask : [opt] string or unicode - '|' separated file mask. (i.e. '.jpg|.png')
        useThumbs : [opt] boolean - if True autoswitch to Thumb view if files exist (default=false).
        treatAsFolder : [opt] boolean - if True playlists and archives act as folders (default=false).
        default : [opt] string - default path or file.

        Types:
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage


        *Note,
        returns tuple of marked filenames as a string,"
        if user pressed 'Ok' or a masked item was selected. Returns empty tuple if dialog was canceled.

        example:

        - dialog = xbmcgui.Dialog()
        - fn = dialog.browseMultiple(2, 'XBMC', 'files', '', False, False,
            'special://masterprofile/script_data/XBMC Lyrics')
        """
        return ()

    def browseSingle(self, type, heading, shares, mask=None, useThumbs=None, treatAsFolder=None, default=None):
        """
        browse(type, heading, shares[, mask, useThumbs, treatAsFolder, default])--Show a 'Browse' dialog.

        type : integer - the type of browse dialog.
        heading : string or unicode - dialog heading.
        shares : string or unicode - from sources.xml. (i.e. 'myprograms')
        mask : [opt] string or unicode - '|' separated file mask. (i.e. '.jpg|.png')
        useThumbs : [opt] boolean - if True autoswitch to Thumb view if files exist (default=false).
        treatAsFolder : [opt] boolean - if True playlists and archives act as folders (default=false).
        default : [opt] string - default path or file.

        Types:

        - 0 : ShowAndGetDirectory
        - 1 : ShowAndGetFile
        - 2 : ShowAndGetImage
        - 3 : ShowAndGetWriteableDirectory
        *Note, Returns filename and/or path as a string to the location of the highlighted item,
        if user pressed 'Ok' or a masked item was selected.
        Returns the default value if dialog was canceled.

        example:

        - dialog = xbmcgui.Dialog()
        - fn = dialog.browse(3, 'XBMC', 'files', '', False, False, 'special://masterprofile/script_data/XBMC Lyrics')
        """
        return ""

    def input(self, heading, default=None, type=None, option=None, autoclose=None):
        """
        input(heading[, default, type, option, autoclose])--Show an Input dialog.

        heading : string - dialog heading.
        default : [opt] string - default value. (default=empty string)
        type : [opt] integer - the type of keyboard dialog. (default=xbmcgui.INPUT_ALPHANUM)
        option : [opt] integer - option for the dialog. (see Options below)
        autoclose : [opt] integer - milliseconds to autoclose dialog. (default=do not autoclose)

        Types:
        - xbmcgui.INPUT_ALPHANUM (standard keyboard)
        - xbmcgui.INPUT_NUMERIC (format: #)
        - xbmcgui.INPUT_DATE (format: DD/MM/YYYY)
        - xbmcgui.INPUT_TIME (format: HH:MM)
        - xbmcgui.INPUT_IPADDRESS (format: #.#.#.#)
        - xbmcgui.INPUT_PASSWORD (return md5 hash of input, input is masked)


        Options PasswordDialog :

        - xbmcgui.PASSWORD_VERIFY (verifies an existing (default) md5 hashed password)
        Options AlphanumDialog :

        - xbmcgui.ALPHANUM_HIDE_INPUT (masks input)
        *Note, Returns the entered data as a string.
        Returns an empty string if dialog was canceled.

        Note:
            available since Gotham

        Example:
        - dialog = xbmcgui.Dialog()
        - d = dialog.input('Enter secret code', type=xbmcgui.INPUT_ALPHANUM, option=xbmcgui.ALPHANUM_HIDE_INPUT)
        """
        return ""

    def numeric(self, type, heading, default=None):
        """Show a 'Numeric' dialog.

        type: integer - the type of numeric dialog.
        heading: string or unicode - dialog heading.
        default: string - default value.

        Types:
            0: ShowAndGetNumber    (default format: #)
            1: ShowAndGetDate      (default format: DD/MM/YYYY)
            2: ShowAndGetTime      (default format: HH:MM)
            3: ShowAndGetIPAddress (default format: #.#.#.#)

        Note:
            Returns the entered data as a string.
            Returns the default value if dialog was canceled.

        Example:
            dialog = xbmcgui.Dialog()
            d = dialog.numeric(1, 'Enter date of birth')
        """
        return ""

    def notification(self, heading, message, icon=None, time=None, sound=None):
        """
        notification(heading, message[, icon, time, sound])--Show a Notification alert.

        heading : string - dialog heading.
        message : string - dialog message.
        icon : [opt] string - icon to use. (default xbmcgui.NOTIFICATION_INFO)
        time : [opt] integer - time in milliseconds (default 5000)
        sound : [opt] bool - play notification sound (default True)

        Builtin Icons:

        - xbmcgui.NOTIFICATION_INFO
        - xbmcgui.NOTIFICATION_WARNING
        - xbmcgui.NOTIFICATION_ERROR
        example:
        - dialog = xbmcgui.Dialog()
        - dialog.notification('Movie Trailers', 'Finding Nemo download finished.', xbmcgui.NOTIFICATION_INFO, 5000)
        """
        pass

    def yesno(self, heading, line1, line2=None, line3=None, nolabel=None, yeslabel=None):
        """Show a dialog 'YES/NO'.

        heading: string or unicode - dialog heading.
        line1: string or unicode - line #1 text.
        line2: string or unicode - line #2 text.
        line3: string or unicode - line #3 text.
        nolabel: label to put on the no button.
        yeslabel: label to put on the yes button.

        Note:
            Returns True if 'Yes' was pressed, else False.

        Example:
            dialog = xbmcgui.Dialog()
            ret = dialog.yesno('XBMC', 'Do you want to exit this script?')
        """
        return False

    def ok(self, heading, line1, line2=None, line3=None):
        """Show a dialog 'OK'.

        heading: string or unicode - dialog heading.
        line1: string or unicode - line #1 text.
        line2: string or unicode - line #2 text.
        line3: string or unicode - line #3 text.

        Note:
            Returns True if 'Ok' was pressed, else False.

        Example:
            dialog = xbmcgui.Dialog()
            ok = dialog.ok('XBMC', 'There was an error.')
        """
        return False

    def select(self, heading, list, autoclose=0):
        """Show a select dialog.

        heading: string or unicode - dialog heading.
        list: string list - list of items.
        autoclose: integer - milliseconds to autoclose dialog.

        Note:
            autoclose = 0 - This disables autoclose.
            Returns the position of the highlighted item as an integer.

        Example:
            dialog = xbmcgui.Dialog()
            ret = dialog.select('Choose a playlist', ['Playlist #1', 'Playlist #2, 'Playlist #3'])
        """
        return 0


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class DialogProgress(object):
    def create(self, heading, line1=None, line2=None, line3=None):
        """Create and show a progress dialog.

        heading: string or unicode - dialog heading.
        line1: string or unicode - line #1 text.
        line2: string or unicode - line #2 text.
        line3: string or unicode - line #3 text.

        Note:
            Use update() to update lines and progressbar.

        Example:
            pDialog = xbmcgui.DialogProgress()
            ret = pDialog.create('XBMC', 'Initializing script...')
        """
        pass

    def update(self, percent, line1=None, line2=None, line3=None):
        """Update's the progress dialog.

        percent: integer - percent complete. (0:100)
        line1: string or unicode - line #1 text.
        line2: string or unicode - line #2 text.
        line3: string or unicode - line #3 text.

        Note:
            If percent == 0, the progressbar will be hidden.

        Example:
            pDialog.update(25, 'Importing modules...')
        """
        pass

    def iscanceled(self):
        """Returns True if the user pressed cancel."""
        return False

    def close(self):
        """Close the progress dialog."""
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class DialogProgressBG(object):
    """
    DialogProgressBG class
    Displays a small progress dialog in the corner of the screen.
    """

    def close(self):
        """
        close() --Close the background progress dialog

        example:
        - pDialog.close()
        """
        pass

    def create(self, heading, message=''):
        """
        create(heading[, message])--Create and show a background progress dialog.n

        heading : string or unicode - dialog headingn
        message : [opt] string or unicode - message textn

        *Note, 'heading' is used for the dialog's id. Use a unique heading.n
        Useupdate() to update heading, message and progressbar.n

        example:
        - pDialog = xbmcgui.DialogProgressBG()
        - pDialog.create('Movie Trailers', 'Downloading Monsters Inc. ...')
        """
        pass

    def isFinished(self):
        """
        isFinished() --Returns True if the background dialog is active.

        example:
        - if (pDialog.isFinished()): break
        """
        return False

    def update(self, percent, heading=None, message=None):
        """
        update([percent, heading, message])--Updates the background progress dialog.

        percent : [opt] integer - percent complete. (0:100)
        heading : [opt] string or unicode - dialog heading
        message : [opt] string or unicode - message text

        *Note, To clear heading or message, you must pass a blank character.

        example:
        - pDialog.update(25, message='Downloading Finding Nemo ...')
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class Action(object):
    """Action class.

    For backwards compatibility reasons the == operator is extended so that it
    can compare an action with other actions and action.GetID() with numbers.

    Example:
        (action == ACTION_MOVE_LEFT)
    """

    def getId(self):
        """Returns the action's current id as a long or 0 if no action is mapped in the xml's."""
        return 0

    def getButtonCode(self):
        """Returns the button code for this action."""
        return 0

    def getAmount1(self):
        """Returns the first amount of force applied to the thumbstick."""
        return 0.0

    def getAmount2(self):
        """Returns the second amount of force applied to the thumbstick."""
        return 0.0


def lock():
    """
    lock()--Lock the gui until xbmcgui.unlock() is called.

    *Note, This will improve performance when doing a lot of gui manipulation at once.
    The main program (xbmc itself) will freeze until xbmcgui.unlock() is called.

    example:
    - xbmcgui.lock()
    """
    pass


def unlock():
    """
    unlock()--Unlock the gui from a lock() call.

    example:
    - xbmcgui.unlock()
    """
    pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
def getCurrentWindowId():
    """
    getCurrentWindowId()--Returns the id for the current 'active' window as an integer.

    example:
    - wid = xbmcgui.getCurrentWindowId()
    """
    return long


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
def getCurrentWindowDialogId():
    """
    getCurrentWindowDialogId()--Returns the id for the current 'active' dialog as an integer.

    example:
    - wid = xbmcgui.getCurrentWindowDialogId()
    """
    return long


ALPHANUM_HIDE_INPUT = 2
CONTROL_TEXT_OFFSET_X = 10
CONTROL_TEXT_OFFSET_Y = 2
ICON_OVERLAY_HAS_TRAINER = 4
ICON_OVERLAY_HD = 8
ICON_OVERLAY_LOCKED = 3
ICON_OVERLAY_NONE = 0
ICON_OVERLAY_RAR = 1
ICON_OVERLAY_TRAINED = 5
ICON_OVERLAY_UNWATCHED = 6
ICON_OVERLAY_WATCHED = 7
ICON_OVERLAY_ZIP = 2
INPUT_ALPHANUM = 0
INPUT_DATE = 2
INPUT_IPADDRESS = 4
INPUT_NUMERIC = 1
INPUT_PASSWORD = 5
INPUT_TIME = 3
NOTIFICATION_ERROR = 'error'
NOTIFICATION_INFO = 'info'
NOTIFICATION_WARNING = 'warning'
PASSWORD_VERIFY = 1

__author__ = 'Team XBMC <http://xbmc.org>'
__credits__ = 'Team XBMC'
__date__ = 'Sun Aug 18 16:43:27 CEST 2013'
__platform__ = 'ALL'
__version__ = '2.0'
