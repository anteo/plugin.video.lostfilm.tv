#!/usr/bin/env python

import logging
import StringIO
import traceback
import re
import sys


class CausedException(Exception):
    def __init__(self, *args, **kwargs):
        if len(args) == 1 and not kwargs and isinstance(args[0], Exception):
            # we shall just wrap a non-caused exception
            self.stack = (
                traceback.format_stack()[:-2] +
                traceback.format_tb(sys.exc_info()[2]))
            # ^^^ let's hope the information is still there; caller must take
            # care of this.
            self.wrapped = args[0]
            self._cause = []
            super(CausedException, self).__init__(repr(args[0]))
            # ^^^ to display what it is wrapping, in case it gets printed or similar
            return
        self.wrapped = None
        self.stack = traceback.format_stack()[:-1]  # cut off current frame
        try:
            cause = kwargs['cause']
            del kwargs['cause']
        except KeyError:
            cause = []
        if not isinstance(cause, list):
            cause = [cause]
        self._cause = [CausedException(e) if not isinstance(e, CausedException) else e for e in cause]
        self.kwargs = kwargs
        super(CausedException, self).__init__(*args)

    @property
    def cause(self):
        return [e.wrapped if e.wrapped else e for e in self._cause]

    def cause_tree(self, indentation='  ', already_mentioned_tree=None):
        yield "Traceback (most recent call last):\n"
        already_mentioned_tree = already_mentioned_tree or []
        ellipsed = 0
        for i, line in enumerate(self.stack):
            if ellipsed is not False and i < len(already_mentioned_tree) and line == already_mentioned_tree[i]:
                ellipsed += 1
            else:
                if ellipsed:
                    yield "  ... (%d frame%s repeated)\n" % (
                        ellipsed, "" if ellipsed == 1 else "s")
                    ellipsed = False  # marker for "given out"
                yield line
        e = self if self.wrapped is None else self.wrapped
        for line in traceback.format_exception_only(e.__class__, e):
            yield line
        if self._cause:
            yield ("Caused by %d exception%s\n" %
                   (len(self._cause), "" if len(self._cause) == 1 else "s"))
            for cause_part in self._cause:
                for line in cause_part.cause_tree(indentation, self.stack):
                    yield re.sub(r'([^\n]*\n)', indentation + r'\1', line)

    def log(self, log=logging.root, indentation='  '):
        stream = StringIO.StringIO()
        self.write(stream, indentation)
        log.error(stream.getvalue())

    def write(self, stream=None, indentation='  '):
        stream = sys.stderr if stream is None else stream
        for line in self.cause_tree(indentation):
            stream.write(line)


if __name__ == '__main__':

    def deeplib(i):
        if i == 3:
            1 / 0  # raise non-caused exception
        else:
            raise CausedException("deeplib error %d" % i)

    def library(i):
        if i == 0:
            return "no problem"
        elif i == 1:
            raise CausedException("lib error one %d" % i)
        elif i == 2:
            try:
                deeplib(i)
            except CausedException, e:
                raise CausedException("lib error two %d" % i, cause=e)
            except Exception, e:  # non-caused exception?
                raise CausedException("lib error two %d" % i,
                                      cause=CausedException(e))  # wrap non-caused exception
        elif i == 3:
            try:
                deeplib(i)
            except CausedException, e:
                raise CausedException("lib error three %d" % i, cause=e)
            except Exception, e:  # non-caused exception?
                wrapped_exception = CausedException(e)  # wrap it for fitting in
                try:
                    deeplib(i - 1)  # try again
                except CausedException, e:
                    raise CausedException("lib error three %d" % i,
                                          cause=(wrapped_exception, CausedException(e)))
        else:
            raise CausedException("lib error unexpected %d" % i)

    def application():
        e0 = e1 = e2 = e3 = None
        try:
            library(0)
        except CausedException, e:
            e0 = e
        try:
            library(1)
        except CausedException, e:
            e1 = e
        try:
            library(2)
        except CausedException, e:
            e2 = e
        try:
            library(3)
        except CausedException, e:
            e3 = e
        if e0 or e1 or e2 or e3:
            raise CausedException("application error",
                                  cause=[e for e in (e0, e1, e2, e3) if e is not None])

    try:
        application()
    except CausedException, exc:
        exc.write()
        print >> sys.stderr, "NOW WITH MORE OBVIOUS INDENTATION"
        exc.write(indentation='||  ')
    print >> sys.stderr, "NOW THE DEFAULT HANDLER"
    application()