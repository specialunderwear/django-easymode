from django.core.urlresolvers import reverse
from django.forms import IntegerField
from django.forms.models import BaseInlineFormSet
from django.utils.translation import force_unicode

from easymode.tree.admin.widgets.foreignkey import LinkWidget


class RecursiveInlineFormSet(BaseInlineFormSet):
    """
    A formset that can be used to make the primary key field visible in an
    InlineModelAdmin form.
    """
    
    PRIMARY_KEY_WIDGET = LinkWidget
    
    def add_fields(self, form, index):
        super(RecursiveInlineFormSet, self).add_fields(form, index)
        
        # get the primary key and it's options
        hidden_pk_field = form.fields[self._pk_field.name]
        options =  hidden_pk_field.queryset.model._meta
        
        # the only fields that must show is the primary key
        form._meta.fields = [self._pk_field.name]
        
        widget_attrs = {}
        
        # show the link widget if the item allready exists
        if hidden_pk_field.initial is not None: 
            widget_attrs['url'] = reverse('admin:%s_%s_change' % (options.app_label, options.object_name.lower()), args=[hidden_pk_field.initial])
            widget_attrs['label'] = 'Edit %s' % force_unicode(options.verbose_name)
            
        # if the parent model exists but the item doesn't show the add button
        elif self.instance.pk is not None:
            url = reverse('admin:%s_%s_add' % (options.app_label, options.object_name.lower()))
            widget_attrs['url'] = '%s?%s=%s' % (url, self.fk.name, self.instance.pk)
            widget_attrs['label'] = 'Add %s' % force_unicode(options.verbose_name)
            widget_attrs['popup'] = True
            
        # if the parent model does not exist use an empty link widget.
        else:
            widget_attrs['url'] = None
            widget_attrs['label'] = ''
        
        # turn the primary key into a field that displays a fieldset with a link
        form.fields[self._pk_field.name] = IntegerField(hidden_pk_field.queryset, 
            initial=hidden_pk_field.initial, required=False,
            widget=self.PRIMARY_KEY_WIDGET(attrs=widget_attrs)
        )
