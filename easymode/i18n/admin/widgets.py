from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

class WidgetWrapper(RelatedFieldWidgetWrapper):
    """
    This class is a wrapper to a given widget to add a marker next to
    the field, so you can see that the field is translated.
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
        widget_html = self.widget.render(name, value, *args, **kwargs)
        return mark_safe(u'<div class="localized">%s <small>%s</small></div>' % (widget_html, unichr(8756)))
