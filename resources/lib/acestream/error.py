# -*- coding: utf-8 -*-


class Error(Exception):
    CANT_CONNECT = 1
    CANT_SEND_DATA = 2
    CANT_FIND_EXECUTABLE = 3
    CANT_START_ENGINE = 4
    TIMEOUT = 5
    CANT_LOAD_TORRENT = 6
    CANT_PLAY_TORRENT = 7
    INVALID_DOWNLOAD_PATH = 8

    def __init__(self, message, code=0, **kwargs):
        self.message = message
        self.code = code
        self.kwargs = kwargs

    def __str__(self):
        return self.message
