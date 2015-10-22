# -*- coding: utf-8 -*-

import os
from collections import namedtuple
from xbmcswift2 import xbmc, xbmcgui
from support.common import RESOURCES_PATH

Resolution = namedtuple('Resolution', 'width, height')


def get_skin_resolution():
    import xml.etree.ElementTree as ElementTree
    skin_path = xbmc.translatePath("special://skin/addon.xml")
    if not os.path.exists(skin_path):
        return Resolution(1280, 720)
    else:
        tree = ElementTree.parse(skin_path)
        res = tree.findall("./extension/res")[0]
        return Resolution(int(res.attrib["width"]), int(res.attrib["height"]))


SKIN_RESOLUTION = get_skin_resolution()


class Align:
    LEFT = 0
    TOP = 0
    RIGHT = 1
    CENTER_X = 2
    CENTER_Y = 4
    CENTER = 6
    TRUNCATED = 8
    JUSTIFY = 16
    BOTTOM = 32

    def __init__(self):
        pass


# noinspection PyPep8Naming
class Label(xbmcgui.ControlLabel):
    """ControlLabel class.

    Parameters:
    label: string or unicode - text string.
    font: string - font used for label text. (e.g. 'font13')
    textColor: hexstring - color of enabled label's label. (e.g. '0xFFFFFFFF')
    disabledColor: hexstring - color of disabled label's label. (e.g. '0xFFFF3300')
    alignment: integer - alignment of label - *Note, see xbfont.h
    hasPath: bool - True=stores a path / False=no path.
    angle: integer - angle of control. (+ rotates CCW, - rotates CW)"

    Note:
        After you create the control, you need to add it to the window with placeControl().

    Example:
        self.label = Label('Status', angle=45)
    """
    def __new__(cls, label, font=None, textColor=None, disabledColor=None,
                alignment=None, hasPath=None, angle=None, *args, **kwargs):
        if font is not None:
            kwargs['font'] = font
        if textColor is not None:
            kwargs['textColor'] = textColor
        if disabledColor is not None:
            kwargs['disabledColor'] = disabledColor
        if alignment is not None:
            kwargs['alignment'] = alignment
        # noinspection PyArgumentList
        return super(Label, cls).__new__(cls, -10, -10, 1, 1, label, *args, **kwargs)


# noinspection PyPep8Naming
class Image(xbmcgui.ControlImage):
    """ControlImage class.

    Parameters:
    filename: string - image filename.
    colorKey: hexString - (example, '0xFFFF3300')
    aspectRatio: integer - (values 0 = stretch (default), 1 = scale up (crops), 2 = scale down (black bars)
    colorDiffuse: hexString - (example, '0xC0FF0000' (red tint)).

    Note:
        After you create the control, you need to add it to the window with place_control().

    Example:
        self.image = Image('d:\images\picture.jpg', aspect_ratio=2)
    """
    def __new__(cls, filename, colorKey=None, aspectRatio=None, colorDiffuse=None, *args, **kwargs):
        if colorKey is not None:
            kwargs['colorKey'] = colorKey
        if aspectRatio is not None:
            kwargs['aspectRatio'] = aspectRatio
        if colorDiffuse is not None:
            kwargs['colorDiffuse'] = colorDiffuse
        # noinspection PyArgumentList
        return super(Image, cls).__new__(cls, -10, -10, 1, 1, filename, *args, **kwargs)


# noinspection PyPep8Naming
def positionControl(control, alignment=0, width=1, height=1, offsetX=0, offsetY=0, parent=None):
    if parent is None:
        parentX, parentY = 0, 0
        parentWidth, parentHeight = SKIN_RESOLUTION.width, SKIN_RESOLUTION.height
    else:
        parentX, parentY = parent.getX(), parent.getY()
        parentWidth, parentHeight = parent.getWidth(), parent.getHeight()

    screenWidth = int(width * parentWidth)
    screenHeight = int(height * parentHeight)
    x, y = offsetX, offsetY

    if alignment & Align.LEFT:
        pass
    elif alignment & Align.RIGHT:
        x = 1 - width - x
    elif alignment & Align.CENTER_X:
        x += 0.5 - width / 2.0

    if alignment & Align.TOP:
        pass
    elif alignment & Align.BOTTOM:
        y = 1 - height - y
    elif alignment & Align.CENTER_Y:
        y += 0.5 - height / 2.0

    screenX = parentX + int(x * parentWidth)
    screenY = parentY + int(y * parentHeight)

    control.setPosition(screenX, screenY)
    control.setWidth(screenWidth)
    control.setHeight(screenHeight)


# noinspection PyPep8Naming
class Window(xbmcgui.Window):
    def placeControl(self, control, alignment=0, width=1, height=1, offsetX=0, offsetY=0, parent=None):
        positionControl(control, alignment, width, height, offsetX, offsetY, parent)
        self.addControl(control)


# noinspection PyPep8Naming
class WindowDialog(xbmcgui.Window):
    def placeControl(self, control, alignment=0, width=1, height=1, offsetX=0, offsetY=0, parent=None):
        positionControl(control, alignment, width, height, offsetX, offsetY, parent)
        self.addControl(control)


# noinspection PyPep8Naming,PyAttributeOutsideInit
class InfoOverlay(Window):
    def __new__(cls, windowId=-1, alignment=0, width=1, height=1, offsetX=0, offsetY=0, backgroundColor="0x80000000"):
        self = super(InfoOverlay, cls).__new__(cls, windowId)
        self.controls = []
        self.background = Image(os.path.join(RESOURCES_PATH, "images", "black.png"))
        self.background.setColorDiffuse(backgroundColor)
        self.visible = False
        positionControl(self.background, alignment, width, height, offsetX, offsetY)
        self.controls.append(self.background)
        return self

    def addLabel(self, alignment=0, width=1, height=1, label="", offsetX=0, offsetY=0, font=None, textColor=None):
        label = Label(label, font, textColor, alignment=alignment)
        positionControl(label, alignment, width, height, offsetX, offsetY, self.background)
        self.controls.append(label)
        return label

    def show(self):
        if not self.visible:
            self.addControls(self.controls)
            self.visible = True

    def hide(self):
        if self.visible:
            self.removeControls(self.controls)
            self.visible = False
