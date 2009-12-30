"""
Makes django models into trees.

If a django model tree can de categorised as a DAG (Directed Acylclic Graph)
This app can add recursive serialisation to xml and recursive admin support
to these models.
"""
def xml(decorated_model):
    """tries to convert a django model decorated with toXml to xml"""
    return (decorated_model.__xml__())