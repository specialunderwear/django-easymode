"""
Contains utils for:

Matching first item in a list that matches some predicate.
Mutex
XML parser/generator that handles unknown entities.
Controlling recursion depth
"""
import errno
import os
import threading
import time
import urlparse
import urllib
from contextlib import contextmanager
from hashlib import sha1

from django.conf import settings


__all__ = (
    # members
    'recursion_depth', 'first_match', 'mutex',
    'SemaphoreException','bases_walker', 'url_add_params',

    # packages
    'languagecode', 'polibext', 'standin', 'template', 'xmlutils',
)

# the recursion level is counted globally and is just an approximation.
# usually if the limit is reached there is something wrong in your app.
# if not, try to set settings.RECURSION_LIMIT
RECURSION_LEVEL_DICT = threading.local()
@contextmanager
def recursion_depth(key):
    """
    A context manager used to guard recursion depth for some function.
    Multiple functions can be kept separately because it will be
    counted per key.
    
    Any exceptions raise in the recursive function will reset the counter,
    because the stack will be unwinded.

    usage::

        with recursion_depth('some_function_name') as recursion_level:
            if recursion_level > getattr(settings, 'RECURSION_LIMIT', sys.getrecursionlimit() / 10):
                raise Exception("Too deep")

            # do some recursive dangerous things.

    :param key: The key under which the recursion depth is kept.
    """
    try:
        if not getattr(RECURSION_LEVEL_DICT, 'key', False):
            RECURSION_LEVEL_DICT.key = 0
        RECURSION_LEVEL_DICT.key += 1
        yield RECURSION_LEVEL_DICT.key
        RECURSION_LEVEL_DICT.key -= 1
    except Exception as e:
        RECURSION_LEVEL_DICT.key = 0
        raise e
    
def first_match(predicate, list):
    """
    returns the first value of predicate applied to list, which
    does not return None
    
    >>> 
    >>> def return_if_even(x): 
    ...     if x % 2 is 0:
    ...         return x
    ...     return None
    >>> 
    >>> first_match(return_if_even, [1, 3, 4, 7])
    4
    >>> first_match(return_if_even, [1, 3, 5, 7])
    >>>
    
    :param predicate: a function that returns None or a value.
    :param list: A list of items that can serve as input to ``predicate``.
    :rtype: whatever ``predicate`` returns instead of None. (or None).
    """
    for item in list:
        val = predicate(item)
        if val is not None:
            return val
    
    return None

class SemaphoreException(Exception):
    """An exception that get thrown when an error occurs in the mutex semphore context"""

class mutex(object):
    """
    A semaphore Context Manager that uses a temporary file for locking.
    Only one thread or process can get a lock on the file at once.
    
    it can be used to mark a block of code as being executed exclusively
    by some thread. see `mutex <http://en.wikipedia.org/wiki/Mutual_exclusion>`_.
    
    usage::
        
        from __future__ import with_statement
        from easymode.utils import mutex
        
        with mutex:
            print "hi only one thread will be executing this block of code at a time."
    
    Mutex raises an :class:`easymode.utils.SemaphoreException` when it has to wait to
    long to obtain a lock or when it can not determine how long it was waiting.
    
    :param max_wait: The maximum amount of seconds the process should wait to obtain\
        the semaphore.
    :param lockfile: The path and name of the pid file used to create the semaphore.
    """
    
    def __init__(self, max_wait=None, lockfile=None):
        # the maximum reasonable time for aprocesstobe
        if max_wait is not None:
            self.max_wait = max_wait
        else:
            self.max_wait = 10
        
        # the location of the lock file
        self.lockfile = lockfile or os.path.join( "/tmp/", sha1(settings.SECRET_KEY).hexdigest() + '.semaphore')
    
    def __enter__(self):
        while True:
            try:
                # if the file exists you can not create it and get an exclusive lock on it
                # this is an atomic operation.
                file_descriptor = os.open(self.lockfile, os.O_EXCL | os.O_RDWR | os.O_CREAT)
                # we created the lockfile, so we're the owner
                break
            except OSError as e:
                if e.errno != errno.EEXIST:
                    # should not occur
                    raise e

            # if we got here the file exists so lets see
            # how long we are waiting for it
            try:
                # the lock file exists, try to stat it to get its age
                # and read it's contents to report the owner PID
                file_contents = open(self.lockfile, "r")
                file_last_modified = os.path.getmtime(self.lockfile)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise SemaphoreException("%s exists but stat() failed: %s" %                        
                        (self.lockfile, e.strerror)
                    )
                # we didn't create the lockfile, so it did exist, but it's
                # gone now. Just try again
                continue

            # we didn't create the lockfile and it's still there, check
            # its age
            if time.time() - file_last_modified > self.max_wait:
                pid = file_contents.read()
                raise SemaphoreException("%s has been locked for more than " \
                    "%d seconds by PID %s" % (self.lockfile, self.max_wait, pid))

            # it's not been locked too long, wait a while and retry
            file_contents.close()
            time.sleep(1)

        # if we get here. we have the lockfile. Convert the os.open file
        # descriptor into a Python file object and record our PID in it

        file_handle = os.fdopen(file_descriptor, "w")
        file_handle.write("%d" % os.getpid())
        file_handle.close()
    
    def __exit__(self, exc_type, exc_value, traceback):
        #Remove the lockfile, releasing the semaphore for other processes to obtain
        os.remove(self.lockfile)


def bases_walker(cls):
    """
    Loop through all bases of cls
            
    >>> str = u'hai'
    >>> for base in bases_walker(unicode):
    ...     isinstance(str, base)
    True
    True
    
    :param cls: The class in which we want to loop through the base classes.
    """
    for base in cls.__bases__:
        yield base
        for more in bases_walker(base):
            yield more

def url_add_params(url, **kwargs):
    """
    Add parameters to an url
    
    >>> url_add_params('http://example.com/', a=1, b=3)
    'http://example.com/?a=1&b=3'
    >>> url_add_params('http://example.com/?c=8', a=1, b=3)
    'http://example.com/?c=8&a=1&b=3'
    >>> url_add_params('http://example.com/#/irock', a=1, b=3)
    'http://example.com/?a=1&b=3#/irock'
    >>> url_add_params('http://example.com/?id=10#/irock', a=1, b=3)
    'http://example.com/?id=10&a=1&b=3#/irock'
    """
    parsed_url = urlparse.urlsplit(url)
    params = urlparse.parse_qsl(parsed_url.query)
    parsed_url = list(parsed_url)
    
    for pair in kwargs.iteritems():
        params.append(pair)
        
    parsed_url[3] = urllib.urlencode(params)
    return urlparse.urlunsplit(parsed_url)
