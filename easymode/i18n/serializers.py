"""
Contains serializers that also serialize translated fields
"""
import logging; 
from StringIO import StringIO

from django.core.serializers import base

from django.conf import settings
from django.utils.encoding import smart_unicode

from easymode.tree.introspection import get_default_field_descriptors
from easymode.utils.xmlutils import XmlPrinter

# startDocument must only be called once
# so override it
def startDocumentOnlyOnce(self):
    if hasattr(self, 'allready_called'):
        return
    self.allready_called = True
    XmlPrinter.startDocument(self)

XmlPrinter.startDocument = startDocumentOnlyOnce

class LocalizedSerializer(base.Serializer):
    """
    Serializes a queryset including translated fields
    THE OUTPUT OF THIS SERIALIZER IS NOT MEANT TO BE SERIALIZED BACK
    INTO THE DB.
    """
    
    def serialize(self, queryset, **options):
        # don't cause cyclic import
        # from easymode.tree.introspection import get_default_field_descriptors

        """
        Serialize a queryset.
        """
        self.options = options

        self.stream = options.get("stream", StringIO())
        self.selected_fields = options.get("fields")
        
        self.xml = options.get("xml", None)
        self.root = (self.xml == None)
        
        self.start_serialization()
        for obj in queryset:
            self.start_object(obj)
            for field in obj._meta.local_fields:
                if field.serialize and field.name in obj.localized_fields:
                    if field.rel is None:
                        if self.selected_fields is None or field.attname in self.selected_fields:
                            self.handle_field(obj, field)
                    else:
                        if self.selected_fields is None or field.attname[:-3] in self.selected_fields:
                            self.handle_fk_field(obj, field)
            
            #serialize the default field descriptors:
            for default_field_descriptor in get_default_field_descriptors(obj):
               self.handle_field(obj, default_field_descriptor[1])
                
            for field in obj._meta.many_to_many:
                if field.serialize:
                    if self.selected_fields is None or field.attname in self.selected_fields:
                        self.handle_m2m_field(obj, field)
            self.end_object(obj)
        self.end_serialization()
        return self.getvalue()
        
    def indent(self, level):
        if self.options.get('indent', None) is not None:
            self.xml.ignorableWhitespace('\n' + ' ' * self.options.get('indent', None) * level)

    def start_serialization(self):
        """
        Start serialization -- open the XML document and the root element.
        """
        if (self.root):
            self.xml = XmlPrinter(self.stream, self.options.get("encoding", settings.DEFAULT_CHARSET))
            self.xml.startDocument()
            self.xml.startElement("django-objects", {"version" : "1.0"})

    def end_serialization(self):
        """
        End serialization -- end the document.
        """
        if (self.root):
            self.indent(0)
            self.xml.endElement("django-objects")
            self.xml.endDocument()

    def start_object(self, obj):
        """
        Called as each object is handled.
        """
        if not hasattr(obj, "_meta"):
            raise base.SerializationError("Non-model object (%s) encountered during serialization" % type(obj))

        self.indent(1)
        self.xml.startElement("object", {
            "pk"    : smart_unicode(obj._get_pk_val()),
            "model" : smart_unicode(obj._meta),
        })

    def end_object(self, obj):
        """
        Called after handling all fields for an object.
        """
        self.indent(1)
        self.xml.endElement("object")

    def handle_field(self, obj, field):
        """
        Called to handle each field on an object (except for ForeignKeys and
        ManyToManyFields)
        """
        self.indent(2)

        # handle fields with a font set as speciul
        if getattr(field, 'font', None):
            logging.debug('has font %s' % field.name)
            self.xml.startElement("field", {
                "name" : field.name.replace('_', '.'),
                "type" : field.get_internal_type(),
                "font" : field.font
            })            
        elif getattr(field, 'styles', None):
            logging.debug('has styles %s' % field.name)
            self.xml.startElement("field", {
                "name" : field.name.replace('_', '.'),
                "type" : field.get_internal_type(),
                "style" : ",".join(field.styles)
            })
        else:
            self.xml.startElement("field", {
                "name" : field.name,
                "type" : field.get_internal_type()
            })

        # Checks for a custom value serializer 
        if not hasattr(field, 'custom_value_serializer'):
            # Get a "string version" of the object's data.
            if getattr(obj, field.name) is not None:
                self.xml.characters(field.value_to_string(obj))
            else:
                self.xml.addQuickElement("None")
        else:
            field.custom_value_serializer(obj, self.xml)

        self.xml.endElement("field")

    def handle_fk_field(self, obj, field):
        """
        Called to handle a ForeignKey (we need to treat them slightly
        differently from regular fields).
        """
        self._start_relational_field(field)
        related = getattr(obj, field.name)
        if related is not None:
            if field.rel.field_name == related._meta.pk.name:
                # Related to remote object via primary key
                related = related._get_pk_val()
            else:
                # Related to remote object via other field
                related = getattr(related, field.rel.field_name)
            self.xml.characters(smart_unicode(related))
        else:
            self.xml.addQuickElement("None")
        self.xml.endElement("field")

    def handle_m2m_field(self, obj, field):
        """
        Called to handle a ManyToManyField. Related objects are only
        serialized as references to the object's PK (i.e. the related *data*
        is not dumped, just the relation).
        """
        if field.creates_table:
            self._start_relational_field(field)
            for relobj in getattr(obj, field.name).iterator():
                self.xml.addQuickElement("object", attrs={"pk" : smart_unicode(relobj._get_pk_val())})
            self.xml.endElement("field")

    def _start_relational_field(self, field):
        """
        Helper to output the <field> element for relational fields
        """
        self.indent(2)
        self.xml.startElement("field", {
            "name" : field.name,
            "rel"  : field.rel.__class__.__name__,
            "to"   : smart_unicode(field.rel.to._meta),
        })

    def getvalue(self):
        """
        Return the fully serialized queryset (or None if the output stream is
        not seekable).
        """
        if callable(getattr(self.stream, 'getvalue', None)):
            return self.stream.getvalue()

def serialize_with_locale(queryset):
    """serialize queryset including localised fields"""
    ser = LocalizedSerializer()
    return ser.serialize(queryset)
