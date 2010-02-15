import copy

from django.forms.widgets import MediaDefiningClass, Widget
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

class WidgetWrapper(RelatedFieldWidgetWrapper):
    """
    This class is a wrapper to a given widget to add the add icon for the
    admin interface.
    """
    def __init__(self, widget, **kwargs):            
        if type(widget) is WidgetWrapper:
            self.widget = widget.widget
        else:
            self.widget = widget
        
        self.is_hidden = self.widget.is_hidden
        self.needs_multipart_form = self.widget.needs_multipart_form
        self.attrs = self.widget.attrs
        self.choices = getattr(self.widget, 'choices', None)
    
    def render(self, name, value, *args, **kwargs):
        extra = u''
        if hasattr(value, 'stored_value'):
            if hasattr(value, 'msg'):
                extra = value.msg
            elif hasattr(value, 'fallback'):
                extra = value.fallback
        
        widget_html = self.widget.render(name, value, *args, **kwargs)
        return mark_safe(u'<div class="localized">%s <small>%s %s</small></div>' % (widget_html, unichr(8224), extra))
