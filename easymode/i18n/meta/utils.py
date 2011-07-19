"""
utility functions used by easymode's i18n.meta package to get localized attributes
from a class.
"""
from django.conf import settings
from django.utils import translation

from easymode.utils import first_match
from easymode.utils.languagecode import get_real_fieldname
from easymode.utils import first_match


def valid_for_gettext(value):
    """Gettext acts weird when empty string is passes, and passing none would be even weirder"""
    return value not in (None, "")
    
def get_fallback_languages():
    """Retrieve the fallback languages from the settings.py"""
    lang = translation.get_language()
    fallback_list = settings.FALLBACK_LANGUAGES.get(lang, None)
    if fallback_list:
        return fallback_list

    return settings.FALLBACK_LANGUAGES.get(lang[:2], [])


def get_localized_property(context, field=None, language=None):
    '''
    When accessing to the name of the field itself, the value
    in the current language will be returned. Unless it's set,
    the value in the default language will be returned.
    '''
    if language:
        return getattr(context, get_real_fieldname(field, language))
    
    if hasattr(settings, 'FALLBACK_LANGUAGES'):
        attrs = [translation.get_language()]
        attrs += get_fallback_languages()
    else:
        attrs = [
            translation.get_language(),
            translation.get_language()[:2],
            settings.LANGUAGE_CODE, 
        ]
    
    def predicate(x):
        value = getattr(context, get_real_fieldname(field, x), None)
        return value if valid_for_gettext(value) else None

    return first_match(predicate, attrs)


def get_localized_field_name(context, field):
    """Get the name of the localized field"""
    attrs = [
             translation.get_language(), 
             translation.get_language()[:2], 
             settings.LANGUAGE_CODE
            ]
            
    def predicate(x):
        field_name = get_real_fieldname(field, x)
        if hasattr(context, field_name):
            return field_name
        return None

    return first_match(predicate, attrs)

def get_field_from_model_by_name(model_class, field_name):
    """
    Get a field by name from a model class without messing with the app cache.
    """
    return first_match(lambda x: x if x.name == field_name else None, model_class._meta.fields)
