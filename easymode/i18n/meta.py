"""
Derived from django-transmeta.
Contains machinery to change a type after construction,
by using a class decorator.

This in contrast with django-transmeta which requires
overriding the __metaclass__.
"""
import copy

from django.conf import settings
from django.db.models.fields import NOT_PROVIDED
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.utils import translation
from django.utils.encoding import force_unicode
from django.utils.translation.trans_real import translation as translation_catalogs

from easymode.utils import first_match
from easymode.utils.standin import standin_for
from easymode.utils.languagecode import get_all_language_codes, get_real_fieldname

__all__ = ('GettextVO',)

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


class GettextVO:
    """
    A value object that contains information about the origin
    of the value in question.
    
    .. attribute:: standin_value_is_from_database

        is True if the value came from the database

    .. attribute:: msgid
    
        The message id that originated the lookup

    .. attribute:: msg
        
        The message that is the result of the lookup
    
    .. attribute:: fallback
    
        the fallback that was found during the lookup
    
    .. attribute:: stored_value
        
        the value as it is stored in the database
    
    """
    
    def __init__(self):
        self.standin_value_is_from_database = False
        self.msgid = None
        self.msg = None
        self.fallback = None
        self.stored_value = None


class DefaultFieldDescriptor(property):
    """
    Descriptor that implements access to the default language.
    It inherits property because django wants that, it doesn't process
    it as a field if it is not isinstance(self, property)
    """

    def __init__(self, name, **kwargs):
        """The name param is the name of the field the descriptor is emulating."""
        self.name = name
        self.__dict__.update(kwargs)

    def __get__(self, obj, typ=None):
        """
        Read the localised version of the field this descriptor emulates.
        First try to see if the localised field is really set.
        If not, then use ugettext_lazy to find a tranlation in the current language
        for this field.
        """
        # self must be returned in a getattr context.
        if obj is None:
            return self

        current_language = translation.get_language()
        real_field_name = get_real_fieldname(self.name, current_language)

        vo = GettextVO()
        
        # first check if the database contains the localized data
        vo.stored_value = getattr(obj, real_field_name)

        # the database does not have our localized data.
        # check if we have a translation, first get the msgid, as a unicode string.
        vo.msgid = get_localized_property(obj, self.name, getattr(settings, 'MSGID_LANGUAGE', settings.LANGUAGE_CODE))

        # check the translation in the current language
        # but avoid empty string and None 
        if valid_for_gettext(vo.msgid):
            vo.msg = self.to_python(translation.ugettext(force_unicode(vo.msgid)))
        elif valid_for_gettext(vo.stored_value):
            # we can not use the msgid for gettext but we did find a valid
            # translation in the database. Fine we stop here and return that
            # value. No need for a standin, because we don't have a catalog value.
            return vo.stored_value
        else:
            # we can not use the msgid for gettext lookups, so there is no
            # point in trying. Check for fallback languages in database.
            vo.fallback = get_localized_property(obj, self.name)
            
            if not valid_for_gettext(vo.fallback):
                # Also if we are sure we don't have any old
                # translations in the catalog or something for the fallback
                # languages in the database, we do not need to return a standin either
                return vo.msgid
        
        # we got here so we've got a valid messageid. Now collect data from the catalog(s)
        
        # if there isn't anything new in the catalog belonging to the current language:
        if vo.msg == vo.msgid:
            # maybe we have a translation in any of the fallback languages.
            if hasattr(settings, 'FALLBACK_LANGUAGES'):
                # first check if the database has the localized data in
                # any of the fallback languages.
                vo.fallback = get_localized_property(obj, self.name)
                
                # if the fallback is the same as the msgid, go and look in the catalog
                if vo.fallback == vo.msgid:
                    # there might be a translation in any
                    # of the fallback languages.
                    for fallback in get_fallback_languages():
                        catalog = translation_catalogs(fallback)
                        msg = catalog.ugettext(force_unicode(vo.msgid))
                        if self.to_python(msg) != vo.msgid:
                            vo.fallback = self.to_python(msg)
                            break
                elif vo.fallback:
                    # if a valid fallback is found, then, since the msg is equal
                    # to the msgid, the fallback is the winner.
                    vo.msg = vo.fallback

        # if we came here we collected data from the catalog and we should return
        # a standin. A standin is the return value, with some extra properties.
        # see GettextVO for the extra properties added.
        if valid_for_gettext(vo.stored_value):
            vo.standin_value_is_from_database = True
            # database always wins
            return standin_for(vo.stored_value, **vo.__dict__)
        elif valid_for_gettext(vo.msg):
            # runner up is the translation in the native language
            return standin_for(vo.msg, **vo.__dict__)
        elif valid_for_gettext(vo.fallback):
            # and last is the translation in a fallback language
            return standin_for(vo.fallback, **vo.__dict__)

        assert(valid_for_gettext(vo.msgid))

        # there is a very very small probability that the translation of
        # a valid msgid evaluates to empty string or None (after to_python).
        # If that happened, we got here. I choose to return None, because i like
        # to be like that
        return None

    def __set__(self, obj, value):
        """Write the localised version of the field this descriptor emulates."""
        local_property = get_localized_field_name(obj, self.name)
        setattr(obj, local_property, value)

    def get_internal_type(self):
        """Used to describe the type while serializing."""
        return "CharField"

    def value_to_string(self, obj):
        """This descriptor acts as a Field, as far as the serializer is concerned."""
        try:
            return force_unicode(self.__get__(obj))
        except TypeError:
            return str(self.__get__(obj))


def localize_fields(cls, localized_fields):
    """
    For each field name in localized_fields,
    for each language in settings.LANGUAGES,
    add fields to cls,
    and remove the original field, instead
    replace it with a DefaultFieldDescriptor,
    which always returns the field in the current language.
    """
    
    # never do this twice
    if hasattr(cls, 'localized_fields'):
        return cls
        
    # MSGID_LANGUAGE is the language that is used for the gettext message id's.
    # If it is not available, because the site isn't using subsites, the LANGUAGE_CODE
    # is good too. MSGID_LANGUAGE gives the opportunity to specify a language not available
    # in the site but which is still used for the message id's.
    msgid_language = getattr(settings, 'MSGID_LANGUAGE',  settings.LANGUAGE_CODE)
    
    # set the localized fields property
    cls.localized_fields = localized_fields
    
    for field in localized_fields:
        original_attr = cls._meta.get_field_by_name(field)[0]
        
        for cnt, language_code in enumerate(get_all_language_codes()):
            i18n_attr = copy.copy(original_attr)
            # add support for south introspection.
            i18n_attr._south_introspects = True
            i18n_attr.original_fieldname = field
            i18n_attr.include_in_xml = False
            lang_attr_name = get_real_fieldname(field, language_code)
            i18n_attr.creation_counter = i18n_attr.creation_counter + .01 * cnt
            # null must be allowed for the message id language because this language
            # might not be available at all in the backend
            if not i18n_attr.null and i18n_attr.default is NOT_PROVIDED:
                i18n_attr.null = True
            
            if language_code != msgid_language:
                # no validation for the fields that are language specific
                if not i18n_attr.blank:
                    i18n_attr.blank = True
                    
            if i18n_attr.verbose_name:
                i18n_attr.verbose_name = translation.string_concat(i18n_attr.verbose_name, u' (%s)' % language_code)
            cls.add_to_class(lang_attr_name, i18n_attr)
            
        # delete original field
        del cls._meta.local_fields[cls._meta.local_fields.index(original_attr)]

        # copy some values and functions from the original_attr
        # so the field can emulate the original_attr as good as possible
        kwargs = {
            'serialize': getattr(original_attr, 'serialize', True),
            'extra_attrs':getattr(original_attr, 'extra_attrs', None),
            'max_length': getattr(original_attr, 'max_length', None),
            'min_length' : getattr(original_attr, 'min_length', None),
            'form_field' : original_attr.formfield(**FORMFIELD_FOR_DBFIELD_DEFAULTS.get(original_attr.__class__, {})),
            'get_internal_type': original_attr.get_internal_type,
            'unique': getattr(original_attr, 'unique', False),
            'to_python': original_attr.to_python,
        }
            
        # copy custom_value_serializer if it was defined on the original attr
        if hasattr(original_attr, 'custom_value_serializer'):
            kwargs['custom_value_serializer'] = original_attr.custom_value_serializer

        # add the DefaultFieldDescriptor where the original_attr was.
        cls.add_to_class(field, DefaultFieldDescriptor(field, **kwargs))
        
        # update fields cache
        cls._meta._fill_fields_cache()

    # return the finished product
    return cls
