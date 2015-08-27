# -*- coding: utf-8 -*-
from support.abstract.progress import AbstractTorrentTransferProgress, AbstractProgress, AbstractFileTransferProgress
from support.common import lang
from support.gui import InfoOverlay, Align
from support.torrent import TorrentStatus
from xbmcswift2 import xbmcgui, xbmc


class XbmcProgress(AbstractProgress):
    def __init__(self, heading):
        AbstractProgress.__init__(self)
        self.dialog = xbmcgui.DialogProgress()
        self.opened = False
        self.heading = heading
        xbmc.sleep(500)

    def open(self):
        if not self.opened:
            self.dialog.create(self.heading)
            self.opened = True

    def close(self):
        if self.opened:
            self.dialog.close()
            self.opened = False

    def is_cancelled(self):
        return self.opened and self.dialog.iscanceled()

    def update(self, percent, *lines):
        self.dialog.update(percent, *lines)


class XbmcFileTransferProgress(AbstractFileTransferProgress):
    def __init__(self, name=None, size=-1, heading=None):
        AbstractFileTransferProgress.__init__(self, name, size)
        self.heading = heading or lang(33000)
        self.handler = XbmcProgress(heading)

    def open(self):
        self.handler.open()

    def close(self):
        self.handler.close()

    def is_cancelled(self):
        return self.handler.is_cancelled()

    def update(self, percent):
        lines = []
        if self.name:
            lines.append(lang(33001) % {'name': self.name})
        size = self._human_size(self.size) if self.size >= 0 else lang(33003)
        lines.append(lang(33002) % ({'transferred': self._human_size(self._transferred_bytes),
                                     'total': size}))
        return self.handler.update(percent, *lines)


class XbmcTorrentTransferProgress(AbstractTorrentTransferProgress):
    def __init__(self, name=None, size=-1, heading=None):
        AbstractTorrentTransferProgress.__init__(self, name, size)
        heading = heading or lang(33010)
        self.handler = XbmcProgress(heading)

    def open(self):
        self.handler.open()

    def close(self):
        self.handler.close()

    def is_cancelled(self):
        return self.handler.is_cancelled()

    def update(self, percent):
        lines = []
        if self.name is not None:
            lines.append(lang(33011) % {'name': self.name})
        if self.state in [TorrentStatus.DOWNLOADING, TorrentStatus.SEEDING,
                          TorrentStatus.CHECKING, TorrentStatus.PREBUFFERING]:
            size = self._human_size(self.size) if self.size >= 0 else lang(33015)
            lines.append(lang(33013) % {'transferred': self._human_size(self._transferred_bytes),
                                        'total': size,
                                        'state': self.state.localized})
            if self.state != TorrentStatus.CHECKING:
                lines.append(lang(33014) % {'download_rate': self._human_rate(self.download_rate),
                                            'upload_rate': self._human_rate(self.upload_rate),
                                            'peers': self.peers,
                                            'seeds': self.seeds})
        else:
            lines.append(lang(33012) % {'state': self.state.localized})
        return self.handler.update(percent, *lines)


class XbmcOverlayTorrentTransferProgress(AbstractTorrentTransferProgress):
    def __init__(self, name=None, size=-1, overlay=None, window_id=-1):
        """
        :type overlay: InfoOverlay
        """
        AbstractTorrentTransferProgress.__init__(self, name, size)
        self.overlay = overlay or InfoOverlay(window_id, Align.CENTER, 0.8, 0.3)
        self.heading = self.overlay.addLabel(Align.CENTER_X, offsetY=0.05, font="font16")
        self.title = self.overlay.addLabel(Align.CENTER_X, offsetY=0.3, font="font30_title", label=name)
        self.label = self.overlay.addLabel(Align.BOTTOM | Align.CENTER_X, height=0.4)

    def open(self):
        self.overlay.show()

    def close(self):
        self.overlay.hide()

    def is_cancelled(self):
        return False

    def update(self, percent):
        if not self.overlay.visible:
            return
        heading = "%s - %d%%" % (self.state.localized, percent)
        self.heading.setLabel(heading)
        self.title.setLabel(self.name)
        lines = []
        if self.state in [TorrentStatus.DOWNLOADING, TorrentStatus.CHECKING,
                          TorrentStatus.SEEDING, TorrentStatus.PREBUFFERING]:
            size = self._human_size(self.size) if self.size >= 0 else lang(33015)
            lines.append(lang(33016) % {'transferred': self._human_size(self._transferred_bytes),
                                        'total': size})
            if self.state != TorrentStatus.CHECKING:
                lines.append(lang(33014) % {'download_rate': self._human_rate(self.download_rate),
                                            'upload_rate': self._human_rate(self.upload_rate),
                                            'peers': self.peers,
                                            'seeds': self.seeds})
        self.label.setLabel("\n".join(lines))
