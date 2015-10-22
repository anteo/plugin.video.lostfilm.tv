# -*- coding: utf-8 -*-

import logging
import time

from util.callbacks import Callbacks


class AbstractPlayer(Callbacks):
    PLAYBACK_STARTED = 'playback_started'
    PLAYBACK_ENDED = 'playback_ended'
    PLAYBACK_STOPPED = 'playback_stopped'
    PLAYBACK_PAUSED = 'playback_paused'
    PLAYBACK_RESUMED = 'playback_resumed'
    PLAYBACK_SEEK = 'playback_seek'
    PLAYBACK_SEEK_CHAPTER = 'playback_seek_chapter'
    PLAYBACK_SPEED_CHANGED = 'playback_speed_changed'
    QUEUE_NEXT_ITEM = 'queue_next_item'

    def play(self, item=None, subtitles=None):
        """
        :type item: dict
        """
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def pause(self):
        raise NotImplementedError

    def is_playing(self):
        raise NotImplementedError

    def get_time(self):
        raise NotImplementedError

    def get_total_time(self):
        raise NotImplementedError

    def set_subtitles(self, path):
        raise NotImplementedError

    def get_percent(self):
        if self.get_total_time():
            return float(self.get_time()) / float(self.get_total_time()) * 100
        else:
            return 0


class DummyPlayer(AbstractPlayer):
    def set_subtitles(self, path):
        pass

    def get_total_time(self):
        return self.play_duration

    def get_time(self):
        return time.time() - self.start_time

    def is_playing(self):
        if self.playing and not self.paused:
            if time.time() - self.start_time >= self.play_duration:
                self.stop()
        return self.playing

    def pause(self):
        if not self.paused and self.playing:
            self.log.info("Pausing playback...")
            self.run_callbacks(self.PLAYBACK_PAUSED)
            self.paused = True

    def play(self, item=None, subtitles=None):
        """
        :type item: ListItem
        """
        if item is None and self.playing:
            if self.paused:
                self.log.info("Resuming playback...")
                self.run_callbacks(self.PLAYBACK_RESUMED)
                self.paused = False
        elif not self.playing:
            self.log.info("Starting playback...")
            self.start_time = time.time()
            self.run_callbacks(self.PLAYBACK_STARTED)
            self.playing = True

    def stop(self):
        if self.playing:
            self.log.info("Stopping playback...")
            self.playing = False
            self.run_callbacks(self.PLAYBACK_STOPPED)

    def log_events(self, event):
        self.log.info("Player event: %s", event)

    def __init__(self, play_duration, log=None):
        super(DummyPlayer, self).__init__()
        self.log = log or logging.getLogger(__name__)
        self.playing = False
        self.start_time = None
        self.paused = False
        self.play_duration = play_duration
