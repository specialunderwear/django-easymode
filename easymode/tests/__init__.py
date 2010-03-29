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

from easymode.tests.testcases.testdiocorefields import *
from easymode.tests.testcases.testeasypublisher import *
from easymode.tests.testcases.testi18n import *
from easymode.tests.testcases.testrelatedadmin import *
from easymode.tests.testcases.testtoxml import *
from easymode.tests.testcases.testxslt import *

from easymode.utils.languagecode import *
__test__ = {
    "test_get_language_codes" : get_language_codes,
    "test_get_short_language_codes" : get_short_language_codes,
    "test_get_language_code_from_shorthand" : get_language_code_from_shorthand,
    "test_strip_language_code" : strip_language_code,
    "test_get_real_fieldname" : get_real_fieldname,
    "test_localize_fieldnames" : localize_fieldnames,
    "get_language_codes_as_disjunction" : get_language_codes_as_disjunction,
}
#for filename in filenames: # import testcases into current scoope
#    modulename = re.sub(pattern, r'\1', filename)
#    try:
#        exec("from easymode.tests.testcases.%s import *" % modulename)
#    except Exception, e:
#        print "%s in %s, please correct if you want to run this test suite." % (e, modulename)
