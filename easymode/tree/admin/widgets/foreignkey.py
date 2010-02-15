"""
Contains widgets that can be used for admin models
with related items.
"""
from django import forms
from django.template.loader import render_to_string
from django.core import urlresolvers
from django.utils.encoding import force_unicode

from easymode.utils.languagecode import strip_language_code

class RenderLink(forms.Widget):
    """
    Renders a link to an admin page based on the primary key
    value of the model.
    """
    input_type = None
    
    def _has_changed(self, initial, data):
        return False
    def id_for_label(self, id_):
        return "hmm geen idee"
        
    def render(self, name, value, attrs=None):
        
        modelname = self.attrs['modelname']
        app_label = self.attrs['app_label']
        label = self.attrs['label']
        url_pattern = '%s:%s_%s_change' % ('admin', app_label, modelname)
        
        url = strip_language_code(urlresolvers.reverse(url_pattern, args=[value]))
            
        if value is None: value = ''
        final_attrs = self.build_attrs(attrs, type=self.input_type, name=name)
        if value != '':
            # Only add the 'value' attribute if a value is non-empty.
            final_attrs['value'] = force_unicode(value)
        return render_to_string('tree/admin/widgets/foreignkeylink.html', locals())

class EmptyWidgetThatDoesNothing(forms.Widget):
    """does nothing"""
    def render(self, name, value, attrs=None):
        return render_to_string('tree/admin/widgets/foreignkeylink.html', locals())
