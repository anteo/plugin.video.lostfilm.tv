# -*- coding: utf-8 -*-
import logging
import requests
from support.abstract.proxylist import *
from concurrent.futures import ThreadPoolExecutor
from util.htmldocument import HtmlDocument
from util.pygif import GifDecoder


def split_by_n(line, n):
    return [line[i:i + n] for i in range(0, len(line), n)]


class HideMeProxyList(ProxyList):
    BASE_URL = 'http://hideme.ru'
    USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) ' \
                 'Chrome/45.0.2454.101 Safari/537.36'

    COUNTRIES = ["AL", "AR", "AU", "BD", "BY", "BE", "BZ", "BO", "BR", "BG", "KH", "CM", "CA", "CL", "CN",
                 "CO", "CR", "CY", "CZ", "EC", "EG", "EU", "FI", "FR", "GE", "DE", "GH", "GI", "GR", "HK", "HU", "IN",
                 "ID", "IR", "IQ", "IE", "IT", "JP", "KZ", "KE", "KR", "LA", "LV", "LB", "LT", "MK", "MY", "MV", "MX",
                 "MD", "MN", "MZ", "NA", "NP", "NL", "NG", "PK", "PS", "PA", "PY", "PE", "PH", "PL", "RO", "RU", "RS",
                 "SC", "SG", "SK", "SI", "ZA", "ES", "LK", "SE", "CH", "SY", "TW", "TZ", "TH", "TN", "TR", "UA", "GB",
                 "US", "UZ", "VE", "VN", "VG", "ZW"]

    PORT_GLYPHS = [263177052548475L,  # 0
                   144856293813883L,  # 1
                   145064598633393L,  # 2
                   218716642933681L,  # 3
                   245707409415415L,  # 4
                   218716641628064L,  # 5
                   218715551690595L,  # 6
                   272537080527840L,  # 7
                   218715551886257L,  # 8
                   250121207606193L,  # 9
                   281474976710655L,  # Space
                   ]

    unpickable_properties = ProxyList.unpickable_properties[:]
    unpickable_properties.extend(['log', 'requests_session'])

    def __init__(self, types=None, countries=None, except_countries=None, maxtime=None, ports=None, anonymity=None,
                 sort_by=None, reverse=False):
        super(HideMeProxyList, self).__init__(sort_by, reverse)
        self.log = logging.getLogger(__name__)
        self.requests_session = requests.Session()
        self.types = types
        self.countries = countries
        self.except_countries = except_countries
        self.anonymity = anonymity
        self.maxtime = maxtime
        self.ports = ports

    def __setstate__(self, _dict):
        super(HideMeProxyList, self).__setstate__(_dict)
        self.log = logging.getLogger(__name__)
        self.requests_session = requests.Session()

    def _prepare_params(self):
        params = {}
        if self.types is not None:
            if isinstance(self.types, list):
                types = ""
                for t in self.types:
                    if t == Proxy.HTTP:
                        types += 'h'
                    elif t == Proxy.HTTPS:
                        types += 's'
                    elif t == Proxy.SOCKS4:
                        types += '4'
                    elif t == Proxy.SOCKS5:
                        types += '5'
                params['type'] = types
            else:
                params['type'] = self.types
        if self.anonymity is not None:
            if isinstance(self.anonymity, list):
                anonymity = ""
                for t in self.anonymity:
                    if t == Anonymity.NONE:
                        anonymity += '1'
                    elif t == Anonymity.LOW:
                        anonymity += '2'
                    elif t == Anonymity.AVG:
                        anonymity += '3'
                    elif t == Anonymity.HIGH:
                        anonymity += '4'
                params['anon'] = anonymity
            else:
                params['anon'] = self.anonymity
        countries = []
        if self.countries is not None:
            if isinstance(self.countries, list):
                countries = self.countries
            else:
                countries = split_by_n(self.countries, 2)
        if self.except_countries is not None:
            if not countries:
                countries = self.COUNTRIES
            if isinstance(self.except_countries, list):
                excludes = self.except_countries
            else:
                excludes = split_by_n(self.except_countries, 2)
            excludes = set(excludes)
            countries = [c for c in countries if c not in excludes]
        if countries:
            params['country'] = "".join(countries)
        if self.maxtime is not None:
            params['maxtime'] = self.maxtime
        if self.ports is not None:
            if isinstance(self.ports, list):
                params['ports'] = ",".join(self.ports)
            else:
                params['ports'] = self.ports
        return params

    def _prepare_headers(self):
        return {
            'user-agent': self.USER_AGENT
        }

    def _recognize_port(self, filename, gif_content):
        gif = GifDecoder(gif_content)
        if gif.ls_width != 32 or gif.ls_height != 12:
            self.log.warn('Proxy port image should be 32x12 size, skipping %s' % filename)
            return False
        pixels = gif.images[0].pixels
        port = 0
        exp = 1
        for n in reversed(xrange(5)):
            glyph = 0L
            glyph_str = ""
            i = 0
            for y in xrange(3, 11):
                for x in xrange(n * 6, (n + 1) * 6):
                    pixel = pixels[y * 32 + x]
                    glyph_str += "X" if not pixel else " "
                    glyph += (pixel << i)
                    i += 1
                glyph_str += "\n"
            try:
                digit = self.PORT_GLYPHS.index(glyph)
            except ValueError:
                self.log.warn('Glyph not recognized, skipping %s' % filename)
                self.log.info('Hash: %ld' % glyph)
                self.log.info('Figure:\n' + glyph_str)
                return False
            if digit >= 10:
                continue
            port += exp * digit
            exp *= 10
        return port

    def _download_port_gif_and_recognize(self, url):
        try:
            res = self.requests_session.get(url)
            res.raise_for_status()
        except requests.exceptions.RequestException:
            self.log.warn("Can't get port image, skipping %s" % url)
            return False
        return self._recognize_port(url, res.content)

    def _load_proxies(self):
        self.log.info("Getting hideme.ru proxy list...")
        try:
            response = self.requests_session.get(self.BASE_URL + "/proxy-list/", params=self._prepare_params(),
                                                 headers=self._prepare_headers())
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            raise ProxyListException("Can't obtain proxies list", cause=e)
        doc = HtmlDocument.from_string(response.content, response.encoding)
        table = doc.find('table', {'class': 'pl'})
        port_images = []
        proxies = []
        for row in table.find('tr'):
            td = row.find('td')
            if not td:
                continue
            img = td[1].find('img', {'src': '/images/proxylist_port_\d+.gif'}).attr('src')
            if not img:
                self.log.warn("Can't get image port URL, skipping...")
                continue
            proto = td[5].text.lower().split(", ")
            try:
                ping = int(td[4].text.split(" ")[0])
            except (ValueError, KeyError):
                ping = 0
            anon = td[6].text
            if anon == u'Нет':
                anon = Anonymity.NONE
            elif anon == u'Низкая':
                anon = Anonymity.LOW
            elif anon == u'Средняя':
                anon = Anonymity.AVG
            elif anon == u'Высокая':
                anon = Anonymity.HIGH
            else:
                anon = None
            proxy = Proxy(td[0].text, False, td[2].text, proto, ping, anon)
            port_images.append(self.BASE_URL + img)
            proxies.append(proxy)

        with ThreadPoolExecutor(max_workers=5) as e:
            ports = e.map(self._download_port_gif_and_recognize, port_images)
            for i, port in enumerate(ports):
                proxies[i].port = port

        proxies = [p for p in proxies if p.port]
        if not proxies:
            raise ProxyListException("Can't obtain proxies list (hideme.ru structure has changed?)")
        self.log.info("%d proxy(ies) have successfully obtained." % len(proxies))
        self.log.debug(proxies)
        return proxies
