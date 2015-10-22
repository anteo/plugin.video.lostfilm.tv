# -*- coding: utf-8 -*-
import logging
import threading
import requests

# noinspection PyPep8Naming
from socket import timeout as SocketTimeout
from requests.packages.urllib3.connection import BaseSSLError
from concurrent.futures import ThreadPoolExecutor, as_completed
from requests import adapters, RequestException
from urlparse import urlparse

DEFAULT_PROXY_TRIES = 20


class XRequestsException(RequestException):
    pass


class NoValidProxiesFound(XRequestsException):
    pass


class ProxyAlreadyFound(XRequestsException):
    pass


class ProxyInvalid(XRequestsException):
    def __init__(self, message, *args, **kwargs):
        self.proxy = kwargs.pop('proxy', None)
        message = "Proxy %r: %s" % (self.proxy, message)
        super(ProxyInvalid, self).__init__(message, *args, **kwargs)


class Session(requests.Session):

    def __init__(self, timeout=None, max_retries=adapters.DEFAULT_RETRIES, proxy_list=None,
                 proxy_tries=DEFAULT_PROXY_TRIES, **adapter_params):
        super(Session, self).__init__()

        self.timeout = timeout
        self.proxy_list = proxy_list
        self.proxy_tries = proxy_tries
        self.proxy_validators = []
        self.proxy_need_checks = []

        adapter = HTTPAdapter(max_retries=max_retries, session=self, **adapter_params)
        self.mount('http://', adapter)
        self.mount('https://', adapter)

    def add_proxy_validator(self, func):
        self.proxy_validators.append(func)

    def add_proxy_need_check(self, func):
        self.proxy_need_checks.append(func)

    def validate_proxy_response(self, proxy, request, response):
        for func in self.proxy_validators:
            res = func(proxy=proxy, request=request, response=response)
            if not res:
                continue
            if not isinstance(res, basestring):
                res = 'Invalid proxy (%r)' % func
            raise ProxyInvalid(res, proxy=proxy, request=request, response=response)

    def is_proxy_needed(self, request, response=None):
        for func in self.proxy_need_checks:
            if func(request=request, response=response) is True:
                return True
        return False


class HTTPAdapter(adapters.HTTPAdapter):
    def __init__(self, session, pool_connections=adapters.DEFAULT_POOLSIZE,
                 pool_maxsize=adapters.DEFAULT_POOLSIZE, max_retries=adapters.DEFAULT_RETRIES,
                 pool_block=adapters.DEFAULT_POOLBLOCK, debug_headers=False):
        """
        :type session: Session
        """
        super(HTTPAdapter, self).__init__(pool_connections, pool_maxsize, max_retries, pool_block)
        self.session = session
        self.debug_headers = debug_headers
        self.log = logging.getLogger(__name__)
        self._lock = threading.Lock()

    def _try_proxy(self, request, stream, timeout, verify, cert):
        scheme = urlparse(request.url).scheme
        proxy_list = self.session.proxy_list
        if proxy_list.last_good_proxy:
            raise ProxyAlreadyFound()
        proxy = proxy_list.get_proxy(scheme)
        self.log.debug('Trying %r...' % proxy)
        response = self._send(request, stream, timeout, verify, cert, proxy.for_requests)
        self.session.validate_proxy_response(proxy, request, response)
        if not proxy_list.last_good_proxy:
            self.log.info("Found valid proxy: %r" % proxy)
            proxy_list.last_good_proxy = proxy
        return response

    def _send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        if self.debug_headers:
            self.log.debug("Request headers: %r" % request.headers)
        response = super(HTTPAdapter, self).send(request, stream, timeout, verify, cert, proxies)
        if self.debug_headers:
            self.log.debug("Response headers: %r" % response.headers)
        if not stream:
            try:
                response.content
            except (SocketTimeout, BaseSSLError) as e:
                raise requests.exceptions.ReadTimeout(e, request=response.request)
        return response

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        timeout = timeout or self.session.timeout
        proxy_list = self.session.proxy_list

        if not proxy_list or proxies or not self.session.is_proxy_needed(request):
            response = self._send(request, stream, timeout, verify, cert, proxies)
            if not proxy_list or proxies or not self.session.is_proxy_needed(request, response):
                return response

        self._lock.acquire()
        while proxy_list.last_good_proxy:
            self._lock.release()
            try:
                response = self._send(request, stream, timeout, verify, cert,
                                      proxy_list.last_good_proxy.for_requests)
                self.session.validate_proxy_response(proxy_list.last_good_proxy, request, response)
                return response
            except requests.RequestException as e:
                self.log.warn(e)
                proxy_list.last_good_proxy = None
            self._lock.acquire()

        self.log.info("Looking for valid proxy...")
        executor = ThreadPoolExecutor(max_workers=self.session.proxy_tries / 2)
        futures = [executor.submit(self._try_proxy, request, stream, timeout, verify, cert)
                   for _ in range(self.session.proxy_tries)]
        try:
            for future in as_completed(futures):
                try:
                    response = future.result()
                    return response
                except requests.RequestException as e:
                    self.log.debug(e)
                    pass
        finally:
            self._lock.release()
            executor.shutdown(wait=False)
        self.log.info("No valid proxies found.")
        raise NoValidProxiesFound(request=request)
