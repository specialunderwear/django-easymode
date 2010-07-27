"""
Derived from django-transmeta.
Contains mach to make models internationalized.

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
    
    if settings.FALLBACK_LANGUAGES:
        attrs = [translation.get_language()]
        attrs += get_fallback_languages()
    else:
        attrs = [
            translation.get_language(),
            translation.get_language()[:2],
            settings.LANGUAGE_CODE, 
        ]
        
    predicate = lambda x: getattr(context, get_real_fieldname(field, x), None)

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
    
    .. attribute:: msgid
    
        The message id that originated the lookup

    .. attribute:: msg
        
        The message that is the result of the lookup
    
    .. attribute:: fallback
    
        the fallback that was found during the lookup
    
    .. attribute:: stored_value
        
        the value as it is stored in the databas
    
    """
    msgid = None
    msg = None
    fallback = None
    stored_value = None

                       
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
        vo.msgid = force_unicode(get_localized_property(obj, self.name, 
            getattr(settings, 'MSGID_LANGUAGE', settings.LANGUAGE_CODE)))

        # check the translation in the current language
        vo.msg = self.to_python(translation.ugettext(vo.msgid))

        # if there isn't anything new in the catalog belonging to the current language:
        if vo.msg is vo.msgid:
            # maybe we have a translation in any of the fallback languages.
            if hasattr(settings, 'FALLBACK_LANGUAGES'):
                # first check if the database has the localized data in
                # any of the fallback languages.
                vo.fallback = get_localized_property(obj, self.name)

                # if the msgid is '' or None we don't have to look
                # for translations because there are none.
                if vo.fallback not in (None, "") and vo.msgid not in (None, ""):
                    # there might be a translation in any
                    # of the fallback languages.
                    for fallback in get_fallback_languages():
                        catalog = translation_catalogs(fallback)
                        msg = catalog.ugettext(vo.msgid)
                        if self.to_python(msg) is not vo.msgid:
                            vo.fallback = self.to_python(msg)
                            break

        if vo.stored_value not in (None, ""):
            return standin_for(vo.stored_value, **vo.__dict__)
        elif vo.msg not in (None, ""):
            return standin_for(vo.msg, **vo.__dict__)
        elif vo.fallback not in (None, ""):
            return standin_for(vo.fallback, **vo.__dict__)

        if vo.msgid in (None, ""):
            return standin_for(self.to_python(u''), **vo.__dict__)

        # # no fallback language and the database does not have
        # # the localized data, so use the translation of the msgid
        return self.to_python(standin_for(vo.msg, **vo.__dict__))

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
        
        for cnt, lang_code in enumerate(get_all_language_codes()):
            lang_attr = copy.copy(original_attr)
            # add support for south introspection.
            lang_attr._south_introspects = True
            lang_attr.original_fieldname = field
            lang_attr.include_in_xml = False
            lang_attr_name = get_real_fieldname(field, lang_code)
            lang_attr.creation_counter = lang_attr.creation_counter + .01 * cnt
            # null must be allowed for the message id language because this language
            # might not be available at all in the backend
            if not lang_attr.null and lang_attr.default is NOT_PROVIDED:
                lang_attr.null = True
            
            if lang_code != msgid_language:
                # no validation for the fields that are language specific
                if not lang_attr.blank:
                    lang_attr.blank = True
                    
            if lang_attr.verbose_name:
                lang_attr.verbose_name = translation.string_concat(lang_attr.verbose_name, u' (%s)' % lang_code)
            cls.add_to_class(lang_attr_name, lang_attr)
            
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
