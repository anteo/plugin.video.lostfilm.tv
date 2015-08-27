# -*- coding: utf-8 -*-

import gc
import timeit
import logging


class Timer:
    def __init__(self, timer=None, disable_gc=False, logger=None, log_level=logging.INFO, name="Total time"):
        if timer is None:
            timer = timeit.default_timer
        self.timer = timer
        self.disable_gc = disable_gc
        self.logger = logger
        self.log_level = log_level
        self.name = name
        self.start = self.end = self.interval = None

    def __enter__(self):
        if self.disable_gc:
            self.gc_state = gc.isenabled()
            gc.disable()
        if self.logger:
            self.logger.log(self.log_level, '%s started...' % self.name)
        self.start = self.timer()
        return self

    def __exit__(self, *args):
        self.end = self.timer()
        if self.disable_gc and self.gc_state:
            gc.enable()
        self.interval = self.end - self.start
        if self.logger:
            self.logger.log(self.log_level, '%s taken: %f seconds' % (self.name, self.interval))
