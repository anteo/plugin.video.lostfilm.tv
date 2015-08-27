# -*- coding: utf-8 -*-
import logging
import re
import socket
import requests

from urlparse import urlparse


log = logging.getLogger(__name__)


class Immunizer(object):
    def __init__(self):
        self.hosts = []
        self.urls = []
        self.proxy = None

    def add_host(self, name):
        self.hosts.append(socket.gethostbyname(name))

    def is_host_immunized(self, hostname):
        return socket.gethostbyname(hostname) in self.hosts

    def is_url_immunized(self, url):
        hostname = urlparse(url).hostname
        return url in self.urls or self.is_host_immunized(hostname)

    def get_proxy_for_url(self, url):
        if self.is_url_immunized(url) and self.proxy:
            return self.proxy
        else:
            return None


class AntiZapretImmunizer(Immunizer):
    PAC_URL = "http://antizapret.prostovpn.org/proxy.pac"

    def __init__(self):
        super(AntiZapretImmunizer, self).__init__()
        self.antizapret_proxy = None
        self.loaded = False

    def __getstate__(self):
        self.ensure_loaded()
        return self.__dict__

    def get_proxy_for_url(self, url):
        self.ensure_loaded()
        if self.is_host_immunized(urlparse(url).hostname):
            return self.antizapret_proxy
        else:
            return super(AntiZapretImmunizer, self).get_proxy_for_url(url)

    def ensure_loaded(self):
        if not self.loaded:
            self.load()

    def load(self):
        try:
            res = requests.get(self.PAC_URL)
            res.raise_for_status()
        except requests.exceptions.RequestException as e:
            log.warn("Couldn't load immunizer data (%s): %s" % (self.PAC_URL, e))
            return
        data = res.content
        proxy = {}
        r = re.search(r"\"PROXY (.*?);", data)
        if r:
            proxy['http'] = r.group(1)
        r = re.search(r"\"HTTPS (.*?);", data)
        if r:
            proxy['https'] = r.group(1)
        self.antizapret_proxy = proxy
        self.hosts += re.findall(r"\"(\d+\.\d+\.\d+\.\d+)\"", data)
        self.loaded = True
