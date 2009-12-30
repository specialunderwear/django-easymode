"""
Defines a render_to_response function that resembles django.utils's
render_to_response helper. Only this time the template is an xslt and the object
passed as the second argument must have a __xml__ method.
"""
from django.http import HttpResponse
from django.template.loader import find_template_source
from easymode.xslt import transform
from easymode import tree


def render_to_response(template, object, params=None, mimetype='text/html'):
    """
    template: an xslt template
    object: an object that has an __xml__ method
    """
    xsl = find_template_source(template)[0]
    xml = tree.xml(object)
    
    result = transform(xml, xsl, params)
    return HttpResponse(result, mimetype=mimetype)
    
def render_to_string(template, object, params=None):
    """
    template: an xslt template
    object: an object that has an __xml__ method
    """
    xsl = find_template_source(template)[0]
    xml = tree.xml(object)

    result = transform(xml, xsl, params)
    return result

def render_xml_to_string(template, input, params=None):
    """
    template: an xslt template
    input: an string that contains xml
    """
    xsl = find_template_source(template)[0]
    result = transform(input, xsl, params)  
    return result