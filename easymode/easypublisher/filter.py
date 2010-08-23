from lxml import etree

__all__ = ('filter_unpublished',)

def filter_unpublished(xml):
    """
    >>> a = '''<root>
    ... <object><field name="published">False</field>hahaha</object>
    ... <object><field name="published">True</field>hihih</object>
    ... <object><field name="koe">False</field>lololol</object>
    ... <object>
    ...     <field name="published">False</field>
    ...     hahaha
    ...     <object><field name="koe">False</field>doe eens niet</object>
    ... </object></root>'''
    >>>
    >>> filter_unpublished(a)
    '<root>\\n<object><field name="published">True</field>hihih</object>\\n<object><field name="koe">False</field>lololol</object>\\n</root>'
    """
    
    xpath = "//object[field[@name='published' and text() = 'False']]"
    xml_tree = etree.fromstring(xml)
    for node in xml_tree.xpath(xpath):
        node.getparent().remove(node)
    
    return etree.tostring(xml_tree)