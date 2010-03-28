"""
Contains utils for:

Matching first item in a list that matches some predicate.
Mutex
XML parser/generator that handles unknown entities.

"""
import os
import errno
import sys
import time
import stat

from hashlib import sha1

from django.conf import settings

    
def first_match(predicate, list):
    """
    returns the first value of predicate applied to list, which
    does not return None
    
    >>> def return_if_even(x):
    >>>     if x % 2 is 0:
    >>>         return x
    >>>     return None
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
    
    Mutex should probably raise an ``Exception`` instead of ``sys.exit``
    
    :param max_wait: The maximum amount of seconds the process should wait to obtain\
        the semaphore.
    :param lockfile: The path and name of the pid file used to create the semaphore.
    """
    
    def __init__(self, max_wait=10, lockfile=None):
        # the maximum reasonable time for aprocesstobe    
        self.max_wait=10
        # the location of the lock file
        self.lockfile = lockfile or os.path.join( "/tmp/", sha1(settings.SECRET_KEY).hexdigest() + '.semaphore')
    
    def __enter__(self):
        while True:
            try:
                # if the file exists you can not create it and get an exclusive lock on it
                fd = os.open(self.lockfile, os.O_EXCL | os.O_RDWR | os.O_CREAT)
                # we created the lockfile, so we're the owner
                break
            except OSError, e:
                if e.errno != errno.EEXIST:
                    # should not occur
                    raise

            # if we got here the file exists so lets see
            # how long we are waiting for it
            try:
                # the lock file exists, try to stat it to get its age
                # and read it's contents to report the owner PID
                f = open(self.lockfile, "r")
                s = os.stat(self.lockfile)
            except OSError, e:
                if e.errno != errno.EEXIST:
                    sys.exit("%s exists but stat() failed: %s" %
                        (self.lockfile, e.strerror))
                # we didn't create the lockfile, so it did exist, but it's
                # gone now. Just try again
                continue

            # we didn't create the lockfile and it's still there, check
            # its age
            now = int(time.time())
            if now - s[stat.ST_MTIME] > self.max_wait:
                pid = f.readline()
                sys.exit("%s has been locked for more than " \
                    "%d seconds (PID %s)" % (self.lockfile, self.max_wait, pid))

            # it's not been locked too long, wait a while and retry
            f.close()
            time.sleep(1)

        # if we get here. we have the lockfile. Convert the os.open file
        # descriptor into a Python file object and record our PID in it

        f = os.fdopen(fd, "w")
        f.write("%d\n" % os.getpid())
        f.close()
    
    def __exit__(self, exc_type, exc_value, traceback):
        """docstring for __exit__"""
        os.remove(self.lockfile)
        
