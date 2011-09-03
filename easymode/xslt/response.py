"""
Defines a :func:`render_to_response` function that resembles django.utils's
:func:`~django.shortcuts.render_to_response` helper. Only this time the template is an xslt and the object
passed as the second argument must have a ``__xml__`` method. (See :func:`~easymode.tree.xml.decorators.toxml`)
"""
from django.http import HttpResponse

from easymode.tree import xml as xmltree
from easymode.utils.template import find_template_path
from easymode.xslt import transform


def render_to_response(template, object, params=None, mimetype='text/html'):
    """
    ``object`` will be converted to xml using :func:`easymode.tree.xml`. The resulting xml 
    will be transformed using ``template``.
    The result will be a :class:`~django.http.HttpResponse` object,
    containing the transformed xml as the body.
    
    :param template: an xslt template name.
    :param object: an object that has an ``__xml__`` method. (See :func:`easymode.tree.xml.decorators.toxml`).
    :param params: A dictionary containing xslt parameters. Use :func:`~easymode.xslt.prepare_string_param`\
        on strings you want to pass in.
    :param mimetype: The mimetype of the :class:`~django.http.HttpResponse`
    :rtype: :class:`django.http.HttpResponse`
    """
    xsl_path = find_template_path(template)
    xml = xmltree.xml(object)
    
    result = transform(xml, str(xsl_path), params)
    return HttpResponse(result, mimetype=mimetype)
    
def render_to_string(template, object, params=None):
    """
    ``object`` will be converted to xml using :func:`easymode.tree.xml`. The resulting xml 
    will be transformed using ``template``.
    The result is a unicode string containing the transformed xml.
    
    :param template: an xslt template name.
    :param object: an object that has an ``__xml__`` method. (See :func:`easymode.tree.xml.decorators.toxml`).
    :param params: A dictionary containing xslt parameters. Use :func:`~easymode.xslt.prepare_string_param`\
        on strings you want to pass in.
    :rtype: :class:`unicode`
    """
    xsl_path = find_template_path(template)
    xml = xmltree.xml(object)
    
    result = transform(xml, str(xsl_path), params)
    return result

def render_xml_to_string(template, input, params=None):
    """
    Transforms ``input`` using ``template``, which should be an xslt.
    
    :param template: an xslt template name.
    :param input: an string that contains xml
    :param params: A dictionary containing xslt parameters. Use :func:`~easymode.xslt.prepare_string_param`\
        on strings you want to pass in.
    :rtype: :class:`unicode`
    """
    xsl_path = find_template_path(template)

    result = transform(input, str(xsl_path), params)  
    return result
