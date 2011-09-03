"""
Derived from django-transmeta.
Contains machinery to change a type after construction,
by using a class decorator.

This in contrast with django-transmeta which requires
overriding the __metaclass__.
"""
import copy

from django.conf import settings
from django.contrib.admin.options import FORMFIELD_FOR_DBFIELD_DEFAULTS
from django.db.models.fields import NOT_PROVIDED
from django.utils import translation

from easymode.utils.languagecode import get_all_language_codes, get_real_fieldname
from easymode.i18n.meta.fields import DefaultFieldDescriptor
from easymode.i18n.meta.utils import get_field_from_model_by_name


__all__ = ('localize_fields',)


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
        original_attr = get_field_from_model_by_name(cls, field)
        
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
            
        # copy __serialize__ if it was defined on the original attr
        if hasattr(original_attr, '__serialize__'):
            kwargs['__serialize__'] = original_attr.__serialize__

        # add the DefaultFieldDescriptor where the original_attr was.
        cls.add_to_class(field, DefaultFieldDescriptor(field, **kwargs))
        
        # update fields cache
        cls._meta._fill_fields_cache()

    # return the finished product
    return cls
