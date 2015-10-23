# -*- coding: utf-8 -*-
import sys


FILENAME_CLEAN_RE = ur'[/\\<>:"\|\?\* \t\n\r\u200f]+'


def ensure_unicode(string, encoding='utf-8'):
    if isinstance(string, str):
        string = string.decode(encoding)
    return string


def ensure_str(string, encoding='utf-8'):
    if isinstance(string, unicode):
        string = string.encode(encoding)
    if not isinstance(string, str):
        string = str(string)
    return string


def get_filesystem_encoding():
    return sys.getfilesystemencoding() or 'utf-8'


def decode_fs(string, errors='strict'):
    return unicode(string, get_filesystem_encoding(), errors)


def encode_fs(string, errors='strict'):
    string = ensure_unicode(string)
    return string.encode(get_filesystem_encoding(), errors)


def clean_filename(filename):
    import re
    return re.sub(FILENAME_CLEAN_RE, ' ', filename).rstrip(".")
