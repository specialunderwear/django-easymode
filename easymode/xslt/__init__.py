"""
Contains xslt transformation functionality to be used with django models
"""
import codecs
from StringIO import StringIO
from django.utils.encoding import smart_unicode

__all__ = ('XsltError', 'transform', 'prepare_string_param')

class XsltError(Exception):
    """The xslt transformation resulted in an error"""
    pass
    
class MessageHandler:
    def __init__(self):
        self.content = ''
    def write(self, msg):
        self.content = self.content + msg
    def getContent(self):
        return self.content

def _transform_libxslt(xml, xslt, params=None):
    """
    Do xml transformation using libxml2-python and libxslt-python.
    
    http://xmlsoft.org/python.html
    """
    try:
        xslt_doc = libxml2.parseDoc(xslt)
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

def _transform_libxsltmod(xml, xslt, params=None):
    """
    Do xslt transformation using libxsltmod.
    
    http://www.rexx.com/~dkuhlman/libxsltmod.html
    """
    handler = MessageHandler()
    try:
        result = libxsltmod.translate_to_string(
            's', xslt,
            's', xml,
            handler, params or {})            
        return result
    except RuntimeError:
        messages = handler.getContent()
        raise XsltError(messages)

def _transform_lxml(xml, xslt, params=None):
    """
    Do xslt transformation using lxml.
    
    http://codespeak.net/lxml/
    """
    # assuming params where created with prepare_string_param,
    # they are encoded as unicode, which lxml does not like
    for (key, value) in params.iteritems():
        params[key] = value.decode('utf-8')

    xml_doc = etree.fromstring(xml)
    xslt_doc = etree.fromstring(xslt)
    xslt_proc = etree.XSLT(xslt_doc)
    
    result = xslt_proc(xml_doc, **params)
    return unicode(result)

# determine which xslt engine to use,
# the default is libxsltmod.
transform = _transform_libxsltmod

try:
    import libxslt
    import libxml2

    transform = _transform_libxslt
except:
    pass

try:
    from lxml import etree

    transform = _transform_lxml
except:
    pass
   
def prepare_string_param(string):    
    result = u"'%s'" % (string.replace("'","&apos;") or '')
    return result.encode('utf-8')
    
