# -*- coding: utf-8 -*-

from support.common import lang, with_fanart, batch, download_torrent
from xbmcswift2.common import abort_requested
from support.plugin import plugin
from lostfilm.common import select_torrent_link, get_scraper, itemify_episodes, get_torrent, itemify_file, play_torrent, \
    itemify_series, BATCH_SERIES_COUNT, BATCH_EPISODES_COUNT
from support.torrent import Torrent


@plugin.route('/browse_season/<series>/<season>')
def browse_season(series, season):
    plugin.set_content('episodes')
    select_quality = plugin.request.arg('select_quality')
    series = get_scraper().get_series_cached(series)
    link = select_torrent_link(series.id, season, "99", select_quality)
    if not link:
        return []
    torrent = get_torrent(link.url)
    items = [itemify_file(torrent.file_name, series, season, f) for f in torrent.files]
    return with_fanart(items)


@plugin.route('/play_file/<path>/<file_id>')
def play_file(path, file_id):
    torrent = Torrent(file_name=path)
    play_torrent(torrent, file_id)


@plugin.route('/download/<series>/<season>/<episode>')
def download(series, season, episode):
    link = select_torrent_link(series, season, episode, force=True)
    if not link:
        return
    torrent = get_torrent(link.url)
    download_torrent(torrent)


@plugin.route('/play_episode/<series>/<season>/<episode>')
def play_episode(series, season, episode):
    select_quality = plugin.request.arg('select_quality')
    link = select_torrent_link(series, season, episode, select_quality)
    if not link:
        return
    torrent = get_torrent(link.url)
    play_torrent(torrent)


@plugin.route('/browse_series/<series_id>')
def browse_series(series_id):
    plugin.set_content('episodes')
    scraper = get_scraper()
    episodes = scraper.get_series_episodes(series_id)
    items = itemify_episodes(episodes, same_series=True)
    return with_fanart(items)


@plugin.route('/browse_all_series')
def browse_all_series():
    plugin.set_content('tvshows')
    scraper = get_scraper()
    all_series_ids = scraper.get_all_series_ids()
    total = len(all_series_ids)
    for batch_ids in batch(all_series_ids, BATCH_SERIES_COUNT):
        if abort_requested():
            break
        series = scraper.get_series_bulk(batch_ids)
        items = [itemify_series(series[i]) for i in batch_ids]
        plugin.add_items(with_fanart(items), total)
    plugin.finish()


@plugin.route('/')
def index():
    plugin.set_content('episodes')
    skip = plugin.request.arg('skip')
    per_page = plugin.get_setting('per-page', int)
    scraper = get_scraper()
    episodes = scraper.browse_episodes(skip)
    total = len(episodes)
    header = [
        {'label': lang(40401), 'path': plugin.url_for('browse_all_series')},
    ]
    items = []
    if skip:
        skip_prev = max(skip - per_page, 0)
        total += 1
        items.append({
            'label': lang(34003),
            'path': plugin.request.url_with_params(skip=skip_prev)
        })
    elif header:
        items.extend(header)
        total += len(header)
    plugin.add_items(with_fanart(items), total)
    for batch_res in batch(episodes, BATCH_EPISODES_COUNT):
        if abort_requested():
            break
        items = itemify_episodes(batch_res)
        plugin.add_items(with_fanart(items), total)
    items = []
    if scraper.has_more:
        skip_next = (skip or 0) + per_page
        items.append({
            'label': lang(34004),
            'path': plugin.request.url_with_params(skip=skip_next)
        })
    plugin.finish(items=with_fanart(items),
                  cache_to_disc=True,
                  update_listing=skip is not None)
