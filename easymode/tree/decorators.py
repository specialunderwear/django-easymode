"""
Contains a decorator that can be used to add xml serialization to django
models as a method. In effect it ass a __xml__ method to both the model and
the queryset used in the model.

Also contains some decorators for adding methods to classes
"""

from easymode.tree.serializers import RecursiveXmlSerializer
from query import QuerySetManager, XmlSerializableQuerySet

def toxml(cls):
    """adds a __xml__ method to both the queryset as the model class"""
    
    if cls._meta.abstract:
        raise Exception("You can not use toxml on abstract classes")
        
    def __xml__(self):
            """turn model object into xml recursively"""
            ser = RecursiveXmlSerializer()
            return ser.serialize([self])
    
    cls.add_to_class('objects', QuerySetManager(XmlSerializableQuerySet))
    cls.__xml__ = __xml__
    return cls
