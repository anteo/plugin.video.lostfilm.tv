# -*- coding: utf-8 -*-

import requests
from requests import adapters


class Session(requests.Session):

    def __init__(self, timeout=None, max_retries=adapters.DEFAULT_RETRIES, immunizer=None):
        super(Session, self).__init__()

        self.immunizer = immunizer
        adapter = HTTPAdapter(max_retries=max_retries, timeout=timeout, immunizer=immunizer)
        self.mount('http://', adapter)
        self.mount('https://', adapter)


class HTTPAdapter(adapters.HTTPAdapter):
    def __init__(self, pool_connections=adapters.DEFAULT_POOLSIZE,
                 pool_maxsize=adapters.DEFAULT_POOLSIZE, max_retries=adapters.DEFAULT_RETRIES,
                 pool_block=adapters.DEFAULT_POOLBLOCK, timeout=None, immunizer=None):
        super(HTTPAdapter, self).__init__(pool_connections, pool_maxsize, max_retries, pool_block)
        self.timeout = timeout
        self.immunizer = immunizer

    def send(self, request, stream=False, timeout=None, verify=True, cert=None, proxies=None):
        timeout = timeout or self.timeout
        if self.immunizer and not proxies:
            proxies = self.immunizer.get_proxy_for_url(request.url)
        return super(HTTPAdapter, self).send(request, stream, timeout, verify, cert, proxies)
