"""
Imports all testcases found in the 'testcases' subfolder of 
folder containg the file parameter.
Doing that is enough to make the testrunner find them.
"""

import glob
import re
import os

from django.conf import settings

from easymode.utils.languagecode import get_language_codes

if 'de' not in get_language_codes():
    raise Exception('the language "de" must be in your LANGUAGES to run the test suite')
if 'en-us' not in get_language_codes():
    raise Exception('the language "en-us" must be in your LANGUAGES to run the test suite')

if settings.LANGUAGE_CODE is not 'en':
    raise Exception('To run the test suite the LANGUAGE_CODE must be set to "en"')

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
from easymode.tests.testcases.testutils import *
from easymode.tests.testcases.testmiddleware import *

from easymode.utils import *
from easymode.utils.languagecode import *
from easymode.utils.standin import *

__test__ = {
    "test_get_language_codes" : get_language_codes,
    "test_get_short_language_codes" : get_short_language_codes,
    "test_get_language_code_from_shorthand" : get_language_code_from_shorthand,
    "test_strip_language_code" : strip_language_code,
    "test_get_real_fieldname" : get_real_fieldname,
    "test_localize_fieldnames" : localize_fieldnames,
    "test_get_language_codes_as_disjunction" : get_language_codes_as_disjunction,
    "test_first_match" : first_match,
    "test_bases_walker" : bases_walker,
    "test_standin_for": standin_for,
}
#for filename in filenames: # import testcases into current scoope
#    modulename = re.sub(pattern, r'\1', filename)
#    try:
#        exec("from easymode.tests.testcases.%s import *" % modulename)
#    except Exception, e:
#        print "%s in %s, please correct if you want to run this test suite." % (e, modulename)
