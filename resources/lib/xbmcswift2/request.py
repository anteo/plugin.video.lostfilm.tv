"""
    xbmcswift2.request
    ------------------

    This module contains the Request class. This class represents an incoming
    request from XBMC.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
"""
from xbmcswift2.common import unpickle_args
import urlparse
import urllib
try:
    from urlparse import parse_qs
except ImportError:
    from cgi import parse_qs


class Request(object):
    """The request objects contains all the arguments passed to the plugin via
    the command line.

    :param url: The complete plugin URL being requested. Since XBMC typically
                passes the URL query string in a separate argument from the
                base URL, they must be joined into a single string before being
                provided.
    :param handle: The handle associated with the current request.
    """

    def __init__(self, url, handle):
        #: The entire request url.
        self.url = url

        #: The current request's handle, an integer.
        self.handle = int(handle)

        # urlparse doesn't like the 'plugin' scheme, so pass a protocol
        # relative url, e.g. //plugin.video.helloxbmc/path
        self.scheme, remainder = url.split(':', 1)
        parts = urlparse.urlparse(remainder)
        self.netloc, self.path, self.query_string = (
            parts[1], parts[2], parts[4])
        # noinspection PyDeprecation
        self.args = unpickle_args(parse_qs(self.query_string))

        # Convert string to integers where possible
        for key, val in self.args.items():
            for k, v in enumerate(val):
                if isinstance(v, basestring):
                    try:
                        self.args[key][k] = int(v)
                    except ValueError:
                        pass

    def url_with_params(self, **kwargs):
        scheme, remainder = self.url.split(':', 1)
        url_parts = list(urlparse.urlparse(remainder))
        query = dict(self.args)
        query.update(kwargs)
        url_parts[4] = urllib.urlencode(query)
        url_parts[0] = scheme
        return urlparse.urlunparse(url_parts)

    def arg(self, name, default=None):
        if name in self.args:
            val = self.args[name]
            if len(val) == 1:
                val = val[0]
            return val
        else:
            return default