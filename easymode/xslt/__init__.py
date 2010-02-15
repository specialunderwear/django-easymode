"""
Contains xslt transformation functionality to be used with django models
"""
import codecs
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
    import libxslt
    import libxml2
    
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

def _transform_libxsltmod(xml, xslt, params):
    import libxsltmod
    
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

def _transform_lxml(xml, xslt, params):
    from lxml import etree
    from StringIO import StringIO
    
    try:
        xml_doc = etree.fromstring(xml)
        xslt_doc = etree.fromstring(xslt)
        xslt_proc = etree.XSLT(xslt_doc)
        
        result = xslt_proc(xml_doc, **params)
        return unicode(result)
    except RuntimeError as e:
        raise XsltError(str(e))
    
def transform(xml, xslt, params=None):
    """transform the xml using the xslt"""
    try:
        return _transform_libxslt(xml, xslt, params)
    except ImportError:
        pass
    
    try:
        return _transform_lxml(xml, xslt, params)
    except ImportError:
        pass
        
    return _transform_libxsltmod(xml, xslt, params)

def prepare_string_param(string):    
    result = u"'%s'" % (string.replace("'","&apos;") or '')
    return result.encode('utf-8')
    
