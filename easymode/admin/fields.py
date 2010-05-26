"""
form and model fields, for integration with diocore as3 framework,
and others.

This documentation is not finished. The classes in this file
will be moved to other files. Take care when using them.
"""
import re
import os
import logging
from StringIO import StringIO
from time import time
from xml import sax
from urlparse import urljoin
from urllib import urlopen

from django.db import connection, models
from django.db.models import CharField, TextField
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import DictWrapper
from django.forms import ValidationError
from django.conf import settings
from django.forms import fields
from django.contrib.sites.models import Site
from django.utils.encoding import smart_unicode
from django.utils.html import strip_tags
from django.contrib.admin.widgets import AdminTextInputWidget, AdminTextareaWidget

from tinymce.widgets import TinyMCE

from easymode.utils import xmlutils

############################################################################
# form fields
############################################################################

class PoSafeTextField(fields.CharField):
    """
    Having carriage return in po files is an error.
    Ths field's clean function will strip these ugly
    characters from the input.
    """

    def clean(self, value):
        return super(PoSafeTextField, self).clean(value.replace('\r',''))
    
class HtmlEntityField(fields.CharField):
    """
    A form field that can validate the length of a rich text field.
    
    It ignores html markup and it counts html entities as only a single
    character.
    """
    def clean(self, value):
        value = value.replace('\r','')
        tagless_value = strip_tags(value)
        entityless_value = re.sub(r'&[^;]+;', 'X', tagless_value)

        # validate using super class
        super(HtmlEntityField, self).clean(entityless_value)
        # return unmodified value, but normalize line endings.
        return smart_unicode(value)

class FlashUrlField(fields.URLField):
    """A field that validates input to be either an absolute or a flash url with a hash"""

    def clean(self, value):
        try:
            cleaned_value = super(FlashUrlField, self).clean(value)
        except ValidationError:
            if re.match(r'^#/', value):
                return value
            elif re.match(r'^/\S+$', value):
                return value
            else:
                raise ValidationError(self.error_messages['invalid'])

        return cleaned_value

############################################################################
# model fields
############################################################################


# When using Field the test enigine will not create the url attribute
# For now used very dirty workaround; extending CharField
class HtmlFlashUrlField(CharField):
    
    _south_introspects = True

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.pop('max_length', 512)
        super(HtmlFlashUrlField, self).__init__(*args, **kwargs)
    
    def custom_value_serializer(self, obj, xml):
        '''Custom serializer for easymode.'''

        current_site = Site.objects.get_current()        
        base = getattr(settings, 'BASE_URL', 'http://' + current_site.name + '/')
        url = self.value_to_string(obj).strip('/')

        if re.match(r'^#/', url): # it is a flash url
            reload_url = urljoin(base, url)
            url = re.sub(r'^#/','',url)            
            html_url = urljoin(base, url + '.html')
        else: # it is a normal url
            url = html_url = reload_url = urljoin(base, url)
            
        xml.startElement('url-html', { 'value': html_url })
        xml.endElement('url-html')

        xml.startElement('url-flash', { 'value': url })
        xml.endElement('url-flash')
        
        xml.startElement('url-reload-flash', {'value': reload_url})
        xml.endElement('url-reload-flash')

    def get_internal_type(self):
        """return the type of this field"""
        return self.__class__.__name__

    def db_type(self):
        data = DictWrapper(self.__dict__, connection.ops.quote_name, "qn_")
        try:
            return connection.creation.data_types["CharField"] % data
        except KeyError:
            return None

    def formfield(self, **kwargs):
        """overrides the formfield"""
        defaults = {
            'form_class': FlashUrlField,
            'max_length': self.max_length or 512,
            'error_messages': {
                'invalid': _('Alleen valide urls of relative flash urls die beginnen met #/ zijn geoorloofd')
            }
        }
        defaults.update(kwargs)
        return super(HtmlFlashUrlField, self).formfield(**defaults)


class DiocoreCharField(CharField):
    """
    This charfield stores a font as well.
    Also it will replace underscores in it's name with '.'s
    The serializer is built to detect this and will add the font as
    an attribute in the xml.
    """
    
    _south_introspects = True
    
    def __init__(self, *args, **kwargs):
        self.font = kwargs.pop('font', None)
        super(DiocoreCharField, self).__init__(*args, **kwargs)
    
    def formfield(self, **kwargs):
        defaults = {
            'widget': AdminTextInputWidget
        }
        defaults.update(kwargs)
        return super(DiocoreCharField, self).formfield(**defaults)
        
class DiocoreHTMLField(TextField):
    """
    This textfield stores a font as well.
    Also it will replace underscores in it's name with '.'s
    The serializer is built to detect this and will add the font as
    an attribute in the xml.
    """
    
    _south_introspects = True
    
    def __init__(self, *args, **kwargs):
        self.font = kwargs.pop('font', None)
        self.mce_width = kwargs.pop('width', 340)
        self.mce_height = kwargs.pop('height', 160)
        self.buttons = kwargs.pop('buttons', "bullist,numlist,|,undo,redo,|,link,unlink,|,code,|,cleanup,removeformat,code")

        super(DiocoreHTMLField, self).__init__(*args, **kwargs)
        
    def custom_value_serializer(self, obj, xml):
        richtext = self.value_to_string(obj)
        value = u"<richtext>%s</richtext>"  % richtext
        
        if xmlutils.is_valid(value):
            parser = sax.make_parser(["easymode.utils.xmlutils"])
            parser.setContentHandler(xml)
            parser.parse(StringIO(value.encode('utf-8')))            
        else:
            logging.error('Invalid xml in %s: %s' % (obj, value))
    
    def formfield(self, **kwargs):
        mce_default_attrs = {
            'theme_html_buttons1' : self.buttons,
            'theme_advanced_resizing' : True,
            'width': self.mce_width,
            'height': self. mce_height,
        }
    
        defaults = {
            'form_class': PoSafeTextField,
        }
        
        # if this thing has a max_length then use a 
        # special form field
        if hasattr(self, 'max_length'):
            defaults['form_class'] = HtmlEntityField
            defaults['max_length'] = self.max_length
            
        defaults.update(kwargs)
        defaults['widget'] = TinyMCE(mce_attrs=mce_default_attrs)
        
        return super(DiocoreHTMLField, self).formfield(**defaults)


class CSSField(DiocoreHTMLField):
    """
    A field adds a *style* property when serialized by easymode.
    
    .. code-block:: xml
    
        <field type="CharField" name="title" style="large,at-left">Hi</field>
        
        
    """
    def __init__(self, *args, **kwargs):
        self.styles = kwargs.pop('styles', None)
        self.mce_width = kwargs.pop('width', 340)
        self.mce_height = kwargs.pop('height', 160)
        self.buttons = kwargs.pop('buttons', "bullist,numlist,|,undo,redo,|,link,unlink,|,code,|,cleanup,removeformat,code")

        TextField.__init__(self, *args, **kwargs)
    
class DiocoreTextField(TextField):
    """
    This textfield stores a font as well.
    Also it will replace underscores in it's name with '.'s
    The serializer is built to detect this and will add the font as
    an attribute in the xml.
    """

    _south_introspects = True
    
    def __init__(self, *args, **kwargs):
        self.font = kwargs.pop('font', None)
        super(DiocoreTextField, self).__init__(*args, **kwargs)
        
    def formfield(self, **kwargs):
        defaults = {
            'widget': AdminTextareaWidget,
            'form_class': PoSafeTextField,
        }
        defaults.update(kwargs)
        return super(DiocoreTextField, self).formfield(**defaults)

class RelativeFilePathField(fields.ChoiceField):
    """A FilePathField which stores paths as relative paths"""
    
    _south_introspects = True
    
    def __init__(self, base, relative_path, match=None, recursive=False, required=True,
                 widget=None, label=None, initial=None, help_text=None, path='',
                 *args, **kwargs):

        self.base, self.relative_path, self.match, self.recursive = base, relative_path, match, recursive

        super(RelativeFilePathField, self).__init__(choices=(), required=required,
            widget=widget, label=label, initial=initial, help_text=help_text,
            *args, **kwargs)

        if self.required:
            self.choices = []
        else:
            self.choices = [("", "---------")]

        if self.match is not None:
            self.match_re = re.compile(self.match)

        if recursive:
            for root, dirs, files in os.walk(self.path):
                for f in files:
                    if self.match is None or self.match_re.search(f):
                        f = os.path.join(root, f)
                        self.choices.append((f.replace(self.base, ""), f.replace(self.path, "", 1)))
        else:
            try:
                for f in os.listdir(self.path):
                    full_file = os.path.join(self.path, f)
                    if os.path.isfile(full_file) and (self.match is None or self.match_re.search(f)):
                        self.choices.append((os.path.join(self.relative_path, f), f))
            except OSError:
                pass

        self.widget.choices = self.choices

    @property
    def path(self):
        return os.path.join(self.base, self.relative_path)
        
        
class IncludeFileField(models.FilePathField):
    """
    This field will include the contents of the file it references when serialized by
    any descendant of easymode.i18n.serializers.LocalizedSerializer.
    """
    
    _south_introspects = True
    
    def __init__(self, verbose_name=None, name=None, base='', relative_path='', match=None, recursive=False, **kwargs):
        self.base, self.relative_path, self.match, self.recursive = base, relative_path, match, recursive
        kwargs['max_length'] = kwargs.get('max_length', 100)
        super(IncludeFileField, self).__init__(verbose_name, name, **kwargs)
        
    def custom_value_serializer(self, obj, xml):
        file_path = os.path.join(self.base, self.value_to_string(obj))
        if os.path.isfile(file_path):
            file_content = sax.make_parser()
            file_content.setContentHandler(xml)
            file_content.parse(file_path)
    
    def formfield(self, **kwargs):
        defaults = {
            'base': self.base,
            'relative_path': self.relative_path,
            'match': self.match,
            'recursive': self.recursive,
            'form_class': RelativeFilePathField,
        }
        defaults.update(kwargs)
        return super(IncludeFileField, self).formfield(**defaults)

class RemoteIncludeField(models.URLField):
    """
    Open an url and include the result in the xml when serialized.
    Same as the IncludeFileField but then a remote file.
    Also it caches the request and only get the result once ever 'interval'.
    interval is a setting that can be used when constructing the field.
    """
    
    _south_introspects = True
    
    def get_internal_type(self):
        """return the type of this field"""
        return self.__class__.__name__

    def db_type(self):
        data = DictWrapper(self.__dict__, connection.ops.quote_name, "qn_")
        try:
            return connection.creation.data_types["CharField"] % data
        except KeyError:
            return None
            
    def __init__(self, *args, **kwargs):
        self.interval = kwargs.pop('interval', 10 * 60)
        self._cached_data_url = None
        super(RemoteIncludeField, self).__init__(*args, **kwargs)

    def custom_value_serializer(self, obj, xml):
        '''Custom serializer for easymode.'''

        url = self.value_to_string(obj)

        if ( not hasattr(self, '_cached_data') or
             self._cached_data_url                != url or
             time() - self._cached_data_timestamp >  self.interval ):
            
            try:
                self._cached_data           = urlopen(url).read()
                self._cached_data_url       = url
                self._cached_data_timestamp = time()                
            except IOError:
                self._cached_data = "<root>file not found</root>"

        file_content = sax.make_parser()
        file_content.setContentHandler(xml)
        file_content.parse(StringIO(self._cached_data))

class XmlField(models.TextField):
    """
    This field will make sure that when it is serialized the content
    will not be escaped to html entities. As such kepping the xml.
    """
    
    _south_introspects = True
    
    def custom_value_serializer(self, obj, xml):                
        """Parse the value of this field as xml and add nodes to the serializer tree"""
        value = self.value_to_string(obj).encode('utf-8')
        parser = sax.make_parser(["easymode.utils.xmlutils"])
        parser.setContentHandler(xml)
        parser.parse(StringIO(value))

class SafeTextField(models.TextField):
    """
    This class should be used instead of :class:`django.db.models.TextField`, if you
    want to use easymode's gettext facilities. It will strip all cariage returns from
    the input. Cariage returns are an error when included in gettext message id's.
    """
    def formfield(self, **kwargs):
        defaults = {'form_class': PoSafeTextField}
        defaults.update(kwargs)
        return super(SafeTextField, self).formfield(**defaults)