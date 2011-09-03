"""
Fields to be used in models.
"""
import logging
import os
import re
import warnings
from StringIO import StringIO
from time import time
from urllib import urlopen
from xml import sax

from django.conf import settings
from django.contrib.admin.widgets import AdminTextInputWidget, AdminTextareaWidget
from django.db import connection, models
from django.db.models import CharField, TextField
from django.forms import fields
from django.utils.datastructures import DictWrapper
from django.utils.translation import ugettext_lazy as _
from tinymce.widgets import TinyMCE

from easymode.admin.forms import fields as form_fields
from easymode.utils import xmlutils


try:
    import tinymce
except ImportError:
    warnings.warn(
        """
        Without tinymce most of the fields related to rich text do not work, 
        this will also cause some of tests to fail!!
        http://code.google.com/p/django-tinymce/
        """
    )



__all__ = ('FlashUrlField', 'RelativeFilePathField', 'XmlField', 'SafeTextField', 'SafeHTMLField'
)

DEFAULT_MCE_CONFIG = None
if hasattr(settings, 'TINYMCE_DEFAULT_CONFIG'):
    DEFAULT_MCE_CONFIG = settings.TINYMCE_DEFAULT_CONFIG.get('theme_advanced_buttons1')

class FlashUrlField(CharField):
    """
    A field that is an url in flash.
    
    A valid flash url must be one of:
    
    1. an absolute url, eg. *http://example.com/*
    2. a relative url, eg. */main/chapter* 
    3. a flash url with a hash eg. *#/main/chapter*
    """
    
    _south_introspects = True

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = kwargs.pop('max_length', 512)
        super(FlashUrlField, self).__init__(*args, **kwargs)
    
    def get_internal_type(self):
        return self.__class__.__name__

    def db_type(self, connection):
        data = DictWrapper(self.__dict__, connection.ops.quote_name, "qn_")
        try:
            return connection.creation.data_types['CharField'] % data
        except KeyError:
            return None

    def formfield(self, **kwargs):
        defaults = {
            'form_class': form_fields.FlashUrlField,
            'max_length': self.max_length or 512,
            'error_messages': {
                'invalid': _('Alleen valide urls of relative flash urls die beginnen met #/ zijn geoorloofd')
            }
        }
        defaults.update(kwargs)
        return super(FlashUrlField, self).formfield(**defaults)

class SafeTextField(models.TextField):
    """
    Removes all cariage returns from the input.

    This class should be used instead of :class:`django.db.models.TextField`, if you
    want to use easymode's gettext facilities. It will strip all cariage returns from
    the input. Cariage returns are an error when included in gettext message id's. It
    also allows you to specify the number of rows and columns of the textarea.
    
    :param rows: The number of rows of the textarea.
    :param cols: The number of columns of the textarea.
    """

    _south_introspects = True
    
    def __init__(self, *args, **kwargs):
        self.rows = kwargs.pop('rows', 5)
        self.cols = kwargs.pop('cols', 40)
        
        super(SafeTextField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'widget': AdminTextareaWidget(attrs={'rows':self.rows, 'cols':self.cols}),
            'form_class': form_fields.PoSafeTextField
        }
        defaults.update(kwargs)
        return super(SafeTextField, self).formfield(**defaults)


class SafeHTMLField(TextField):
    """
    A html field with the following properties:

    1. Escapes cariage returns
    2. Will render as html, without escaping &lt; and &gt;
    3. Validates that html and will log errors when invalid html 
       is discovered, instead of crash.
    4. Allows the max_length attribute, the max_length is then computed,
       without counting markup. Also html entities are converted to normal
       characters before measuring the length as well.
    5. accepts tinymce configuration options.

    usage::

        html = SafeHTMLField(_('some rich text'), max_length=200, width=300, height=100, buttons="link,unlink,code")

    :param max_length: The maximum length of the text, after stripping markup and
        converting html entities to normal characters.
    :param width: The width of the html editor in the admin
    :param height: The height of the html editor in the admin
    :param buttons: Configuration for the 
        `theme_advanced_buttons1 <http://wiki.moxiecode.com/index.php/TinyMCE:Configuration/theme_advanced_buttons_1_n>`_. 
        The default is "bullist,numlist,|,undo,redo,|,link,unlink,|,code,|,cleanup,removeformat".
    """
    _south_introspects = True

    def __init__(self, *args, **kwargs):
        mce_config = DEFAULT_MCE_CONFIG or \
            "bullist,numlist,|,undo,redo,|,link,unlink,|,code,|,cleanup,removeformat"
        
        self.mce_width = kwargs.pop('width', 340)
        self.mce_height = kwargs.pop('height', 160)
        self.buttons = kwargs.pop('buttons', mce_config)
        
        super(SafeHTMLField, self).__init__(*args, **kwargs)

    def __serialize__(self, obj, xml):
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
            'theme_advanced_buttons1' : self.buttons,
            'theme_advanced_resizing' : True,
            'width': self.mce_width,
            'height': self. mce_height,
        }

        defaults = {
            'form_class': form_fields.PoSafeTextField,
        }

        # if this thing has a max_length then use a 
        # special form field
        if hasattr(self, 'max_length'):
            defaults['form_class'] = form_fields.HtmlEntityField
            defaults['max_length'] = self.max_length

        defaults.update(kwargs)
        defaults['widget'] = TinyMCE(mce_attrs=mce_default_attrs)
        
        return super(SafeHTMLField, self).formfield(**defaults)


class RelativeFilePathField(fields.ChoiceField):
    """
    A FilePathField which stores paths as relative paths.
    
    :param base: The base path, this base path will **NOT** be in the database (eg. settings.PROJECT_DIR).
    :param relative_path: The relative part of the path, which will be in the database, together with the filename.
    """
    
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


class XmlField(models.TextField):
    """
    Used to store XML.
    
    When using :func:`easymode.tree.xml`, all data is escaped and
    html tags are turned into entities. Using this field will make
    sure the escaping is skipped, so xml is rendered unmodified.
    """
    
    _south_introspects = True

    def __init__(self, *args, **kwargs):
        super(XmlField, self).__init__(*args, **kwargs)
    
    def __serialize__(self, obj, xml):                
        """Parse the value of this field as xml and add nodes to the serializer tree"""
        value = self.value_to_string(obj).encode('utf-8')
        parser = sax.make_parser(["easymode.utils.xmlutils"])
        parser.setContentHandler(xml)
        parser.parse(StringIO(value))
