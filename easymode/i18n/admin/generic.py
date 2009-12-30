from django.forms.models import save_instance
from django.contrib.contenttypes.generic import BaseGenericInlineFormSet
from django.contrib.contenttypes.models import ContentType


class LocalizableGenericInlineFormSet(BaseGenericInlineFormSet):
    """
    Generic inline formset that is a bit less dumb about
    fields that are not model fields but are on the form anyway.
    """

    def save_new(self, form, commit=True):
        # Avoid a circular import.
        kwargs = {
            self.ct_field.get_attname(): ContentType.objects.get_for_model(self.instance).pk,
            self.ct_fk_field.get_attname(): self.instance.pk,
        }
        
        # try to add all data that can be used to initialize the model.
        cleaned_data = form.cleaned_data
        initial_data = dict([(key, cleaned_data[key]) for key  in cleaned_data.keys() if key in dir(self.model)])
        initial_data.update(kwargs)
        new_obj = self.model(**initial_data)
        return save_instance(form, new_obj, commit=commit)    