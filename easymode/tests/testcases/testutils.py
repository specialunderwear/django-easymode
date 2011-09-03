import errno
import os
from hashlib import sha1
from os.path import join

from django.conf import settings
from django.test import TestCase

from easymode.utils import mutex, SemaphoreException, recursion_depth


__all__ = ('TestUtils',)

class TestUtils(TestCase):
    
    def test_semaphore(self):
        """the semaphore should bind a file to the context and hold on to it untill after the context is closed"""
        lockfile = join('/tmp', sha1(settings.SECRET_KEY).hexdigest() +'.semaphore')
        for a in range(1, 4):
            with mutex():
                assert(os.path.isfile(lockfile))
        
            assert(not os.path.exists(lockfile))

    def test_semaphore_exception(self):
        """The semaphore should throw an exception when the wait time is over"""
        lockfile = join('/tmp', sha1(settings.SECRET_KEY).hexdigest() +'.semaphore')
        try:
            with mutex(max_wait=0, lockfile=lockfile):
                with mutex(max_wait=0, lockfile=lockfile):
                    pass
        except SemaphoreException:
            pass
        else:
            self.fail('Should have triggered SemaphoreException')
        self.assertFalse(os.path.exists(lockfile))
        
    def test_fdopen_works_correctly(self):
        """fdopen should allow proper locking"""
        lockfile = join('/tmp', sha1(settings.SECRET_KEY).hexdigest() +'.semaphore')
        
        try:
            os.open(lockfile, os.O_EXCL | os.O_RDWR | os.O_CREAT)
            os.open(lockfile, os.O_EXCL | os.O_RDWR | os.O_CREAT)
        except OSError as e:
            self.assertEqual(e.errno, errno.EEXIST)
        else:
            self.fail("If the file exists an OSError should be thrown")
        finally:
            os.remove(lockfile)
    
    def test_recursion_depth(self):
        """recursion depth should work properly"""
        def recurse(arr):
            with recursion_depth('test_recursion_depth') as recursion_level:
                if recursion_level > 10:
                    raise Exception('error')
                if arr and arr.pop():
                    recurse(arr)

        recurse(range(0,10))
        self.assertRaises(Exception, recurse, range(0,11))
        recurse(range(0,10))
        self.assertRaises(Exception, recurse, range(0,11))
        
