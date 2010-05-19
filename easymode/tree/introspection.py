"""
functionality for finding inverse foreign key relations in model classes
"""
import inspect

from django.contrib.contenttypes.generic import ReverseGenericRelatedObjectsDescriptor
from django.db.models.fields.related import ForeignRelatedObjectsDescriptor, SingleRelatedObjectDescriptor
from django.db.models.base import ModelBase

from easymode.i18n.meta import DefaultFieldDescriptor

SUBFIELDBASE_ERROR = """
%s

Easymode caught an AttributeError while trying
to inspect %s looking for %s. This is probably caused
by SubFieldBase, see http://code.djangoproject.com/ticket/12568.
Easymode will patch SubFieldBase for you, you just have to make sure
not to reference it before easymode is imported. This
means you can not load any apps that use SubFieldBase before
you load easymode.
"""

def _get_members_of_type(obj, member_type):
    """
    Finds members of a certain type in obj.

    :param obj: A model instance or class.
    :param member_type: The type of the menber we are trying to find.
    :rtype: A :class:`list` of ``member_type`` found in ``obj``
    """
    try:
        def filter_member_type(member):
            try:
                return type(member) is member_type
            except AttributeError:
                return False
                
        # if the type of obj is the metaclass for all models, just search in the object
        # because it is not a model instance but a type
        if type(obj) is ModelBase:
            key_hash = inspect.getmembers(obj, filter_member_type)
        else:
            key_hash = inspect.getmembers(obj.__class__, filter_member_type)
            
    except AttributeError as e:
        raise AttributeError(SUBFIELDBASE_ERROR % (e, obj, member_type))

    return key_hash

def get_foreign_key_desciptors(obj):
    """
    finds all :class:`~django.db.models.fields.ForeignRelatedObjectsDescriptor` in obj.
    
    :param obj: A model instance or class.
    """
    return _get_members_of_type(obj, ForeignRelatedObjectsDescriptor)

def get_one_to_one_descriptors(obj):
    """
    finds all :class:`~django.db.models.fields.SingleRelatedObjectDescriptor` in obj.

    :param obj: A model instance or class.
    """
    return _get_members_of_type(obj, SingleRelatedObjectDescriptor)

def get_generic_relation_descriptors(obj):
    """
    Finds all the :class:`~django.contrib.contenttypes.generic.ReverseGenericRelatedObjectsDescriptor` in obj.
    
    :param obj: A model instance or class.
    """
    return _get_members_of_type(obj, ReverseGenericRelatedObjectsDescriptor)

def get_default_field_descriptors(obj):
    """
    find all  :class:`~easymode.i18n.meta.DefaultFieldDescriptor` in obj.
    
    :param obj: A model instance or class.
    """
    return _get_members_of_type(obj, DefaultFieldDescriptor)
