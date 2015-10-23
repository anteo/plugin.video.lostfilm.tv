# -*- coding: utf-8 -*-
from contextlib import closing
from support import services, library

import support.titleformat as tf
from xbmcswift2 import xbmcgui, actions, xbmc, abort_requested
from lostfilm.scraper import Episode, Series, Quality, LostFilmScraper
from support.torrent import TorrentFile
from support.common import lang, date_to_str, singleton, save_files, purge_temp_dir, LocalizedError, \
    batch, toggle_watched_menu
from support.plugin import plugin


BATCH_EPISODES_COUNT = 5
BATCH_SERIES_COUNT = 20
LIBRARY_ITEM_COLOR = "FFFFFB8B"
NEW_LIBRARY_ITEM_COLOR = "lime"


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


def update_library_menu():
    return [(lang(40311), actions.background(plugin.url_for('update_library_on_demand')))]


def library_menu(s):
    """
    :type s: Series
    """
    items = library_items()
    if s.id in items:
        return [(lang(40310), actions.background(plugin.url_for('remove_from_library', series_id=s.id)))]
    else:
        return [(lang(40309), actions.background(plugin.url_for('add_to_library', series_id=s.id)))]


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
    if e in library_new_episodes():
        label += tf.color("* ", NEW_LIBRARY_ITEM_COLOR)
    if e.series_id in library_items() and not same_series:
        color = LIBRARY_ITEM_COLOR
    else:
        color = 'white'
    if not same_series:
        label += tf.color(e.series_title, color) + " / " + e.episode_title
    else:
        label += tf.color(e.episode_title, color)
    if e.original_title and plugin.get_setting('show-original-title', bool):
        label += " / " + e.original_title
    return label


def mark_series_watched_menu(series):
    """
    :type series: Series
    """
    return [(lang(40312), actions.background(plugin.url_for('mark_series_watched',
                                                            series_id=series.id)))]


def toggle_episode_watched_menu(episode):
    """
    :type episode: Episode
    """
    return [(lang(40151), actions.background(plugin.url_for('toggle_episode_watched',
                                                            series_id=episode.series_id,
                                                            episode=episode.episode_number,
                                                            season=episode.season_number)))]


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
            download_menu(e) + info_menu(e) + toggle_episode_watched_menu(e) + library_menu(s),
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


def series_label(s, highlight_library_items=True):
    """
    :type s: Series
    """
    if s.id in library_items() and highlight_library_items:
        color = LIBRARY_ITEM_COLOR
    else:
        color = 'white'
    label = tf.color(s.title, color)
    if plugin.get_setting('show-original-title', bool):
        label += " / " + s.original_title
    new_episodes = library_new_episodes().get_by(series_id=s.id)
    if new_episodes:
        label += " (%s)" % tf.color(str(len(new_episodes)), NEW_LIBRARY_ITEM_COLOR)
    return label


def itemify_series(s, highlight_library_items=True):
    """
    :type s: Series
    """
    item = itemify_common(s)
    item.update({
        'label': series_label(s, highlight_library_items),
        'path': series_url(s),
        'context_menu':
            info_menu(s) + library_menu(s) + mark_series_watched_menu(s),
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
    if not quality or force or not ordered_links[quality - 1]:
        filtered_links = [l for l in ordered_links if l]
        if not filtered_links:
            return
        options = ["%s / %s" % (tf.color(l.quality.localized, 'white'), tf.human_size(l.size)) for l in filtered_links]
        res = xbmcgui.Dialog().select(lang(40400), options)
        if res < 0:
            return
        return filtered_links[res]
    else:
        return ordered_links[quality - 1]


def series_cache():
    return plugin.get_storage('series.db', 24 * 60 * 7, cached=False)


def library_items():
    return plugin.get_storage().setdefault('library_items', [])


def library_new_episodes():
    """
    :rtype : NewEpisodes
    """
    return plugin.get_storage().setdefault('new_episodes', NewEpisodes())


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
    player = services.player()
    temp_files = stream.play(player, torrent, file_id=file_id)
    if temp_files:
        save_files(temp_files, rename=not stream.saved_files_needed, on_finish=purge_temp_dir)
    else:
        purge_temp_dir()


def create_lostfilm_source():
    from support.sources import Sources, TvDbScraperSettings, SourceAlreadyExists
    sources = Sources()
    plugin.log.info("Creating LostFilm.TV source...")
    try:
        sources.add_video(plugin.get_setting('library-path', unicode), 'LostFilm.TV', TvDbScraperSettings())
    except SourceAlreadyExists:
        plugin.set_setting('lostfilm-source-created', True)
        raise LocalizedError(40408, "Source is already exist")
    plugin.log.info("LostFilm.TV source created, restart needed...")
    plugin.set_setting('lostfilm-source-created', True)
    d = xbmcgui.Dialog()
    if d.yesno(lang(40404), lang(40405)):
        xbmc.executebuiltin('Quit')


def check_first_start():
    if is_authorized() and not plugin.get_setting('first-start', bool):
        d = xbmcgui.Dialog()
        plugin.set_setting('first-start', 'true')
        if d.yesno(lang(40402), *(lang(40403).split("|"))):
            create_lostfilm_source()


def get_library():
    path = plugin.get_setting('library-path', unicode)
    path = xbmc.translatePath(path)
    return library.Library(path)


def is_authorized():
    return get_scraper().authorized()


def update_library():
    plugin.log.info("Starting LostFilm.TV library update...")
    progress = xbmcgui.DialogProgressBG()
    scraper = get_scraper()
    series_ids = library_items()
    total = len(series_ids)
    lib = get_library()
    processed = 0
    with closing(progress):
        progress.create(lang(30000), lang(40409))
        series_episodes = {}
        for ids in batch(series_ids, BATCH_SERIES_COUNT):
            series_episodes.update(scraper.get_series_episodes_bulk(ids))
            processed += len(ids)
            progress.update(processed * 100 / total)
            if abort_requested():
                return
        medias = []
        for series_id, episodes in series_episodes.iteritems():
            medias.extend(library.Episode(folder=e.series_title, title=e.episode_title,
                                          season_number=e.season_number, episode_number=e.episode_numbers,
                                          url=episode_url(e), time_added=e.release_date,
                                          episode=e)
                          for e in episodes if not e.is_complete_season)
        lib.sync(medias)
        new_episodes = library_new_episodes()
        new_episodes |= NewEpisodes(lib.added_medias)
    if plugin.get_setting('update-xbmc-library', bool):
        if lib.added_medias or lib.created_medias or lib.updated_medias:
            plugin.wait_library_scan()
            plugin.log.info("Starting XBMC library update...")
            plugin.update_library('video', plugin.get_setting('library-path', unicode))
        if lib.removed_files:
            plugin.wait_library_scan()
            plugin.log.info("Starting XBMC library clean...")
            plugin.clean_library('video')
    plugin.log.info("LostFilm.TV library update finished.")
    return lib.added_medias or lib.created_medias or lib.updated_medias or lib.removed_files


def check_last_episode(e):
    storage = plugin.get_storage()
    if 'last_episode' in storage and storage['last_episode'] != e:
        plugin.log.info("Last episode changed, updating library...")
        plugin.set_setting('update-library', True)
    storage['last_episode'] = e


class NewEpisodes(set):
    def remove_by(self, series_id=None, season_number=None, episode_number=None):
        for e in self.copy():
            episode = e.payload['episode']
            if episode.matches(series_id, season_number, episode_number):
                self.remove(e)

    def get_by(self, series_id=None, season_number=None, episode_number=None):
        return [e for e in self if e.payload['episode'].matches(series_id, season_number, episode_number)]

    def __contains__(self, item):
        if isinstance(item, Episode):
            return any(e.payload['episode'] == item for e in self)
        else:
            return super(NewEpisodes, self).__contains__(item)
