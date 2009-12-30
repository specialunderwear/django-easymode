import re
import StringIO
import htmlentitydefs

from django.utils.xmlutils import SimplerXMLGenerator

from xml.sax.expatreader import ExpatParser
from xml.sax.handler import EntityResolver

entities = re.compile(r'&([^;]+);')

__all__ = ('unescape_all', 'XmlScanner', 'XmlPrinter', 'create_parser')

def _unicode_for_entity_with_name(name):
    latin1 = htmlentitydefs.entitydefs[name]
    return latin1.decode('iso-8859-1')

def unescape_all(string):
    """docstring for unescape_all"""
    def escape_single(matchobj):
        return _unicode_for_entity_with_name(matchobj.group(1))
    return entities.sub(escape_single, string)
    
class XmlScanner(ExpatParser):
    """
    This class is an xml parser that can will not throw errors
    when unknown entities are found.
    
    It can be used like:
    >>> sax.make_parser("easymode.utils.xmlutils").
    
    It works by making all unknown entities be skipped.
    This will trigger skippedEntity on the contentHandler.
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
    XmlPrinter can be used as a contenthandler for the XmlScanner.
    
    It will then just copy all skippedEntities to the output stream.
    """
    def skippedEntity(self, name):
        self._out.write(_unicode_for_entity_with_name(name).encode('utf-8'))

def create_parser(*args, **kwargs):
    return XmlScanner(*args, **kwargs)
