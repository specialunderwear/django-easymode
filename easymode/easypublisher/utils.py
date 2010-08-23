"""
Contains tools to enable preview of drafts.
"""
from lxml import etree
from reversion.models import Revision

from easymode.tree.serializers import RecursiveXmlSerializer


__all__ = ('filter_unpublished', 'insert_draft')

def insert_draft(revision_id, xml):
    rev = Revision.objects.get(pk=revision_id)
    xml_doc = etree.fromstring(xml)    
    serializer = RecursiveXmlSerializer()    

    for ver in rev.version_set.all():
        app_label = ver.content_type.app_label
        model_name = ver.content_type.model

        model_instance = ver.get_object_version().object
        
        xpath_params = {
            'app_label' : ver.content_type.app_label,
            'model' : ver.content_type.model,
            'pk': model_instance.pk,
        }
        
        xpath = r"//object[@pk='%(pk)s' and @model='%(app_label)s.%(model)s']" \
            % xpath_params

        draft_xml = serializer.serialize([model_instance])
        draft_doc = etree.fromstring(draft_xml)
        
        draft_node = draft_doc.xpath(r'/django-objects/object')[0]
        for node in xml_doc.xpath(xpath):
            node.getparent().replace(node, draft_node)
        
    return etree.tostring(xml_doc)


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