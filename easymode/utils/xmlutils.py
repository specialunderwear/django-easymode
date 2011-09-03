"""
Contains classes and functions for dealing with html entities.

You need this as soon as you are doing anything with rich
text fields and want to use :func:`easymode.tree.xml.decorators.toxml`.
"""
import re
import StringIO
import htmlentitydefs

from django.utils.xmlutils import SimplerXMLGenerator

from xml.sax.expatreader import ExpatParser
from xml.sax import SAXParseException
from xml.sax.handler import EntityResolver, ContentHandler

entities = re.compile(r'&([^;]+);')

__all__ = ('unescape_all', 'XmlScanner', 'XmlPrinter', 'create_parser')

def _unicode_for_entity_with_name(name):
    # if the entity is unknown, insert question mark
    codepoint = htmlentitydefs.name2codepoint.get(name, 63)
    return unichr(codepoint)
   
def unescape_all(string):
    """Resolve all html entities to their corresponding unicode character"""
    def escape_single(matchobj):
        return _unicode_for_entity_with_name(matchobj.group(1))
    return entities.sub(escape_single, string)

def is_valid(xml_string):
    """validates a unicode string containing xml"""
    xml_file = StringIO.StringIO(xml_string.encode('utf-8'))
    
    parser = XmlScanner()
    parser.setContentHandler(ContentHandler())
    try:
        parser.parse(xml_file)
    except SAXParseException:
        return False
    
    return True
    
class XmlScanner(ExpatParser):
    """
    This class is an xml parser that will not throw errors
    when unknown entities are found.
    
    It can be used as follows::
    
        parser = sax.make_parser(["easymode.utils.xmlutils"])
    
    All entities that can not be resolved will be skipped.
    This will trigger skippedEntity on the contentHandler.
    
    A good contenthandler for this scanner is
    :class:`~easymode.utils.xmlutils.XmlPrinter` because it
    will turn these entities into their unicode characters.
    """
    def __init__(self, *args, **kwargs):
        """docstring for __init__"""
        ExpatParser.__init__(self, *args, **kwargs)
        
        class _NiftyEntityResolver(EntityResolver):
            """
            _NiftyEntityResolver makes the entity errors disappear.
            
            It works by the html spec which says that external entities that
            can not resolved, do not have to be reported as an error by a non
            validating parser.
            """
            def resolveEntity(self, publicId, systemId):
                "This will be called with None, None if it is an unknown entity"
                if systemId or publicId:
                     return EntityResolver.resolveEntity(self,publicId,systemId)
                
                # return an empty stringio in which the parser can never find
                # the entities. This will make it skip the entity, which triggers
                # skippedEntity in the contenthandler.
                return StringIO.StringIO(" ") # if you delete that single space you will be sorry.
        
        self.setEntityResolver(_NiftyEntityResolver())
        
    def reset(self):
        ExpatParser.reset(self)
        # This line makes the parser think unknown
        # entities are external.
        self._parser.UseForeignDTD(True)
    
   
    
class XmlPrinter(SimplerXMLGenerator):
    """
    XmlPrinter can be used as a contenthandler for the 
    :class:`~easymode.utils.xmlutils.XmlScanner`.
    
    It will convert all skippedEntities to their unicode characters
    and copy these to the output stream.
    
    You can use it as a simple xml generator, to create xml::
    
        stream = StringIO.StringIO()
        xml = XmlPrinter(stream, settings.DEFAULT_CHARSET)

        def _render_page(page):
            xml.startElement('title', {})
            xml.characters(page.title)
            xml.endElement('title')
            xml.startElement('template', {})
            xml.characters(page.template)
            xml.endElement('template')
        
        for child in Page.children.all():
            xml.startElement('page', {})
            _render_page(child)
            xml.endElement('page')
    """
    def skippedEntity(self, name):
        self._out.write(_unicode_for_entity_with_name(name).encode('utf-8'))

def create_parser(*args, **kwargs):
    """
    Because this function is defined, you can create an 
    :class:`~easymode.utils.xmlutils.XmlScanner` like this::
        
        from xml import sax
        
        parser = sax.make_parser(["easymode.utils.xmlutils"])
    """
    return XmlScanner(*args, **kwargs)
