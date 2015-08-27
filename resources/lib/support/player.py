# -*- coding: utf-8 -*-

from xbmcswift2 import xbmc
from support.abstract.player import AbstractPlayer
from support.common import plugin
from util.callbacks import Callbacks


class XbmcPlayer(AbstractPlayer):
    # noinspection PyPep8Naming
    class XbmcPlayerWithCallbacks(xbmc.Player, Callbacks):
        def __init__(self, *args, **kwargs):
            xbmc.Player.__init__(self, *args, **kwargs)
            self.duration = 0
            Callbacks.__init__(self)

        def onPlayBackStarted(self):
            self.duration = self.getTotalTime()
            self.run_callbacks('playback_started', duration=self.duration)

        def onPlayBackEnded(self):
            self.run_callbacks('playback_ended')

        def onPlayBackStopped(self):
            self.run_callbacks('playback_stopped')

        def onPlayBackPaused(self):
            self.run_callbacks('playback_paused')

        def onPlayBackResumed(self):
            self.run_callbacks('playback_resumed')

        def onPlayBackSeek(self, time, seekOffset):
            self.run_callbacks('playback_seek', time, seekOffset)

        def onPlayBackSeekChapter(self, chapter):
            self.run_callbacks('playback_seek_chapter', chapter)

        def onPlayBackSpeedChanged(self, speed):
            self.run_callbacks('playback_speed_changed', speed)

        def onQueueNextItem(self):
            self.run_callbacks('queue_next_item')

    def __init__(self):
        super(XbmcPlayer, self).__init__()
        self.player = self.XbmcPlayerWithCallbacks()
        self.time = 0

    def stop(self):
        self.player.stop()

    def pause(self):
        self.player.pause()

    def play(self, item=None, subtitles=None):
        if item is None:
            self.player.play()
        else:
            plugin.set_resolved_url(item, subtitles)

    def is_playing(self):
        return self.player.isPlaying()

    def run_callbacks(self, event, *args, **kwargs):
        self.player.run_callbacks(event, *args, **kwargs)

    def detach(self, event=None, callback=None):
        self.player.detach(event, callback)

    def attach(self, event, callback):
        self.player.attach(event, callback)

    def set_subtitles(self, path):
        self.player.setSubtitles(path)

    def get_total_time(self):
        return self.player.duration

    def get_time(self):
        try:
            self.time = self.player.getTime()
        except RuntimeError:
            pass
        return self.time
