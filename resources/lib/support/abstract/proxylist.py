# -*- coding: utf-8 -*-
from operator import attrgetter
import threading
from util import equal_dicts
from util.causedexception import CausedException


class Anonymity(object):
    NONE = 0
    LOW = 1
    AVG = 2
    HIGH = 3


class SortBy(object):
    PING = 'ping'
    ANONYMITY = 'anonymity'


class Proxy(object):
    HTTP = 'http'
    HTTPS = 'https'
    SOCKS4 = 'socks4'
    SOCKS5 = 'socks5'

    def __init__(self, ip, port, country=None, protocols=None, ping=0, anonymity=None):
        self.ip = ip
        self.port = port
        self.country = country
        self.protocols = protocols or []
        self.ping = ping
        self.anonymity = anonymity

    @property
    def for_requests(self):
        return dict((proto, "%s://%s:%s" % (proto, self.ip, self.port)) for proto in self.protocols)

    def __eq__(self, other):
        return other and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self == other

    def __repr__(self):
        return "<Proxy %s:%d>" % (self.ip, self.port)


class ProxyListException(CausedException):
    pass


class ProxiesListNotAvailable(ProxyListException):
    def __init__(self, *args, **kwargs):
        super(ProxiesListNotAvailable, self).__init__("Can't obtain proxies list", *args, **kwargs)


class NoProxiesAvailable(ProxyListException):
    def __init__(self, proto, *args, **kwargs):
        super(NoProxiesAvailable, self).__init__("No %s proxies available" % proto.upper(), *args, **kwargs)


class ProxyList(object):
    unpickable_properties = ['_lock']

    def __init__(self, sort_by=None, reverse=False):
        self.sort_by = sort_by
        self.reverse = reverse
        self.last_good_proxy = None
        self._lock = threading.RLock()
        self._proxy_counters = {}
        self._proxies = None

    def __eq__(self, other):
        return equal_dicts(self.__dict__, other.__dict__, self.unpickable_properties)

    def __ne__(self, other):
        return not self == other

    def __getstate__(self):
        result = self.__dict__.copy()
        for p in self.unpickable_properties:
            del result[p]
        return result

    def __setstate__(self, _dict):
        self.__dict__ = _dict
        self._lock = threading.RLock()

    def _sorted(self, proxies):
        sort_by = self.sort_by if isinstance(self.sort_by, list) else [self.sort_by]
        return sorted(proxies, key=attrgetter(*sort_by), reverse=self.reverse)

    def _load_proxies(self):
        raise NotImplementedError

    def _ensure_proxies_loaded(self):
        with self._lock:
            if self._proxies is not None:
                return
            proxies = self._load_proxies()
            if self.sort_by:
                proxies = self._sorted(proxies)
            self._proxies = {}
            for proxy in proxies:
                for proto in proxy.protocols:
                    self._proxies.setdefault(proto, []).append(proxy)
            self._proxy_counters = {}

    def reload(self):
        self._proxies = None
        self._proxy_counters = {}
        self.last_good_proxy = None

    def proxies(self, proto=Proxy.HTTP):
        self._ensure_proxies_loaded()
        if proto not in self._proxies:
            raise NoProxiesAvailable(proto)
        return self._proxies[proto]

    def _get_next_proxy(self, proto):
        with self._lock:
            counter = self._proxy_counters.setdefault(proto, 0)
            if counter >= len(self.proxies(proto)):
                self.reload()
                return self._get_next_proxy(proto)
            self._proxy_counters[proto] = counter + 1
            return self._proxies[proto][counter]

    def get_proxy(self, proto=Proxy.HTTP):
        return self.last_good_proxy or self._get_next_proxy(proto)
