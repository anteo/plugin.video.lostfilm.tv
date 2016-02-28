# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from collections import namedtuple
import hashlib
import re

from concurrent.futures import ThreadPoolExecutor, as_completed
from support.common import str_to_date, Attribute
from support.abstract.scraper import AbstractScraper, ScraperError, parse_size
from util.encoding import ensure_str
from util.htmldocument import HtmlDocument
from util.timer import Timer


class Series(namedtuple('Series', ['id', 'title', 'original_title', 'image', 'icon', 'poster', 'country', 'year',
                                   'genres', 'about', 'actors', 'producers', 'writers', 'plot', 'seasons_count',
                                   'episodes_count'])):
    pass


class Episode(namedtuple('Episode', ['series_id', 'series_title', 'season_number', 'episode_number', 'episode_title',
                                     'original_title', 'release_date', 'icon', 'poster', 'image'])):
    def __eq__(self, other):
        return self.series_id == other.series_id and \
            self.season_number == other.season_number and \
            self.episode_number == other.episode_number

    def __ne__(self, other):
        return not self == other

    def matches(self, series_id=None, season_number=None, episode_number=None):
        def eq(a, b):
            return str(a).lstrip('0') == str(b).lstrip('0')

        return (series_id is None or eq(self.series_id, series_id)) and \
               (season_number is None or eq(self.season_number, season_number)) and \
               (episode_number is None or eq(self.episode_number, episode_number))

    @property
    def is_complete_season(self):
        return self.episode_number == "99"

    @property
    def is_multi_episode(self):
        return "-" in self.episode_number

    @property
    def episode_numbers(self):
        if self.is_multi_episode:
            start, end = self.episode_number.split("-", 2)
            return range(int(start), int(end) + 1)
        else:
            return [int(self.episode_number)]


class Quality(Attribute):
    def get_lang_base(self):
        return 40208

    SD = (0, 'sd')
    HD_720 = (1, 'mp4', 'hd')
    HD_1080 = (2, '1080p', '1080')

    def __lt__(self, other):
        return self.id < other.id


TorrentLink = namedtuple('TorrentLink', ['quality', 'url', 'size'])


class LostFilmScraper(AbstractScraper):
    BASE_URL = "http://www.lostfilm.tv"
    LOGIN_URL = "http://login1.bogi.ru/login.php"
    BLOCKED_MESSAGE = "Контент недоступен на территории Российской Федерации"

    def __init__(self, login, password, cookie_jar=None, xrequests_session=None, series_cache=None, max_workers=10,
                 anonymized_urls=None):
        super(LostFilmScraper, self).__init__(xrequests_session, cookie_jar)
        self.series_cache = series_cache if series_cache is not None else {}
        self.max_workers = max_workers
        self.response = None
        self.login = login
        self.password = password
        self.has_more = None
        self.anonymized_urls = anonymized_urls if anonymized_urls is not None else []
        self.session.headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.116 Safari/537.36'
        self.session.add_proxy_need_check(self._check_content_is_blocked)
        self.session.add_proxy_validator(self._validate_proxy)

    # noinspection PyUnusedLocal
    def _validate_proxy(self, proxy, request, response):
        if response.status_code != 200 and response.status_code != 302:
            return "Returned status %d" % response.status_code
        if 'browse.php' in request.url or 'serials.php' in request.url:
            if 'id="MainDiv"' not in response.text:
                return "Response doesn't match original"
            elif self.BLOCKED_MESSAGE in response.text:
                return "Returned blocked content"

    def _check_content_is_blocked(self, request, response):
        if request.url in self.anonymized_urls:
            return True
        elif response and self.BLOCKED_MESSAGE in response.text:
            self.log.info("Content of %s blocked, trying to use anonymous proxy..." % request.url)
            self.anonymized_urls.append(request.url)
            return True
        else:
            return False

    def fetch(self, url, params=None, data=None, **request_params):
        self.response = super(LostFilmScraper, self).fetch(url, params, data, **request_params)
        encoding = self.response.encoding
        if encoding == 'ISO-8859-1':
            encoding = 'windows-1251'
        return HtmlDocument.from_string(self.response.content, encoding)

    def authorize(self):
        with Timer(logger=self.log, name='Authorization'):
            self.fetch(self.BASE_URL + '/browse.php')
            doc = self.fetch(self.LOGIN_URL,
                             params={'referer': 'http://www.lostfilm.tv/'},
                             data={'login': self.login, 'password': self.password})
            action_url = doc.find('form').attr('action')
            names = doc.find('input', {'type': 'hidden'}).attrs('name')
            values = doc.find('input', {'type': 'hidden'}).attrs('value')
            params = zip(names, [ensure_str(s) for s in values])
            if not action_url or not names or not values:
                self.log.debug(doc)
                raise ScraperError(32003, "Authorization failed", check_settings=True)
            self.fetch(action_url, data=params)
            self.session.cookies['hash'] = self.authorization_hash
            if not self.authorized():
                raise ScraperError(32003, "Authorization failed", check_settings=True)

    @property
    def authorization_hash(self):
        return hashlib.md5(self.login + self.password).hexdigest()

    def authorized(self):
        cookies = self.session.cookies
        if not cookies.get('uid') or not cookies.get('pass'):
            return False
        if cookies.get('hash') != self.authorization_hash:
            try:
                cookies.clear('.lostfilm.tv')
            except KeyError:
                pass
            return False
        return True

    def ensure_authorized(self):
        if not self.authorized():
            self.authorize()

    def get_series_bulk(self, series_ids):
        """
        :rtype : dict[int, Series]
        """
        if not series_ids:
            return {}
        cached_details = self.series_cache.keys()
        not_cached_ids = [_id for _id in series_ids if _id not in cached_details]
        results = dict((_id, self.series_cache[_id]) for _id in series_ids if _id in cached_details)
        if not_cached_ids:
            with Timer(logger=self.log,
                       name="Bulk fetching series with IDs " + ", ".join(str(i) for i in not_cached_ids)):
                with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                    futures = [executor.submit(self.get_series_info, _id) for _id in not_cached_ids]
                    for future in as_completed(futures):
                        result = future.result()
                        self.series_cache[result.id] = results[result.id] = result
        return results

    def get_series_cached(self, series_id):
        return self.get_series_bulk([series_id])[series_id]

    def get_all_series_ids(self):
        doc = self.fetch(self.BASE_URL + "/serials.php")
        mid = doc.find('div', {'class': 'mid'})
        links = mid.find('a', {'href': '/browse\.php\?cat=.+?', 'class': 'bb_a'}).attrs('href')
        ids = [int(l[16:].lstrip("_")) for l in links]
        return ids

    def _get_series_doc(self, series_id):
        return self.fetch(self.BASE_URL + "/browse.php", {'cat': series_id})

    def get_series_episodes(self, series_id):
        doc = self._get_series_doc(series_id)
        episodes = []
        with Timer(logger=self.log, name='Parsing episodes of series with ID %d' % series_id):
            body = doc.find('div', {'class': 'mid'})
            series_title, original_title = parse_title(body.find('h1').first.text)
            image = self.BASE_URL + body.find('img').attr('src')
            icon = image.replace('/posters/poster_', '/icons/cat_')
            episode_divs = body.find('div', {'class': 't_row.*?'})
            series_poster = None
            for ep in episode_divs:
                title_td = ep.find('td', {'class': 't_episode_title'})
                episode_title, orig_title = parse_title(title_td.text)
                onclick = title_td.attr('onClick')
                release_date = ep.find('span', {'class': 'micro'}).find('span')[0].text
                release_date = str_to_date(release_date, '%d.%m.%Y %H:%M') if release_date else None
                _, season_number, episode_number = parse_onclick(onclick)
                poster = poster_url(original_title, season_number)
                if not series_poster:
                    series_poster = poster
                episode = Episode(series_id, series_title, season_number, episode_number, episode_title,
                                  orig_title, release_date, icon, poster, image)
                episodes.append(episode)
            self.log.info("Got %d episode(s) successfully" % (len(episodes)))
            self.log.debug(repr(episodes).decode("unicode-escape"))
        return episodes

    def get_series_episodes_bulk(self, series_ids):
        """
        :rtype : dict[int, list[Episode]]
        """
        if not series_ids:
            return {}
        results = {}
        with Timer(logger=self.log,
                   name="Bulk fetching series episodes with IDs " + ", ".join(str(i) for i in series_ids)):
            with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
                futures = dict((executor.submit(self.get_series_episodes, _id), _id) for _id in series_ids)
                for future in as_completed(futures):
                    _id = futures[future]
                    results[_id] = future.result()
        return results

    def get_series_info(self, series_id):
        doc = self._get_series_doc(series_id)
        with Timer(logger=self.log, name='Parsing series info with ID %d' % series_id):
            body = doc.find('div', {'class': 'mid'})
            series_title, original_title = parse_title(body.find('h1').first.text)
            image = self.BASE_URL + body.find('img').attr('src')
            icon = image.replace('/posters/poster_', '/icons/cat_')
            info = body.find('div').first.text.replace("\xa0", "")

            res = re.search('Страна: (.+)\r\n', info)
            country = res.group(1) if res else None
            res = re.search('Год выхода: (.+)\r\n', info)
            year = res.group(1) if res else None
            res = re.search('Жанр: (.+)\r\n', info)
            genres = res.group(1).split(', ') if res else None
            res = re.search('Количество сезонов: (.+)\r\n', info)
            seasons_count = int(res.group(1)) if res else 0
            res = re.search('О сериале[^\r\n]+\s*(.+?)($|\r\n)', info, re.S | re.M)
            about = res.group(1) if res else None
            res = re.search('Актеры:\s*(.+?)($|\r\n)', info, re.S | re.M)
            actors = [parse_title(t) for t in res.group(1).split(', ')] if res else None
            res = re.search('Режиссеры:\s*(.+?)($|\r\n)', info, re.S | re.M)
            producers = res.group(1).split(', ') if res else None
            res = re.search('Сценаристы:\s*(.+?)($|\r\n)', info, re.S | re.M)
            writers = res.group(1).split(', ') if res else None
            res = re.search('Сюжет:\s*(.+?)($|\r\n)', info, re.S | re.M)
            plot = res.group(1) if res else None

            episodes_count = len(body.find('div', {'class': 't_row.*?'})) - \
                len(body.find('label', {'title': 'Сезон полностью'}))

            poster = poster_url(original_title, seasons_count)
            series = Series(series_id, series_title, original_title, image, icon, poster, country, year,
                            genres, about, actors, producers, writers, plot, seasons_count, episodes_count)

            self.log.info("Parsed '%s' series info successfully" % series_title)
            self.log.debug(repr(series).decode("unicode-escape"))

        return series

    def browse_episodes(self, skip=0):
        self.ensure_authorized()
        doc = self.fetch(self.BASE_URL + "/browse.php", {'o': skip})
        with Timer(logger=self.log, name='Parsing episodes list'):
            body = doc.find('div', {'class': 'content_body'})
            series_titles = body.find('span', {'style': 'font-family:arial;.*?'}).strings
            titles = body.find('span', {'class': 'torrent_title'}).strings
            episode_titles, original_titles = zip(*[parse_title(t) for t in titles])
            release_dates = body.find('b').strings[1::3]
            release_dates = [str_to_date(d, '%d.%m.%Y %H:%M') for d in release_dates]
            selected_page = body.find('span', {'class': 'd_pages_link_selected'}).text
            last_page = body.find('a', {'class': 'd_pages_link'}).last.text
            self.has_more = int(selected_page) < int(last_page)
            icons = body.find('img', {'class': 'category_icon'}).attrs('src')
            onclicks = body.find('a', {'href': 'javascript:{};'}).attrs('onClick')
            series_ids, season_numbers, episode_numbers = zip(*[parse_onclick(s or "") for s in onclicks])
            posters = [poster_url(i[0][18:-5], i[1]) for i in zip(icons, season_numbers)]
            icons = [self.BASE_URL + url for url in icons]
            images = [url.replace('/icons/cat_', '/posters/poster_') for url in icons]
            data = zip(series_ids, series_titles, season_numbers,
                       episode_numbers, episode_titles, original_titles, release_dates, icons, posters, images)
            episodes = [Episode(*e) for e in data if e[0]]
            self.log.info("Got %d episode(s) successfully" % (len(episodes)))
            self.log.debug(repr(episodes).decode("unicode-escape"))
        return episodes

    def get_torrent_links(self, series_id, season_number, episode_number):
        doc = self.fetch(self.BASE_URL + '/nrdr.php', {
            'c': series_id,
            's': season_number,
            'e': episode_number
        })
        links = []
        with Timer(logger=self.log, name='Parsing torrent links'):
            urls = doc.find('a', {'style': 'font-size:18px;.*?'}).attrs('href')
            table = doc.find('table')
            qualities = table.find('img', {'src': 'img/search_.+?'}).attrs('src')
            qualities = [s[11:-4] for s in qualities]
            sizes = re.findall('Размер: (.+)\.', table.text)
            for url, qua, size in zip(urls, qualities, sizes):
                links.append(TorrentLink(Quality.find(qua), url, parse_size(size)))
            self.log.info("Got %d link(s) successfully" % (len(links)))
            self.log.info(repr(links).decode("unicode-escape"))
        return links


def parse_title(t):
    title, original_title = re.findall('^(.*?)\s*(?:\((.*)\)\.?)?$', t)[0]
    return title, original_title


def parse_onclick(s):
    res = re.findall("ShowAllReleases\('([^']+)','([^']+)','([^']+)'\)", s)
    if res:
        series_id, season, episode = res[0]
        series_id = int(series_id.lstrip("_"))
        season = int(season.split('.')[0])
        return series_id, season, episode
    else:
        return 0, 0, ""


def poster_url(original_title, season):
    return 'http://i551.photobucket.com/albums/ii448/suslikcorp/lostfilm/posters/%s-s%02d-lostfilm.jpg' \
           % (re.sub(r'[^a-z]+', '', original_title.lower()), season)
