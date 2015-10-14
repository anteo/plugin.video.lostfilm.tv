# -*- coding: utf-8 -*-

from support.common import singleton
from support.plugin import plugin
from support.torrent import TorrentClient, TorrentStream


@singleton
def file_transfer_progress():
    from support.progress import XbmcFileTransferProgress

    return XbmcFileTransferProgress()


@singleton
def transmission_client():
    from support.torrent.client import TransmissionClient

    return TransmissionClient(login=plugin.get_setting('transmission-login', unicode),
                              password=plugin.get_setting('transmission-password', unicode),
                              host=plugin.get_setting('transmission-host', unicode),
                              port=plugin.get_setting('transmission-port', int, default=9091),
                              path=plugin.get_setting('transmission-path', unicode))


@singleton
def utorrent_client():
    from support.torrent.client import UTorrentClient

    return UTorrentClient(login=plugin.get_setting('utorrent-login', unicode),
                          password=plugin.get_setting('utorrent-password', unicode),
                          host=plugin.get_setting('utorrent-host', unicode),
                          port=plugin.get_setting('utorrent-port', int, default=8080))


@singleton
def torrent_client():
    """
    :rtype : TorrentClient
    """
    client = plugin.get_setting('torrent-client', choices=(None, utorrent_client, transmission_client))
    return client() if client else None


@singleton
def acestream_engine():
    import acestream
    from support.common import temp_path

    return acestream.Engine(host=plugin.get_setting('as-host', unicode),
                            port=plugin.get_setting('as-port', int, default=62062),
                            save_path=temp_path() if plugin.get_setting('save-files', int) else None)


@singleton
def stream_buffering_progress():
    from support.progress import XbmcTorrentTransferProgress

    return XbmcTorrentTransferProgress()


@singleton
def stream_playing_progress():
    from support.progress import XbmcOverlayTorrentTransferProgress

    if plugin.get_setting('show-playing-progress', bool):
        return XbmcOverlayTorrentTransferProgress(window_id=12005)


@singleton
def ace_stream():
    from support.torrent.stream import AceStream

    return AceStream(engine=acestream_engine(),
                     buffering_progress=stream_buffering_progress(),
                     playing_progress=stream_playing_progress())


@singleton
def torrent2http_engine():
    import torrent2http
    from support.common import temp_path

    return torrent2http.Engine(download_path=temp_path(),
                               state_file=plugin.addon_data_path('t2h_state'),
                               connections_limit=plugin.get_setting('t2h-max-connections', int, default=None),
                               download_kbps=plugin.get_setting('t2h-download-rate', int, default=None),
                               upload_kbps=plugin.get_setting('t2h-upload-rate', int, default=None),
                               log_overall_progress=plugin.get_setting('t2h-debug-mode', bool),
                               log_pieces_progress=plugin.get_setting('t2h-debug-mode', bool),
                               debug_alerts=plugin.get_setting('t2h-debug-mode', bool),
                               listen_port=plugin.get_setting('t2h-listen-port', int, default=6881),
                               use_random_port=plugin.get_setting('t2h-use-random-port', bool),
                               trackers=['http://retracker.local/announce'],
                               dht_routers=['dht.transmissionbt.com', 'router.utorrent.com', 'router.bittorrent.com'],
                               max_idle_timeout=5,
                               keep_files=True,
                               enable_utp=False)


@singleton
def torrent2http_stream():
    from support.torrent.stream import Torrent2HttpStream

    return Torrent2HttpStream(engine=torrent2http_engine(),
                              buffering_progress=stream_buffering_progress(),
                              playing_progress=stream_playing_progress(),
                              pre_buffer_bytes=plugin.get_setting('t2h-pre-buffer-mb', int) * 1024 * 1024)


@singleton
def torrent_stream():
    """
    :rtype : TorrentStream
    """
    stream = plugin.get_setting('torrent-stream', choices=(torrent2http_stream, ace_stream))
    return stream()


def proxy_list():
    from support.hideme import HideMeProxyList, Proxy, SortBy, Anonymity

    storage = plugin.get_storage()
    proxies = HideMeProxyList(types=[Proxy.HTTP], except_countries=['RU'], sort_by=SortBy.PING,
                              anonymity=[Anonymity.LOW, Anonymity.AVG, Anonymity.HIGH])
    return storage.setdefault('proxies', proxies, ttl=24 * 60 * 3)


def xrequests_session():
    from requests.packages.urllib3.util import Retry
    from support.xrequests import Session

    use_proxy = plugin.get_setting('use-proxy', int)

    session = Session(max_retries=Retry(total=2, status_forcelist=[500, 502, 503, 504], backoff_factor=0.3),
                      timeout=5, proxy_list=proxy_list() if use_proxy else None)

    # noinspection PyUnusedLocal,PyShadowingNames
    def always_use_proxy(request, response):
        return True

    if use_proxy == 2:
        session.add_proxy_need_check(always_use_proxy)

    return session


def torrent(url=None, data=None, file_name=None):
    from support.torrent import Torrent

    return Torrent(url, data, file_name)


@singleton
def player():
    from support.player import XbmcPlayer

    return XbmcPlayer()
