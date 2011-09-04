"""
Contains widgets that can be used for admin models
with related items.
"""
from django import forms
from django.conf import settings
from django.core import urlresolvers
from django.forms import widgets
from django.template.loader import render_to_string
from django.utils.encoding import force_unicode
from django.utils.html import mark_safe
from django.utils.translation import ugettext

from easymode.utils.languagecode import strip_language_code

__all__ = ('RenderLink', 'LinkWidget')

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


class LinkWidget(widgets.TextInput):
    """
    A widget that renders only a link the change view or edit view of an object.
    """
    def _has_changed(self, initial, data):
        return False

    def render(self, name, value, attrs=None):
        # dress up the widget as a field, so it can be rendered by 'admin/includes/fieldset.html'
        fieldset = [[self]]

        if value is None:
            value = ''
        if value != '':
            value = force_unicode(self._format_value(value))

        # store values, they will be needed in self.field later on
        self.value = value
        self.name = name
        
        return render_to_string('admin/includes/fieldset.html', {'fieldset':[[self,]]})

    def field(self):
        # the whole widget is based entirely on the fact that *render* gets called
        # BEFORE *field*. And that is true because field is called by the rendering
        # done in *render*.
        context = {
            'name':self.name,
            'value':self.value,
            'description': ugettext('Change'),
            'ADMIN_MEDIA_PREFIX':settings.ADMIN_MEDIA_PREFIX,
        }
        
        context.update(self.attrs)
        if self.attrs.get('popup', False):
            return render_to_string('tree/admin/widgets/add_widget.html', context)
        
        return render_to_string('tree/admin/widgets/link_widget.html', context)

    def label_tag(self):
        return mark_safe(u'<label class="required">%s</label>' % self.attrs['label'] )

