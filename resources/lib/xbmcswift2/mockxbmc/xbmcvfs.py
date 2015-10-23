# @package xbmcvfs
# Classes and functions to work with files and folders.
#

import os
import shutil
from xbmcswift2.common import encode_fs
from xbmcswift2.logger import log


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class File(object):
    def __init__(self, filename, type=None):
        """
        'w' - opt open for write
        example:
         f = xbmcvfs.File(file, ['w'])
        """
        pass

    def close(self):
        """
        example:
         f = xbmcvfs.File(file)
         f.close()
        """
        pass

    def read(self, bytes=None):
        """
        bytes : how many bytes to read [opt]- if not set it will read the whole file
        example:
        f = xbmcvfs.File(file)
        b = f.read()
        f.close()
        """
        pass

    def readBytes(self, numbytes):
        """
        readBytes(numbytes)

        numbytes : how many bytes to read [opt]- if not set it will read the whole file

        returns: bytearray

        example:
        f = xbmcvfs.File(file)
        b = f.read()
        f.close()
        """
        return bytearray()

    def seek(self):
        """
        FilePosition : position in the file
        Whence : where in a file to seek from[0 begining, 1 current , 2 end possition]
        example:
         f = xbmcvfs.File(file)
         result = f.seek(8129, 0)
         f.close()
        """
        pass

    def size(self):
        """
        example:
         f = xbmcvfs.File(file)
         s = f.size()
         f.close()
        """
        return 0

    def write(self, buffer):
        """
        buffer : buffer to write to file
        example:
         f = xbmcvfs.File(file, 'w', True)
         result = f.write(buffer)
         f.close()
        """
        pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming,PyBroadException
def copy(source, destination):
    """Copy file to destination, returns true/false.

    source: string - file to copy.
    destination: string - destination file

    Example:
        success = xbmcvfs.copy(source, destination)"""
    try:
        shutil.copy(encode_fs(source), encode_fs(destination))
        return True
    except:
        log.warning("Can't copy %s to %s", file, destination, exc_info=True)
        return False


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming,PyBroadException
def delete(file):
    """Deletes a file.

    file: string - file to delete

    Example:
        xbmcvfs.delete(file)"""
    try:
        os.remove(encode_fs(file))
        return True
    except:
        log.warning("Can't remove %s", file, exc_info=True)
        return False


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
def rename(file, newFileName):
    """Renames a file, returns true/false.

    file: string - file to rename
    newFileName: string - new filename, including the full path

    Example:
        success = xbmcvfs.rename(file,newFileName)"""
    return True


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming,PyBroadException
def mkdir(path):
    """Create a folder.

    path: folder

    Example:
        success = xbmcfvs.mkdir(path)
    """
    try:
        os.mkdir(encode_fs(path))
        return True
    except:
        log.warning("Can't mkdir %s", path, exc_info=True)
        return False


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming,PyBroadException
def mkdirs(path):
    """
    mkdirs(path)--Create folder(s) - it will create all folders in the path.

    path : folder

    example:

    - success = xbmcvfs.mkdirs(path)
    """
    try:
        os.makedirs(encode_fs(path))
        return True
    except:
        log.warning("Can't makedirs %s", path, exc_info=True)
        return False


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming,PyBroadException
def rmdir(path):
    """Remove a folder.

    path: folder

    Example:
        success = xbmcfvs.rmdir(path)
    """
    try:
        os.rmdir(encode_fs(path))
        return True
    except:
        log.warning("Can't rmdir %s", path, exc_info=True)
        return False


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming,PyBroadException
def exists(path):
    """Checks for a file or folder existance, mimics Pythons os.path.exists()

    path: string - file or folder

    Example:
        success = xbmcvfs.exists(path)"""
    try:
        return os.path.exists(encode_fs(path))
    except:
        return False


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
def listdir(path):
    """
    listdir(path) -- lists content of a folder.

    path        : folder

    example:
     - dirs, files = xbmcvfs.listdir(path)
    """
    pass


# noinspection PyUnusedLocal,PyMethodMayBeStatic,PyShadowingBuiltins,PyPep8Naming
class Stat(object):
    def __init__(self, path):
        """
        Stat(path) -- get file or file system status.

        path        : file or folder

        example:
        - print xbmcvfs.Stat(path).st_mtime()
        """

    def st_mode(self):
        return None

    def st_ino(self):
        return None

    def st_nlink(self):
        return None

    def st_uid(self):
        return None

    def st_gid(self):
        return None

    def st_size(self):
        return None

    def st_atime(self):
        return None

    def st_mtime(self):
        return None

    def st_ctime(self):
        return None
