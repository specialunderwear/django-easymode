"""
Contains formsets where the add_fields method does not hide 
the autofield.
"""
from django.forms.models import BaseModelFormSet
from django.forms import IntegerField
from django.forms.formsets import BaseFormSet
from django.utils.translation import ugettext_lazy as _

from easymode.tree.admin.widgets.foreignkey import RenderLink

class VisiblePrimaryKeyFormset(BaseModelFormSet):
    """
    This formset will show the primary keys instead of hide it.
    """
    def add_fields(self, form, index):

        self._pk_field = self.model._meta.pk

        if form.is_bound:
            pk_value = form.instance.pk
        else:
            try:
                pk_value = self.get_queryset()[index].pk
            except IndexError:
                pk_value = None

        attrs = dict(app_label=self.model._meta.app_label, modelname=self.model.__name__.lower(), label=unicode(form.instance))
        form.fields[self._pk_field.name] = IntegerField( initial=pk_value, required=False, 
                                                         widget=RenderLink(attrs=attrs), label=_("Navigate to:"))

        BaseFormSet.add_fields(self, form, index)
