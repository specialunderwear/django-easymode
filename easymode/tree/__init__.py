"""
Makes django models into trees.

If a django model tree can be categorised as a DAG (Directed Acylclic Graph)
This module contains the machinery to add recursive serialisation to xml 
and recursive admin support to the models in such a tree.
"""
def xml(decorated_model):
    """
    Used to convert either 
    
    - a django model decorated with :func:`easymode.tree.decorators.toxml`
    - a queryset obtained by querying a model decorated with :func:`easymode.tree.decorators.toxml`
    - an :class:`easymode.tree.query.XmlQuerySetChain`
    
    to xml
    """
    return (decorated_model.__xml__())