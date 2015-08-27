# -*- coding: utf-8 -*-


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