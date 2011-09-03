"""
Functionality to create trees of django models.

If a django model tree can be categorised as a DAG (Directed Acylclic Graph)
This module contains the machinery to add recursive serialisation to xml
and recursive admin support to the models in such a tree.
"""

__all__ = ('xml', 'admin', 'decorators', 'introspection', 'query', 'serializers')

def xml(obj):
    """
    Used to convert either 
    
    - a django model decorated with :func:`easymode.tree.xml.decorators.toxml`
    - a queryset obtained by querying a model decorated with :func:`easymode.tree.xml.decorators.toxml`
    - an :class:`easymode.tree.xml.query.XmlQuerySetChain`
    
    to xml
    """
    return (obj.__xml__())