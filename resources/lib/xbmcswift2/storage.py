"""
    xbmcswift2.storage
    ~~~~~~~~~~~~~~~~~~

    This module contains persistent storage classes.

    :copyright: (c) 2012 by Jonathan Beluch
    :license: GPLv3, see LICENSE for more details.
"""
import sys
import sqlite3
import copy
import time
import os

from datetime import datetime, timedelta
from xbmcswift2.common import encode_fs
from xbmcswift2.logger import log
from UserDict import DictMixin

try:
    from cPickle import dumps, loads
except ImportError:
    from pickle import dumps, loads


def encode(obj):
    """Serialize an object using pickle to a binary format accepted by SQLite."""
    return sqlite3.Binary(dumps(obj))


def decode(obj):
    """Deserialize objects retrieved from SQLite."""
    return loads(bytes(obj))


class Storage(DictMixin):
    """A dict with the ability to persist to disk and TTL for items."""

    CREATE_TABLE = 'CREATE TABLE IF NOT EXISTS %s (key TEXT PRIMARY KEY, value BLOB, expire DATETIME)'
    CREATE_INDEX = 'CREATE INDEX IF NOT EXISTS expire ON %s (expire)'
    GET_LEN = 'SELECT COUNT(*) FROM %s WHERE (expire IS NULL OR expire >= DATETIME("NOW"))'
    GET_MAX = 'SELECT MAX(ROWID) FROM %s WHERE (expire IS NULL OR expire >= DATETIME("NOW"))'
    GET_KEYS = 'SELECT key FROM %s WHERE (expire IS NULL OR expire >= DATETIME("NOW")) ORDER BY rowid'
    GET_VALUES = 'SELECT value FROM %s WHERE (expire IS NULL OR expire >= DATETIME("NOW")) ORDER BY rowid'
    GET_ITEMS = 'SELECT key, value, expire FROM %s WHERE (expire IS NULL OR expire >= DATETIME("NOW")) ORDER BY rowid '
    HAS_ITEM = 'SELECT 1 FROM %s WHERE key = ? AND (expire IS NULL OR expire >= DATETIME("NOW"))'
    GET_ITEM = 'SELECT value, expire FROM %s WHERE key = ? AND (expire IS NULL OR expire >= DATETIME("NOW"))'
    ADD_ITEM_NO_TTL = 'REPLACE INTO %s (key, value, expire) VALUES (?, ?, NULL)'
    ADD_ITEM_TTL = 'REPLACE INTO %s (key, value, expire) VALUES (?, ?, DATETIME("NOW", "+%d SECONDS"))'
    SET_ITEM_TTL = 'UPDATE %s SET expire=DATETIME("NOW", "+%d SECONDS") WHERE key = ?'
    SET_ITEM_NO_TTL = 'UPDATE %s SET expire=NULL WHERE key = ?'
    DEL_ITEM = 'DELETE FROM %s WHERE key = ?'
    CLEAR_ALL = 'DELETE FROM %s'
    PURGE_ALL = 'DELETE FROM %s WHERE expire < DATETIME("NOW")'

    def __init__(self, filename, tablename="unnamed", flag="c", ttl=None, autocommit=True, cached=False,
                 autopurge=False, autorecover=True):
        """
        Initialize a thread-safe sqlite-backed dictionary. The dictionary will
        be a table `tablename` in database file `filename`. A single file (=database)
        may contain multiple tables.
        If no `filename` is given, a random file in temp will be used (and deleted
        from temp once the dict is closed/deleted).
        If you enable `autocommit`, changes will be committed after each operation
        (more inefficient but safer). Otherwise, changes are committed on `self.commit()`,
        `self.clear()` and `self.close()`.
        Set `journal_mode` to 'OFF' if you're experiencing sqlite I/O problems
        or if you need performance and don't care about crash-consistency.
        The `flag` parameter:
          'c': default mode, open for read/write, creating the db/table if necessary.
          'w': open for r/w, but drop `tablename` contents first (start with empty table)
          'n': create a new database (erasing any existing tables, not just `tablename`!).

        TTL if provided should be in seconds.
        """
        self.ttl = ttl
        self.filename = filename
        self.autopurge = autopurge
        self.flag = flag
        self.tablename = tablename
        self.autocommit = autocommit
        self.cached = cached
        self.autorecover = autorecover
        self.original = {}
        self.cache = {}
        self.expire_cache = {}
        self.conn = None

    def _connect(self):
        log.debug("Opening Sqlite table %r in %s" % (self.tablename, self.filename))
        filename = encode_fs(self.filename)
        if self.flag == 'n':
            if os.path.exists(filename):
                os.remove(filename)
        dirname = os.path.dirname(filename)
        if dirname and not os.path.exists(dirname):
            raise RuntimeError('Error! The directory does not exist, %s' % self.filename)

        if self.autocommit:
            self.conn = sqlite3.connect(self.filename, isolation_level=None)
        else:
            self.conn = sqlite3.connect(self.filename)
        try:
            self._execute(self.CREATE_TABLE % self.tablename)
            self._execute(self.CREATE_INDEX % self.tablename)
            if self.flag == 'w':
                self.clear()
            elif self.autopurge and self.ttl:
                self.purge()
            elif self.cached:
                self._load()
        except sqlite3.DatabaseError:
            self.close()
            raise

    def _load(self):
        sql = self.GET_ITEMS % self.tablename
        c = self._execute(sql)
        self.cache = {}
        self.expire_cache = {}
        for key, value, expire in c:
            # noinspection PyBroadException
            try:
                k = decode(key)
                value = decode(value)
                self.cache[k] = value
                self.expire_cache[k] = self._datetime(expire)
            except:
                if self.autorecover:
                    self.__delkey(key)
                else:
                    raise
        self.original = copy.deepcopy(self.cache)

    def _execute(self, sql, params=()):
        if not self.conn:
            self._connect()
        c = self.conn.cursor()
        # if params:
        #     log.info("%s ? %s", sql, params)
        # else:
        #     log.info(sql)
        c.execute(sql, params)
        return c

    def __enter__(self):
        return self

    # noinspection PyUnusedLocal
    def __exit__(self, *exc_info):
        self.close()

    def __str__(self):
        return "Storage(%s)" % self.filename

    def __repr__(self):
        return str(self)  # no need of something complex

    def __len__(self):
        # `select count (*)` is super slow in sqlite (does a linear scan!!)
        # As a result, len() is very slow too once the table size grows beyond trivial.
        # We could keep the total count of rows ourselves, by means of triggers,
        # but that seems too complicated and would slow down normal operation
        # (insert/delete etc).
        if self.cached:
            if not self.conn:
                self._connect()
            return len(self.cache)
        else:
            sql = self.GET_LEN % self.tablename
            c = self._execute(sql)
            rows = c.fetchone()
            return rows[0] if rows is not None else 0

    def __delkey(self, key):
        sql = self.DEL_ITEM % self.tablename
        self._execute(sql, (key,))

    def __nonzero__(self):
        if self.cached:
            if not self.conn:
                self._connect()
            return bool(self.cache)
        else:
            # No elements is False, otherwise True
            sql = self.GET_MAX % self.tablename
            c = self._execute(sql)
            m = c.fetchone()[0]
            # Explicit better than implicit and bla bla
            return True if m is not None else False

    def keys(self):
        if self.cached:
            if not self.conn:
                self._connect()
            return self.cache.keys()
        else:
            sql = self.GET_KEYS % self.tablename
            c = self._execute(sql)
            keys = []
            for key in c:
                # noinspection PyBroadException
                try:
                    keys.append(decode(key[0]))
                except:
                    if self.autorecover:
                        self.__delkey(key[0])
                    else:
                        raise
            return keys

    def values(self):
        if self.cached:
            if not self.conn:
                self._connect()
            return self.cache.values()
        else:
            sql = self.GET_ITEMS % self.tablename
            c = self._execute(sql)
            values = []
            for key, value, expire in c:
                # noinspection PyBroadException
                try:
                    values.append(decode(value))
                except:
                    if self.autorecover:
                        self.__delkey(key)
                    else:
                        raise
            return values

    def items(self):
        if self.cached:
            if not self.conn:
                self._connect()
            return self.cache.items()
        else:
            sql = self.GET_ITEMS % self.tablename
            c = self._execute(sql)
            res = []
            self.expire_cache = {}
            for key, value, expire in c:
                # noinspection PyBroadException
                try:
                    k = decode(key)
                    res.append((k, decode(value)))
                    self.expire_cache[k] = self._datetime(expire)
                except:
                    if self.autorecover:
                        self.__delkey(key)
                    else:
                        raise
            return res

    def iterkeys(self):
        for k in self.keys():
            yield k

    def itervalues(self):
        for v in self.values():
            yield v

    def iteritems(self):
        for kv in self.items():
            yield kv

    def __contains__(self, key):
        if not self.conn:
            self._connect()
        if key in self.cache:
            return self.cache[key]
        elif self.cached:
            return False
        else:
            sql = self.HAS_ITEM % self.tablename
            c = self._execute(sql, (encode(key),))
            return c.fetchone() is not None

    def __getitem__(self, key):
        if not self.conn:
            self._connect()
        if key in self.cache:
            return self.cache[key]
        elif self.cached:
            raise KeyError(key)
        else:
            sql = self.GET_ITEM % self.tablename
            c = self._execute(sql, (encode(key),))
            item = c.fetchone()
            if item is None:
                raise KeyError(key)
            # noinspection PyBroadException
            try:
                res = decode(item[0])
            except:
                if self.autorecover:
                    res = None
                else:
                    raise
            if self.cached:
                self.cache[key] = res
            self.expire_cache[key] = self._datetime(item[1])
            return res

    @staticmethod
    def _datetime(s):
        if s is None:
            return None
        else:
            return datetime(*(time.strptime(s, '%Y-%m-%d %H:%M:%S')[0:6]))

    def __setitem__(self, key, value):
        self.set(key, value)

    def _get_expire_datetime(self, ttl=False):
        if ttl is False:
            ttl = self.ttl
        if ttl is None:
            return None
        else:
            return datetime.utcnow() + timedelta(seconds=ttl)

    def __delitem__(self, key):
        if not self.conn:
            self._connect()
        if key in self.expire_cache:
            del self.expire_cache[key]
        if key in self.cache:
            del self.cache[key]
        elif key not in self:
            raise KeyError(key)
        self.__delkey(encode(key))

    def update(self, items=None, **kwds):
        if not self.conn:
            self._connect()
        items = items or {}
        if self.cached:
            self.cache.update(items)
        else:
            pairs = []
            try:
                pairs = [(encode(k), encode(v)) for k, v in items.items()]
            except AttributeError:
                pass

            if self.ttl:
                sql = self.ADD_ITEM_TTL % (self.tablename, self.ttl)
            else:
                sql = self.ADD_ITEM_NO_TTL % self.tablename
            # log.info("%s (%s)", sql, pairs)
            self.conn.executemany(sql, pairs)
        for k in items.keys():
            self.expire_cache[k] = self._get_expire_datetime()
        if kwds:
            self.update(kwds)

    def get_expire(self, key):
        if key not in self.expire_cache:
            self.__getitem__(key)
        return self.expire_cache[key]

    def set(self, key, value, ttl=None):
        if not self.conn:
            self._connect()
        if self.cached:
            self.cache[key] = value
        else:
            ttl = ttl or self.ttl
            if ttl:
                sql = self.ADD_ITEM_TTL % (self.tablename, ttl)
            else:
                sql = self.ADD_ITEM_NO_TTL % self.tablename
            self._execute(sql, (encode(key), encode(value)))
        self.expire_cache[key] = self._get_expire_datetime()

    def setdefault(self, key, default=None, ttl=None):
        try:
            return self[key]
        except KeyError:
            self.set(key, default, ttl)
        return default

    def set_ttl(self, key, ttl):
        if ttl is None:
            sql = self.SET_ITEM_NO_TTL % self.tablename
        else:
            sql = self.SET_ITEM_TTL % (self.tablename, ttl)
        if self._execute(sql, (encode(key),)).rowcount:
            self.expire_cache[key] = self._get_expire_datetime(ttl)
        else:
            raise KeyError(key)

    def protect(self, key):
        self.set_ttl(key, None)

    def unprotect(self, key):
        self.set_ttl(key, self.ttl)

    def __iter__(self):
        return iter(self.keys())

    def clear(self):
        # avoid VACUUM, as it gives "OperationalError: database schema has changed"
        sql = self.CLEAR_ALL % self.tablename
        self._execute(sql)
        self.cache = {}
        self.expire_cache = {}

    def purge(self):
        sql = self.PURGE_ALL % self.tablename
        self._execute(sql)
        if self.cached:
            self._load()
        else:
            self.cache = {}
            self.expire_cache = {}

    def commit(self):
        if self.cached and self.cache:
            self.cached = False
            upd_dict = dict((k, v) for k, v in self.cache.iteritems()
                            if k not in self.original or not self.original[k] == v)
            if upd_dict:
                log.debug("Updated storage keys: %s" % ", ".join(upd_dict.keys()))
                self.update(upd_dict)
            self.original = copy.deepcopy(self.cache)
            self.cached = True
        if self.conn:
            self.conn.commit()
    sync = commit

    def close(self):
        log.debug("Closing %s" % self)
        if self.conn:
            if self.autocommit:
                self.commit()
            self.conn.close()
            self.conn = None

    def terminate(self):
        """Delete the underlying database file. Use with care."""
        self.close()

        if self.filename == ':memory:':
            return

        log.info("Deleting %s" % self.filename)
        try:
            os.remove(self.filename)
        except IOError:
            _, e, _ = sys.exc_info()  # python 2.5: "Exception as e"
            log.warning("Failed to delete %s: %s" % (self.filename, str(e)))

    def __del__(self):
        # like close(), but assume globals are gone by now (such as the logger)
        # noinspection PyBroadException
        try:
            if self.conn is not None:
                if self.autocommit:
                    self.commit()
                self.conn.close()
                self.conn = None
        except:
            pass
