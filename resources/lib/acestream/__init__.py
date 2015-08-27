# -*- coding: utf-8 -*-

from collections import namedtuple


class State:
    IDLE = 0
    PREBUFFERING = 1
    DOWNLOADING = 2
    BUFFERING = 3
    COMPLETED = 4
    CHECKING = 5
    ERROR = 6

    def __init__(self):
        pass


Status = namedtuple("Status", "state, status, progress, down_speed, up_speed, download, upload, peers, url, error")

from engine import Engine
from error import Error
from sink import Sink

