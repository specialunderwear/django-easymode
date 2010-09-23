"""
:func:`~django.shortcuts.render_to_response` like functions, that help you
create views with filtered xml.
"""
from django.http import HttpResponse

from easymode.easypublisher.utils import filter_unpublished, insert_draft
from easymode.tree import xml as to_xml
from easymode.xslt.response import render_xml_to_string


def render_to_response_with_revision(template, queryset, revision_id, params=None, mimetype='text/html'):
    """
    Renders a queryset to xml, but inserts the data from revision *revision_id*
    in the appropriate place. This can be used to enable previews
    
    :param template: The xslt template path.
    :param queryset: The queryset that should be turned into xml.
    :param revision_id: The id of the revision whose data we want to include in the xml.
    :param params: xslt params, correctly escaped using :func:`~easymode.xslt.response.prepare_string_param`
    :param mimetype: The mimetype of the response.
    :result: A :class:`~django.http.HttpResponse` with xml, including the data in revision *revision_id*
    """
    xml = insert_draft(revision_id, to_xml(queryset))
    return HttpResponse(render_xml_to_string(template, xml, params), mimetype=mimetype)

def render_to_response_filtered(template, queryset, params=None, mimetype='text/xml'):
    """
    Renders a queryset to xml but it strips all objects that have a field named
    published that is set to False.
    
    :param template: The xslt template path.
    :param queryset: The queryset that should be turned into xml.
    :param params: xslt params, correctly escaped using :func:`~easymode.xslt.response.prepare_string_param`
    :param mimetype: The mimetype of the response.
    :result: A :class:`~django.http.HttpResponse` with xml, with only published models.
    """
    xml = filter_unpublished(to_xml(queryset))
    return HttpResponse(render_xml_to_string(template, xml, params), mimetype=mimetype)