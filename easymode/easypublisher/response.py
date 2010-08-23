from django.http import HttpResponse

from easymode.easypublisher.utils import filter_unpublished, insert_draft
from easymode.tree import xml as to_xml
from easymode.xslt.response import render_xml_to_string


def render_to_response_with_revision(template, queryset, revision_id, params=None, mimetype='text/html'):
    xml = insert_draft(revision_id, to_xml(queryset))
    return HttpResponse(render_xml_to_string(template, xml, params), mimetype=mimetype)

def render_to_response_filtered(template, queryset, params=None, mimetype='text/xml'):
    xml = filter_unpublished(to_xml(queryset))
    return HttpResponse(render_xml_to_string(template, xml, params), mimetype=mimetype)