"""
Classes to support overriding the default queryset used in django models.
These classes add a recursive __xml__ method to a django model's queryset
"""
from itertools import chain

from django.db import models
from django.db.models.query import QuerySet
from easymode.tree.serializers import RecursiveXmlSerializer

class QuerySetManager(models.Manager):

    """
    Allows setting a custom QuerySet type
    """
    use_for_related_fields = True

    def __init__(self, qs_class=models.query.QuerySet):
        """Pass the type of the queryset to the constructor"""
        self.queryset_class = qs_class
        super(QuerySetManager, self).__init__()

    def get_query_set(self):
        """manager will return the custom queryset"""
        return self.queryset_class(self.model)

    def __getattr__(self, attr, *args):
        try:
            return getattr(self.__class__, attr, *args)
        except AttributeError:
            return getattr(self.get_query_set(), attr, *args)

class XmlSerializableQuerySet(QuerySet):
    """
    Adds a method to the queryset that can serialize it to xml
    """
    
    def __xml__(self):
        """turn querysets into xml recursively"""
        ser = RecursiveXmlSerializer()
        return ser.serialize(self)

class XmlQuerySetChain(list):
    """
    Can be used to combine multiple querysets and turn them into
    xml in one go.
    
    usage::
        
        from easymode.tree import xml
        from example.foobar.models import *
        
        foos = Foo.objects.all()
        bars = Bar.objects.all()
        foobars = XmlQuerySetChain(foos, bars)
        
        xml_string = xml(foobars)
    
    You can also pass an ``XmlQuerySetChain`` into ``easymode.xslt.response.render_to_response``.
    
    :param querysets: a :class:`list` of querysets that should combined into a single xml.
    """
    def __init__(self, *querysets):
        """Pass some querysets to this queryset chain and they can all be serialized together."""
        list.__init__(self, chain(*querysets))
    
    def __xml__(self):
        """turn querysets into xml recursively"""
        ser = RecursiveXmlSerializer()
        return ser.serialize(self)
    
    