"""
Contains tools to enable preview of drafts.
"""
from lxml import etree
from reversion.models import Revision

from easymode.tree import xml
from easymode.tree.serializers import RecursiveXmlSerializer
from easymode.xslt.response import render_xml_to_string

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

def render_to_response_with_revision(template, input, revision_id, params=None, mimetype='text/html'):
    xml = insert_draft(revision_id, xml(object))
    render_xml_to_string(template, xml, params)