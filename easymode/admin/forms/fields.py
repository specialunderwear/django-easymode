"""
Fields to be used in forms.
"""
import re

from django.forms import ValidationError
from django.forms import fields
from django.utils.encoding import smart_unicode
from django.utils.html import strip_tags

class PoSafeTextField(fields.CharField):
    """
    Having carriage return in po files is an error.
    This field's clean function will strip these ugly
    characters from the input.
    """

    def clean(self, value):
        if value is not None:
            safe_value = value.replace('\r','')
        else:
            safe_value = value
            
        return super(PoSafeTextField, self).clean(safe_value)
    
class HtmlEntityField(fields.CharField):
    """
    A form field that can validate the length of a rich text field.
    
    It ignores html markup and it counts html entities as only a single
    character.
    """
    def clean(self, value):
        if value is not None:
            value = value.replace('\r','')
            tagless_value = strip_tags(value)
            entityless_value = re.sub(r'&[^;]+;', 'X', tagless_value)
        else:
            entityless_value = value
            value = u''
        
        # validate using super class
        super(HtmlEntityField, self).clean(entityless_value)
        # return unmodified value, but with normalized line endings.
        return smart_unicode(value)

class FlashUrlField(fields.URLField):
    """
    A field that validates input to be either 
    
    1. an absolute url, eg. *http://example.com/*
    2. a relative url, eg. */main/chapter* 
    3. a flash url with a hash eg. *#/main/chapter*
    """

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
