"""
    xbmcswift2.common
    -----------------

    This module contains some common helpful functions.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
"""
import os
import sys
import time
import urllib
import urllib2
import unicodedata

from xbmcswift2 import CLI_MODE

try:
    # noinspection PyPep8Naming
    import cPickle as pickle
except ImportError:
    import pickle


def xbmc_url(url, **options):
    """Appends key/val pairs to the end of a URL. Useful for passing arbitrary
    HTTP headers to XBMC to be used when fetching a media resource, e.g.
    cookies.
    """
    optionstring = urllib.urlencode(options)
    if optionstring:
        return url + '|' + optionstring
    return url


# noinspection PyProtectedMember
def enum(*args, **kwargs):
    """An enum class to mirror XBMC constatns. All args and kwargs.keys are
    added as atrrs on the returned object.

    >>> States = enum('NEW_JERSEY', NY='NEW_YORK')
    >>> States.NY
    'NEW_YORK'
    >>> States.NEW_JERSEY
    'NEW_JERSEY'
    >>> States._fields
    ['NY', 'NEW_JERSEY']
    """
    kwargs.update((arg, arg) for arg in args)
    kwargs['_fields'] = kwargs.keys()
    return type('Enum', (), kwargs)


Modes = enum('XBMC', 'ONCE', 'CRAWL', 'INTERACTIVE')
# noinspection PyUnresolvedReferences
DEBUG_MODES = [Modes.ONCE, Modes.CRAWL, Modes.INTERACTIVE]


def clean_dict(dct):
    """Returns a dict where items with a None value are removed"""
    return dict((key, val) for key, val in dct.items() if val is not None)


def pickle_args(items):
    ret = {}
    pickled_keys = []
    for key, val in items.items():
        if isinstance(val, basestring):
            ret[key] = val
        else:
            try:
                len(val)
            except TypeError:
                val = [val]
            res = []
            for v in val:
                if isinstance(v, basestring):
                    res.append(v)
                else:
                    if key not in pickled_keys:
                        pickled_keys.append(key)
                    res.append(pickle.dumps(v))
            ret[key] = res
    if pickled_keys:
        ret['_pickled'] = ','.join(pickled_keys)
    return ret


def pickle_dict(items):
    """Returns a new dictionary where values which aren't instances of
    basestring are pickled. Also, a new key '_pickled' contains a comma
    separated list of keys corresponding to the pickled values.
    """
    ret = {}
    pickled_keys = []
    for key, val in items.items():
        if isinstance(val, basestring):
            ret[key] = val
        else:
            pickled_keys.append(key)
            ret[key] = pickle.dumps(val)
    if pickled_keys:
        ret['_pickled'] = ','.join(pickled_keys)
    return ret


def unpickle_args(items):
    """Takes a dict and unpickles values whose keys are found in
    '_pickled' key.

    >>> unpickle_args({'_pickled': ['foo']. 'foo': ['I3%0A.']})
    {'foo': 3}
    """
    # Technically there can be more than one _pickled value. At this point
    # we'll just use the first one
    pickled = items.pop('_pickled', None)
    if pickled is None:
        return items

    pickled_keys = pickled[0].split(',')
    ret = {}
    for key, vals in items.items():
        if key in pickled_keys:
            ret[key] = [pickle.loads(val) for val in vals]
        else:
            ret[key] = vals
    return ret


def unpickle_dict(items):
    """Returns a dict pickled with pickle_dict"""
    pickled_keys = items.pop('_pickled', '').split(',')
    ret = {}
    for key, val in items.items():
        if key in pickled_keys:
            ret[key] = pickle.loads(val)
        else:
            ret[key] = val
    return ret


def download_page(url, data=None):
    """Returns the response for the given url. The optional data argument is
    passed directly to urlopen."""
    conn = urllib2.urlopen(url, data)
    resp = conn.read()
    conn.close()
    return resp


_hextochr = dict(('%02x' % i, chr(i)) for i in range(256))
_hextochr.update(('%02X' % i, chr(i)) for i in range(256))


def unhex(inp):
    """unquote(r'abc\x20def') -> 'abc def'."""
    res = inp.split(r'\x')
    for i in xrange(1, len(res)):
        item = res[i]
        try:
            res[i] = _hextochr[item[:2]] + item[2:]
        except KeyError:
            res[i] = '%' + item
        except UnicodeDecodeError:
            res[i] = unichr(int(item[:2], 16)) + item[2:]
    return ''.join(res)


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
    return sys.getfilesystemencoding() if os.name == 'nt' else 'utf-8'


def decode_fs(string):
    res = unicode(string, get_filesystem_encoding(), errors)
    res = unicodedata.normalize('NFC', res)
    return res

def encode_fs(string):
    string = ensure_unicode(string)
    return string.encode(get_filesystem_encoding())


def direxists(path):
    import os
    from xbmcswift2 import xbmcvfs
    if not path.endswith("/") and not path.endswith("\\"):
        path += os.sep
    return xbmcvfs.exists(path)


def filter_dict(d):
    return dict((data for data in d.iteritems() if data[1] is not None))


def abort_requested():
    from xbmcswift2 import xbmc
    if CLI_MODE:
        return False
    else:
        return xbmc.abortRequested


def sleep(ms):
    from xbmcswift2 import xbmc
    if CLI_MODE:
        time.sleep(ms / 1000.0)
    else:
        xbmc.sleep(ms)


def file_size(path):
    from xbmcswift2 import xbmcvfs
    return xbmcvfs.Stat(path).st_size()


def dirwalk(top, topdown=True):
    from xbmcswift2 import xbmcvfs
    dirs, nondirs = xbmcvfs.listdir(top)
    dirs = [ensure_unicode(d) for d in dirs]
    nondirs = [ensure_unicode(d) for d in nondirs]

    if topdown:
        yield top, dirs, nondirs
    for name in dirs:
        new_path = join_path(top, name)
        for x in dirwalk(new_path, topdown):
            yield x
    if not topdown:
        yield top, dirs, nondirs


def get_dir_size(directory):
    dir_size = 0
    for (path, dirs, files) in dirwalk(directory):
        for f in files:
            filename = join_path(path, f)
            dir_size += file_size(filename)
    return dir_size


def get_free_space(folder):
    """ Return folder/drive free space (in bytes)
    """
    import platform
    import ctypes
    if platform.system() == 'Windows':
        free_bytes = ctypes.c_ulonglong(0)
        ctypes.windll.kernel32.GetDiskFreeSpaceExW(ctypes.c_wchar_p(folder), None, None, ctypes.pointer(free_bytes))
        return free_bytes.value / 1024 / 1024
    else:
        st = os.statvfs(folder)
        return st.f_bavail * st.f_frsize / 1024 / 1024


def join_path(a, *p):
    """Join two or more pathname components, inserting "\\" as needed.
    If any component is an absolute path, all previous path components
    will be discarded.

    :type p: list[string]
    """
    path = a
    for b in p:
        b_wins = 0  # set to 1 iff b makes path irrelevant
        if path == "":
            b_wins = 1

        elif os.path.isabs(b):
            # This probably wipes out path so far.  However, it's more
            # complicated if path begins with a drive letter:
            #     1. join('c:', '/a') == 'c:/a'
            #     2. join('c:/', '/a') == 'c:/a'
            # But
            #     3. join('c:/a', '/b') == '/b'
            #     4. join('c:', 'd:/') = 'd:/'
            #     5. join('c:/', 'd:/') = 'd:/'
            if path[1:2] != ":" or b[1:2] == ":":
                # Path doesn't start with a drive letter, or cases 4 and 5.
                b_wins = 1

            # Else path has a drive letter, and b doesn't but is absolute.
            elif len(path) > 3 or (len(path) == 3 and
                                   path[-1] not in "/\\"):
                # case 3
                b_wins = 1

        if b_wins:
            path = b
        else:
            # Join, and ensure there's a separator.
            assert len(path) > 0
            if path[-1] in "/\\":
                if b and b[0] in "/\\":
                    path += b[1:]
                else:
                    path += b
            elif path[-1] == ":":
                path += b
            elif b:
                if b[0] in "/\\":
                    path += b
                else:
                    path += "/" + b
            else:
                # path is not empty and does not end with a backslash,
                # but b is empty; since, e.g., split('a/') produces
                # ('a', ''), it's best if join() adds a backslash in
                # this case.
                path += '/'

    return path
