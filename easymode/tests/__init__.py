import glob
import re
import os

from django.conf import settings

"""
Imports all testcases found in the 'testcases' subfolder of 
folder containg the file parameter.
Doing that is enough to make the testrunner find them.

so 
>>> import_testcases("/tmp/stuff/tests.py")
will import all testcases in /tmp/stuff/testcases/
"""

path = os.path.join(os.path.dirname(__file__), 'testcases')
pattern = os.path.join(path , r'(.+).py')

filenames = glob.glob(path + '/*.py')

if len(filenames): #delete __init__.py. yes it is always first.
    del(filenames[0])

for filename in filenames: # import testcases into current scoope
    modulename = re.sub(pattern, r'\1', filename)
    try:
        exec("from easymode.tests.testcases.%s import *" % modulename)        
    except Exception, e:
        print "%s in %s, which doesn't matter you don't need the test cases to be imported" % (e, modulename)

