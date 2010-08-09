from django.contrib import admin
from django.contrib.admin.sites import AlreadyRegistered
from django.db.models.base import ModelBase

from easymode.i18n.admin.decorators import L10n

__all__ = ('register_all',)

def register_all(module, exclude=[]):
    """
    Register all models in *module* with the admin
    
    :param module: The module that contains the models
    :param exclude: A list of models classes that should not be registered
    """
    member_names = dir(module)

    for member_name in member_names:
        obj = getattr(module, member_name, None)
        if isinstance(obj, ModelBase) \
            and obj not in exclude \
            and not obj._meta.abstract:
            try:
                if hasattr(obj, 'localized_fields'):
                    admin.site.register(obj, L10n(obj, admin.ModelAdmin))
                else:
                    admin.site.register(obj)
            except AlreadyRegistered:
                pass