from django.template.defaultfilters import stringfilter
from django import template

from easymode.utils import languagecode

register = template.Library()

@register.filter
@stringfilter
def strip_locale(url):
    """Strip the language code from the beginning of a string"""
    return languagecode.strip_language_code(url)

@register.filter
def fix_locale_from_request(url, current_language):
    """
    Fixes the language code as follows:
    
    If there is only one language used in the site, it strips the language code.
    If there are more languages used, it will make sure that the url has the current
    language as a prefix.
    """
    return languagecode.fix_language_code(url, current_language)

@register.filter
@stringfilter
def fix_shorthand(language_code):
    """
    Use this if you want to use settings.USE_SHORT_LANGUAGE_CODES.
    fix_shorthand will always return the correct locale to use in an url,
    depending on your settings of USE_SHORT_LANGUAGE_CODES.
    """
    return languagecode.get_shorthand_from_language_code(language_code)


