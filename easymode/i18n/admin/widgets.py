from django.utils.safestring import mark_safe
from django.contrib.admin.widgets import RelatedFieldWidgetWrapper

__all__ = ('WidgetWrapper',)

def find_extra_attrs(value):
    "finds extra attributes in *value* if they are there"
    extra = None
    if hasattr(value, 'stored_value'):
        if hasattr(value, 'msg') and value.stored_value != value.msg:
            extra = value.msg
        elif hasattr(value, 'fallback') and value.stored_value != value.fallback:
            extra = value.fallback
            
    return extra

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
        extra = find_extra_attrs(value)
        widget_html = self.widget.render(name, value, *args, **kwargs)
        
        if extra:
            return mark_safe(u'<div class="localized catalog-has-different-data">%s <small><a class="extra-catalog-data" title="%s">%s%s</a></small></div>' % (widget_html, extra, unichr(8756), unichr(176)))

        return mark_safe(u'<div class="localized">%s <small>%s</small></div>' % (widget_html, unichr(8756)))
