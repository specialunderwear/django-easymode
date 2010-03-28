"""
Defines a :func:`render_to_response` function that resembles django.utils's
:func:`~django.shortcuts.render_to_response` helper. Only this time the template is an xslt and the object
passed as the second argument must have a ``__xml__`` method. (See :func:`~easymode.tree.decorators.toxml`)
"""
from django.http import HttpResponse
from django.template.loader import find_template_source
from easymode.xslt import transform
from easymode import tree


def render_to_response(template, object, params=None, mimetype='text/html'):
    """
    ``object`` will be converted to xml using :func:`easymode.tree.xml`. The resulting xml 
    will be transformed using ``template``.
    The result will be a :class:`~django.http.HttpResponse` object,
    containing the transformed xml as the body.
    
    :param template: an xslt template.
    :param object: an object that has an ``__xml__`` method. (See :func:`easymode.tree.decorators.toxml`).
    :param params: A dictionary containing xslt parameters. Use :func:`~easymode.xslt.prepare_string_param`\
        on strings you want to pass in.
    :param mimetype: The mimetype of the :class:`~django.http.HttpResponse`
    :rtype: :class:`django.http.HttpResponse`
    """
    xsl = find_template_source(template)[0]
    xml = tree.xml(object)
    
    result = transform(xml, xsl, params)
    return HttpResponse(result, mimetype=mimetype)
    
def render_to_string(template, object, params=None):
    """
    ``object`` will be converted to xml using :func:`easymode.tree.xml`. The resulting xml 
    will be transformed using ``template``.
    The result is a unicode string containing the transformed xml.
    
    :param template: an xslt template.
    :param object: an object that has an ``__xml__`` method. (See :func:`easymode.tree.decorators.toxml`).
    :param params: A dictionary containing xslt parameters. Use :func:`~easymode.xslt.prepare_string_param`\
        on strings you want to pass in.
    :rtype: :class:`unicode`
    """
    xsl = find_template_source(template)[0]
    xml = tree.xml(object)

    result = transform(xml, xsl, params)
    return result

def render_xml_to_string(template, input, params=None):
    """
    Transforms ``input`` using ``template``, which should be an xslt.
    
    :param template: an xslt template
    :param input: an string that contains xml
    :param params: A dictionary containing xslt parameters. Use :func:`~easymode.xslt.prepare_string_param`\
        on strings you want to pass in.
    :rtype: :class:`unicode`
    """
    xsl = find_template_source(template)[0]
    result = transform(input, xsl, params)  
    return result