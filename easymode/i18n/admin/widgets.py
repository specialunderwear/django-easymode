from django.contrib.admin.widgets import RelatedFieldWidgetWrapper
from django.utils.safestring import mark_safe


__all__ = ('WidgetWrapper',)

def find_extra_attrs(value):
    "finds extra attributes in *value* if they are there"
    extra = None
    value_is_from_database = True

    if hasattr(value, 'standin_value_is_from_database'):
        value_is_from_database = value.standin_value_is_from_database

        if value.stored_value != value.msg:
            extra = value.msg
        elif value.stored_value != value.fallback:
            extra = value.fallback
    
    return extra, value_is_from_database

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
        (extra, value_is_from_database) = find_extra_attrs(value)
        widget_html = self.widget.render(name, value, *args, **kwargs)
        
        if extra and value_is_from_database:
            return mark_safe(u'<div class="localized catalog-has-different-data">%s <small><a class="extra-catalog-data" title="%s">\u2234\u207A</a></small></div>' % (widget_html, extra))
        elif not value_is_from_database:
            return mark_safe(u'<div class="localized">%s <small>\u2234\u00B0</small></div>' % widget_html)
        
        return mark_safe(u'<div class="localized">%s <small>\u2234</small></div>' % widget_html)
