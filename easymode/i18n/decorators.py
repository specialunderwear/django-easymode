import sys
import os
from django.conf import settings

from easymode.i18n import meta
from easymode import i18n

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
        if getattr(settings, 'AUTO_CATALOG', True):
            i18n.register(cls, getattr(settings, 'LOCALE_DIR', None) or model_dir )
        
        cls._meta.permissions.append(("can_edit_global_fields", "Can edit restricted fields"))

        return cls
    
def L10n_CMS(*localized_fields):

    def modify_class(cls):
        model_dir = os.path.join(settings.PROJECT_DIR, 'cms' + getattr(settings, 'LOCALE_POSTFIX', ''))
        cls = meta.localize_cms_stuff_fields(cls, *localized_fields)
        if getattr(settings, 'AUTO_CATALOG', True):
            i18n.register(cls, getattr(settings, 'LOCALE_DIR', None) or model_dir)
        
        return cls
        
    return modify_class
