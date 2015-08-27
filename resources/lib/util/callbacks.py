# -*- coding: utf-8 -*-

import logging
import inspect


class ContextManager(object):
    def __init__(self, callbacks, event, callback):
        """
        :type callbacks: Callbacks
        """
        self.callbacks = callbacks
        self.event = event
        self.callback = callback

    def __enter__(self):
        self.callbacks.attach(self.event, self.callback)
        return self.callbacks

    # noinspection PyUnusedLocal
    def __exit__(self, exc_type, exc_value, traceback):
        self.callbacks.detach(self.event, self.callback)


class Callbacks(object):
    def __init__(self):
        self.callbacks = {}
        self.log = logging.getLogger(__name__)

    def attached(self, event, callback):
        return ContextManager(self, event, callback)

    def attach(self, event, callback):
        if isinstance(event, list):
            for e in event:
                self.attach(e, callback)
        else:
            self.log.debug("Attaching %s to event '%s'", callback, event)
            if event not in self.callbacks:
                self.callbacks[event] = []
            if callback not in self.callbacks[event]:
                self.callbacks[event].append(callback)

    def detach(self, event=None, callback=None):
        if isinstance(event, list):
            for e in event:
                self.detach(e, callback)
        else:
            self.log.debug("Detaching %s from %s", callback or "all callbacks",
                           "event '%s'" % event if event else "all events")
            if (event is None or event == "*") and callback is None:
                self.callbacks = {}
            elif event is not None and event != "*" and callback is not None:
                if event in self.callbacks:
                    self.callbacks[event].remove(callback)
            elif event == "*" or callback is None:
                for event in self.callbacks:
                    self.callbacks[event].remove(callback)
            else:
                self.callbacks.pop(event, None)

    def run_callbacks(self, event, *args, **kwargs):
        if event != "*":
            self.run_callbacks("*", *args, **kwargs)
            self.log.debug("Event '%s' occurred.", event)
        if event in self.callbacks:
            for callback in self.callbacks[event]:
                self.log.debug("Running callback %s for event '%s'", callback, event)
                argspec = inspect.getargspec(callback)
                specargs = argspec.args
                if hasattr(callback, 'im_self') and callback.im_self is not None:
                    specargs = specargs[1:]
                kwargs['event'] = event
                kwargs = dict(filter(lambda v: v[0] in specargs, kwargs.iteritems()))
                if len(args) > len(specargs):
                    args = args[:len(specargs)]
                callback(*args, **kwargs)
