import re

from django.conf import settings
from django.utils.translation import get_language

USE_SHORT_LANGUAGE_CODES = getattr(settings, 'USE_SHORT_LANGUAGE_CODES', False)


def get_language_codes():
    """return the language codes from the settings"""
    return dict(settings.LANGUAGES).keys()

def get_short_language_codes():
    """
    Returns the short versions of the language codes defined in settings.LANGUAGES
    """
    languages = set([lang[:2] for lang in get_language_codes()])
    return list(languages)

# define regular expressions. they are different, depending on whether we are using full language
# codes, eg 'en-us' or we want to show the abbreviated versions in the url, eg. 'en'
if USE_SHORT_LANGUAGE_CODES:
    STRIP_LANGUAGE_CODE_REGEX = re.compile(ur'/(?:%s)/' % "|".join(get_short_language_codes()))
else:
    STRIP_LANGUAGE_CODE_REGEX = re.compile(ur'/(?:%s)/' % "|".join(get_language_codes()))

def get_all_language_codes():
    """
    Returns all language codes defined in settings.LANGUAGES and also the
    settings.MSGID_LANGUAGE if defined.
    """
    languages = get_language_codes()
    if hasattr(settings, 'MSGID_LANGUAGE'):
        if not settings.MSGID_LANGUAGE in languages:
            languages.insert(0, settings.MSGID_LANGUAGE)
            
    return languages

def get_shorthand_from_language_code(locale):
    """
    Returns the shorthand, based on the language code.
    
    If USE_SHORT_LANGUAGE_CODES is true it will return a
    ahorthand, if it is False, it will not modify the code
    at all.
    """
    if USE_SHORT_LANGUAGE_CODES:
        return locale[:2]
        
    return locale

def get_language_code_from_shorthand(short_locale):
    """
    Returns the real language_code based on the shorthand
    """
    for locale in get_language_codes():
        if locale[:2] == short_locale:
            return locale
    return settings.LANGUAGE_CODE
    
def strip_language_code(url):
    """Strip the language code from the beginning of string"""
    return STRIP_LANGUAGE_CODE_REGEX.sub('/',url, 1)

def fix_language_code(url, current_language):
    """
    Fixes the language code as follows:
    
    If there is only one language used in the site, it strips the language code.
    If there are more languages used, it will make sure that the url has the current
    language as a prefix.
    """
    stripped_url = strip_language_code(url)
    if not getattr(settings, 'MASTER_SITE', False) and len(settings.LANGUAGES) == 1:
        # no MASTER_SITE and only one language, do not add language code to url
        return stripped_url
    
    # add the language code to the url        
    return u"/%s%s" % (get_shorthand_from_language_code(current_language), stripped_url)

def get_real_fieldname(field, lang):
    """
    Depending on the language a field can have a different name.
    """
    return '%s_%s' % (field, lang)

def localize_fieldnames(fields, internationalized_fields):
    """
    Given a list of fields and a list of field names that
    are be internationalized, will return a list with
    all internationalized fields properly localized.
    """
    result = []
    lang = get_language()    
    for field in fields:
        if field in internationalized_fields:
            result.append(get_real_fieldname(field, lang))
        else:
            result.append(field)    
    return result