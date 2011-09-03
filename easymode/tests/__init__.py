"""
Imports all testcases found in the 'testcases' subfolder of 
folder containg the file parameter.
Doing that is enough to make the testrunner find them.
"""
import glob
import os
import re
import sys

from django.conf import settings

from easymode.utils import first_match, bases_walker, url_add_params
from easymode.utils.languagecode import get_language_codes,\
    get_language_codes_as_disjunction, get_language_code_from_shorthand,\
    localize_fieldnames, get_real_fieldname, strip_language_code,\
    get_short_language_codes
from easymode.utils.standin import standin_for

# check if some required settings are fulfilled
if 'de' not in get_language_codes():
    raise Exception('the language "de" must be in your LANGUAGES to run the test suite')
if 'en-us' not in get_language_codes():
    raise Exception('the language "en-us" must be in your LANGUAGES to run the test suite')

if settings.LANGUAGE_CODE is not 'en':
    raise Exception('To run the test suite the LANGUAGE_CODE must be set to "en"')

# find all tests in the testcases folder
path = os.path.join(os.path.dirname(__file__), 'testcases')
pattern = os.path.join(path , r'(.+).py')

filenames = glob.glob(path + '/*.py')

if len(filenames): # delete __init__.py. yes it is always first.
    del(filenames[0])

# import all the testcases in the current scope
for filename in filenames:
    modulename = re.sub(pattern, r'\1', filename)
    try:
       testcase_module = __import__("easymode.tests.testcases.%s" % modulename, locals(), globals(), [''])
       test_class_names = getattr(testcase_module, '__all__')
       for test in testcase_module.__all__:
           setattr(sys.modules[__name__], test, getattr(testcase_module, test))
    except Exception, e:
       print "%s in %s, please correct if you want to run this test suite." % (e, modulename)


# doctests
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
    'test_url_add_params' : url_add_params,
}
