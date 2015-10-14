# -*- coding: utf-8 -*-
from support import services

import support.titleformat as tf
from xbmcswift2 import xbmcgui, actions
from lostfilm.scraper import Episode, Series, Quality, LostFilmScraper
from support.torrent import TorrentFile
from support.common import lang, date_to_str, singleton, save_files, purge_temp_dir, toggle_watched_menu
from support.plugin import plugin


BATCH_EPISODES_COUNT = 5
BATCH_SERIES_COUNT = 20


def info_menu(obj):
    lang_id = 40306 if isinstance(obj, Series) else 40300
    return [(lang(lang_id), "Action(Info)")]


def go_to_series_menu(s):
    return [(lang(40307), actions.update_view(series_url(s)))]


def download_menu(e):
    from xbmcswift2 import actions
    if plugin.get_setting('torrent-client', int):
        return [(lang(40308), actions.background(plugin.url_for('download', series=e.series_id,
                                                                season=e.season_number,
                                                                episode=e.episode_number)))]
    else:
        return []


def select_quality_menu(e):
    """
    :type e: Episode
    """
    if plugin.get_setting('quality', int) > 0:
        url = episode_url(e, True)
        if e.is_complete_season:
            return [(lang(40303), actions.update_view(url))]
        else:
            return [(lang(40301), actions.play_media(url))]
    else:
        return []


def episode_url(e, select_quality=None):
    """
    :type e: Episode
    """
    if e.is_complete_season:
        return plugin.url_for('browse_season', series=e.series_id, season=e.season_number,
                              select_quality=select_quality)
    else:
        return plugin.url_for('play_episode', series=e.series_id, season=e.season_number,
                              episode=e.episode_number, select_quality=select_quality)


def itemify_episodes(episodes, same_series=False):
    """
    :type episodes: list[Episode]
    """
    series_ids = list(set(e.series_id for e in episodes))
    scraper = get_scraper()
    series = scraper.get_series_bulk(series_ids)
    return [itemify_episode(e, series[e.series_id], same_series) for e in episodes]


def episode_label(e, same_series=False):
    """
    :type e: Episode
    """
    label = ""
    if not e.is_complete_season:
        label += tf.color("%02d.%s " % (e.season_number, e.episode_number), 'blue')
    if not same_series:
        label += tf.color(e.series_title, 'white') + " / " + e.episode_title
    else:
        label += tf.color(e.episode_title, 'white')
    if e.original_title and plugin.get_setting('show-original-title', bool):
        label += " / " + e.original_title
    return label


def itemify_episode(e, s, same_series=False):
    """
    :type e: Episode
    :type s: Series
    """
    item = itemify_common(s)
    item.update({
        'thumbnail': e.poster,
        'label': episode_label(e, same_series),
        'path': episode_url(e),
        'context_menu':
            select_quality_menu(e) + (go_to_series_menu(s) if not same_series else []) +
            download_menu(e) + info_menu(e) + toggle_watched_menu(),
        'is_playable': not e.is_complete_season,
    })
    item['info'].update({
        'episode': e.episode_number if not e.is_complete_season else None,
        'season': e.season_number,
        'title': e.episode_title,
        'premiered': date_to_str(e.release_date, '%Y-%m-%d'),
        'originaltitle': e.original_title,
        'date': date_to_str(e.release_date),
    })
    return item


def itemify_common(s):
    """
    :type s: Series
    """
    item = {
        'thumbnail': s.poster or s.image,
        'icon': s.icon,
        'info': {
            'plot': s.plot or s.about,
            'rating': None,
            'studio': None,
            'castandrole': s.actors,
            'writer': " / ".join(s.writers) if s.writers else None,
            'director': " / ".join(s.producers) if s.producers else None,
            'genre': " / ".join(s.genres) if s.genres else None,
            'tvshowtitle': s.title,
            'year': s.year,
        },
        'properties': {
            'fanart_image': s.image,
        }
    }
    return item


def itemify_file(path, series, season, f):
    """
    :type series: Series
    :type season: string
    :type f: TorrentFile
    """
    item = itemify_common(series)
    item.update({
        'label': f.path,
        'path': plugin.url_for('play_file', path=path, series=series.id, season=season, file_id=f.index),
        'context_menu':
            info_menu(series) + toggle_watched_menu(),
        'is_playable': True,
    })
    item['info'].update({
        'season': season,
        'title': f,
    })
    return item


def series_label(s):
    """
    :type s: Series
    """
    label = tf.color(s.title, 'white')
    if plugin.get_setting('show-original-title', bool):
        label += " / " + s.original_title
    return label


def itemify_series(s):
    """
    :type s: Series
    """
    item = itemify_common(s)
    item.update({
        'label': series_label(s),
        'path': series_url(s),
        'context_menu':
            info_menu(s),
        'is_playable': False,
    })
    item['info'].update({
        'title': s.title,
        'episode': s.episodes_count,
        'original_title': s.original_title,
    })
    return item


def series_url(s):
    """
    :type s: Series
    """
    return plugin.url_for('browse_series', series_id=s.id)


def select_torrent_link(series, season, episode, force=False):
    scraper = get_scraper()
    links = scraper.get_torrent_links(series, season, episode)
    qualities = sorted(Quality)
    quality = plugin.get_setting('quality', int)
    ordered_links = [next((l for l in links if l.quality == q), None) for q in qualities]
    if not quality or force or not ordered_links[quality-1]:
        filtered_links = [l for l in ordered_links if l]
        if not filtered_links:
            return
        options = ["%s / %s" % (tf.color(l.quality.localized, 'white'), tf.human_size(l.size)) for l in filtered_links]
        res = xbmcgui.Dialog().select(lang(40400), options)
        if res < 0:
            return
        return filtered_links[res]
    else:
        return ordered_links[quality-1]


def series_cache():
    return plugin.get_storage('series.db', 24 * 60 * 7, cached=False)


@singleton
def get_scraper():
    from support.services import xrequests_session
    anonymized_urls = plugin.get_storage().setdefault('anonymized_urls', [], ttl=24 * 60 * 7)
    return LostFilmScraper(login=plugin.get_setting('login', unicode),
                           password=plugin.get_setting('password', unicode),
                           cookie_jar=plugin.addon_data_path('cookies'),
                           xrequests_session=xrequests_session(),
                           max_workers=BATCH_SERIES_COUNT,
                           series_cache=series_cache(),
                           anonymized_urls=anonymized_urls)


def play_torrent(torrent, file_id=None):
    stream = services.torrent_stream()
    temp_files = stream.play(services.player(), torrent, file_id=file_id)
    if temp_files:
        save_files(temp_files, rename=not stream.saved_files_needed, on_finish=purge_temp_dir)
    else:
        purge_temp_dir()
