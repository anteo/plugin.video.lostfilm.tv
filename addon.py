# -*- coding: utf-8 -*-

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'resources', 'lib'))

import lostfilm.routes
from lostfilm.common import check_first_start
from support.common import run_plugin

if __name__ == '__main__':
    run_plugin()
