# -*- coding: utf-8 -*-


def declension_ru(n, s1, s2, s5):
    ns = n % 10
    n2 = n % 100

    if 10 <= n2 <= 19:
        return s5

    if ns == 1:
        return s1

    if 2 <= ns <= 4:
        return s2

    return s5


def color(title, color_val):
    return "[COLOR %s]%s[/COLOR]" % (color_val, title)


def bold(title):
    return "[B]%s[/B]" % title


def italics(title):
    return "[I]%s[/I]" % title

_color = color
_bold = bold
_italics = italics


# noinspection PyShadowingNames
def decorate(title, color=None, bold=False, italics=False):
    if color:
        title = _color(title, color)
    if bold:
        title = _bold(title)
    if italics:
        title = _italics(title)
    return title


def human_size(num, suffix='b'):
    for unit in ['', 'K', 'M', 'G', 'T', 'P', 'E', 'Z']:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, 'Y', suffix)


def human_duration(total_seconds):
    seconds = total_seconds % 60
    minutes = (total_seconds / 60) % 60
    hours = total_seconds / 3600
    if hours > 0:
        return "%d:%02d:%02d" % (hours, minutes, seconds)
    else:
        return "%02d:%02d" % (minutes, seconds)
