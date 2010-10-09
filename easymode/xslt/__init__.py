"""
Contains xslt transformation functionality to be used with django models
"""

__all__ = ('XsltError', 'transform', 'prepare_string_param', 'response')


class XsltError(Exception):
    """The xslt transformation resulted in an error"""
    pass


def _transform_libxslt(xml, xslt, params=None):
    """
    Transform ``xslt`` using any of the 3 supported xslt engines:

    - `lxml <http://codespeak.net/lxml/>`_
    - `libxml <http://xmlsoft.org/python.html>`_

    :param xml: The xml to be transformed.
    :param xslt: The xslt to be used when transforming the ``xml``.
    :param params: A dictionary containing xslt parameters. Use :func:`~easymode.xslt.prepare_string_param`\
        on strings you want to pass in.
    """
    try:
        xslt_doc = libxml2.parseFile(xslt)
        xslt_proc = libxslt.parseStylesheetDoc(xslt_doc)
        xml_doc = libxml2.parseDoc(xml)
        
        result = xslt_proc.applyStylesheet(xml_doc, params)

        xml_string = str(result)
        xml_unicode_string = xml_string.decode('utf-8')

        xslt_proc.freeStylesheet()
        xml_doc.freeDoc()

        return xml_unicode_string
    except RuntimeError as e:
        raise XsltError(str(e))


def _transform_lxml(xml, xslt_path, params=None):
    """
    Transform ``xslt`` using any of the 2 supported xslt engines:

    - `lxml <http://codespeak.net/lxml/>`_
    - `libxml <http://xmlsoft.org/python.html>`_

    :param xml: The xml to be transformed.
    :param xslt: The xslt to be used when transforming the ``xml``.
    :param params: A dictionary containing xslt parameters. Use :func:`~easymode.xslt.prepare_string_param`\
        on strings you want to pass in.
    """
    # assuming params where created with prepare_string_param,
    # they are encoded as unicode, which lxml does not like
    
    xml_doc = etree.fromstring(xml)
    xslt_doc = etree.parse(xslt_path)
    xslt_proc = etree.XSLT(xslt_doc)

    if params:
        for (key, value) in params.iteritems():
            params[key] = value.decode('utf-8')
        result = xslt_proc(xml_doc, **params)
    else:
        result = xslt_proc(xml_doc)
    
    return unicode(result)

# determine which xslt engine to use,
try:
    from lxml import etree

    transform = _transform_lxml
except:
    import libxslt
    import libxml2

    transform = _transform_libxslt


def prepare_string_param(string):
    """
    Prepare a string for passing as a parameter to the xslt processor.
    
    :param string: The string you want to pass to the xslt.
    """
    result = u"'%s'" % (string.replace("'","&apos;") or '')
    return result.encode('utf-8')
