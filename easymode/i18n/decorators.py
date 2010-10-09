import os
import sys

from django.conf import settings

from easymode import i18n
from easymode.i18n import meta


__all__ = ('I18n',)

class I18n(object):
    """
    Internationalise a model class.
    
    use like this:
    
    >>> from django.db import models
    >>> from easymode.i18n.decorators import I18n
    >>> 
    >>> @I18n('iamatranslatedfield')
    >>> class Bla(models.Model):
    >>>     iamafield = models.CharField(max_length=255)
    >>>     iamatranslatedfield = models.CharField(max_length=255)
    
    Now ``iamatranslatedfield`` it's value can vary by language.
    """
    def __init__(self, *localized_fields):
        """initialize the decorator"""
        self.localized_fields = localized_fields
        
    def __call__(self, cls):
        """Executes the decorator on the cls."""
        model_dir = os.path.dirname(sys.modules[cls.__module__].__file__) + getattr(settings, 'LOCALE_POSTFIX', '')
        cls = meta.localize_fields(cls, self.localized_fields)
        if getattr(settings, 'AUTO_CATALOG', False):
            i18n.register(cls, getattr(settings, 'LOCALE_DIR', None) or model_dir )
        
        # add permission for editing the untranslated fields in this model
        cls._meta.permissions.append(
            ("can_edit_untranslated_fields_of_%s" % cls.__name__.lower(), 
            "Can edit untranslated fields")
        )

        return cls
