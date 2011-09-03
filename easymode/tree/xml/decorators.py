"""
Contains a decorator that can be used to add xml serialization to django
models as a method. In effect it adds an ``__xml__`` method to both the model and
the queryset used in the model.
"""

from easymode.tree.xml.serializers import RecursiveXmlSerializer
from easymode.tree.xml.query import QuerySetManager, XmlSerializableQuerySet

def toxml(cls):
    """
    adds an ``__xml__`` method to both the queryset as the model class.
    
    usage::
    
        from easymode.tree.xml.decorators import toxml

        @toxml
        class Foo(models.ModelAdmin):
            title = models.CharField(max_length=255)
            content = TextField()

        class Bar(models.ModelAdmin):
            foo = models.ForeignKey(Foo, related_name=bars)

            label = models.CharField(233)

    The ``Foo`` model has now gained a ``__xml__`` method on both itself as on the
    queryset it produces. Calling it will produce hierarchical xml, where all inverse
    relations are followed. (Except for manytomany fields, they are not supported)."""
    
    if cls._meta.abstract:
        raise Exception("You can not use toxml on abstract classes")
        
    def __xml__(self):
        """turn model object into xml recursively"""
        ser = RecursiveXmlSerializer()
        return ser.serialize([self])
    
    cls.add_to_class('objects', QuerySetManager(XmlSerializableQuerySet))
    cls.__xml__ = __xml__
    return cls
