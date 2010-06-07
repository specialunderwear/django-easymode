"""
Lots of utility functions that can be used when
implementing a multi lingual django app.
"""
import re

from django.conf import settings
from django.utils.translation import get_language


USE_SHORT_LANGUAGE_CODES = getattr(settings, 'USE_SHORT_LANGUAGE_CODES', False)


def get_language_codes():
    """
    Retrieves all the language codes defined in ``settings.LANGUAGES``.
    
    >>> settings.LANGUAGES = (('en','English'),('de','German'),('nl-be','Belgium dutch'),('fr-be','Belgium french'),)
    >>> sorted( get_language_codes() )
    ['de', 'en', 'fr-be', 'nl-be']
    
    :rtype: A :class:`list` of language codes.
    """
    return dict(settings.LANGUAGES).keys()
    
def get_short_language_codes():
    """
    Retrieves the short versions of the language codes defined in settings.LANGUAGES.

    >>> from django.conf import settings
    >>> settings.LANGUAGES = (('en','English'),('de','German'),('nl-be','Belgium dutch'),('fr-be','Belgium french'),)
    >>> sorted( get_short_language_codes() )
    ['de', 'en', 'fr', 'nl']
    
    :rtype: A :class:`list` of short versions of the language codes.
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
    
    >>> from django.conf import settings
    >>> settings.MSGID_LANGUAGE = 'en-us'
    >>> settings.LANGUAGES = (('en','English'),('de','German'),('nl-be','Belgium dutch'),('fr-be','Belgium french'),)
    >>> sorted( get_language_codes() )
    ['en-us', 'en','de', 'nl-be','fr-be']
    
    :rtype: A :class:`list` of language codes.
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
    
    >>> USE_SHORT_LANGUAGE_CODES = True
    >>> get_shorthand_from_language_code('en-us')
    'en'
    >>> USE_SHORT_LANGUAGE_CODES = False
    >>> get_shorthand_from_language_code('en-us')
    'en-us'
    
    :param locale: The language code as a :class:`unicode` string.
    :rtype: The short version of the language code (when appropriate).
    """
    if USE_SHORT_LANGUAGE_CODES:
        return locale[:2]
        
    return locale

def get_language_code_from_shorthand(short_locale):
    """
    Returns the real language_code based on the shorthand.
    
    >>> settings.LANGUAGES = (('en-us','English'),('de','German'),('nl-be','Belgium dutch'),('fr-be','Belgium french'),)
    >>> get_language_code_from_shorthand('en')
    'en-us'
    
    :param short_locale: The short version of a language code.
    :rtype: The long version of the language code.
    """
    for locale in get_language_codes():
        if locale[:2] == short_locale:
            return locale
    return settings.LANGUAGE_CODE
    
def strip_language_code(url):
    """
    Strip the language code from the beginning of string

    >>> strip_language_code('http://example.com/en/example.html')
    'http://example.com/example.html'
    
    :param url: An url.
    :rtype: The ``url`` but the language code is removed.
    """
    return STRIP_LANGUAGE_CODE_REGEX.sub('/',url, 1)

def fix_language_code(url, current_language):
    """
    Fixes the language code as follows:
    
    If there is only one language used in the site, it strips the language code.
    If there are more languages used, it will make sure that the url has the current
    language as a prefix.
    
    >>> # multiple languages defined
    >>> settings.LANGUAGES = (('en-us','English'),('de','German'),('nl-be','Belgium dutch'),('fr-be','Belgium french'),)
    >>> settings.USE_SHORT_LANGUAGE_CODES = False
    >>> activate('en-us')
    >>> fix_language_code('/de/example.html', 'en-us')
    '/en-us/example.html'
    >>> settings.USE_SHORT_LANGUAGE_CODES = True
    >>> fix_language_code('/de/example.html', 'en-us')
    '/en/example.html'
    >>> fix_language_code('/en/example.html', 'en-us')
    '/example.html'
    >>> # only one language defined
    >>> settings.LANGUAGES = (('en-us', 'English'), )
    >>> fix_language_code('/en-us/example.html', 'en-us')
    '/example.html'
    
    :param url: The (absolute) url to be fixed eg. '/hi/how/is/it'.
    :param current_language: A language code defined in ``settings.LANGUAGES``.
    :rtype: The fixed url.
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
    
    If you want to do a query, using a localized field, you have
    to use the name this function returns, not the default name.
    
    >>> get_real_fieldname('name', 'en-us')
    'name_en-us'
    
    Usage::
    
        def index(request):
            published_in_language = get_real_fieldname('published', request.LANGUAGE_CODE)
            qs = SomeModel.objects.filter(**{published_in_language:True})
            return render_to_response('index.html', {'queryset':qs})
    
    
    :param field: The name of a field in an internationalised model.
    :param lang: The language for which you want to know the real name.
    :rtype: The actual name of the ``field`` in the ``lang``.
    """
    return str('%s_%s' % (field, lang))

def localize_fieldnames(fields, internationalized_fields):
    """
    Given a list of fields and a list of field names that
    are internationalized, will return a list with
    all internationalized fields properly localized.
    
    >>> from django.utils.translation import activate
    >>> activate('en-us')
    >>> localize_fieldnames(['name', 'title', 'url'], ['title'])
    ['name', 'title_en-us', 'url']
    
    :param fields: A :class:`list` af field names.
    :param internationalized_fields: A list of fields names, these fields are internationalized.
    :rtype: A list with the actual field names that are used in the current language.
    """
    result = []
    lang = get_language()    
    for field in fields:
        if field in internationalized_fields:
            result.append(get_real_fieldname(field, lang))
        else:
            result.append(field)    
    return result

def get_language_codes_as_disjunction():
    """
    return a pattern that matches any language defined in ``settings.LANGUAGES``
    
    >>> from django.conf import settings
    >>> settings.USE_SHORT_LANGUAGE_CODES = False
    >>> settings.LANGUAGES = (('en-us','English'),('de','German'),('nl-be','Belgium dutch'),('fr-be','Belgium french'),)
    >>> get_language_codes_as_disjunction()
    'de|en-us|nl-be|fr-be'
    
    usage::
        
        languages = get_language_codes_as_disjunction()
        urlpatterns = patterns('',
            url(r'^(%{languages})/admin/' % locals(), include(admin.site.urls), name="language-admin"),
        )
        
    """
    language_codes = map(get_shorthand_from_language_code, get_language_codes())
    languages = "|".join(language_codes)
    return languages
