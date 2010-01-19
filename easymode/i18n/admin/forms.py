from django import forms
from django.forms.models import fields_for_model
from django.utils.datastructures import SortedDict
from django.forms.util import ErrorList
from django.utils.translation import get_language

class LocalisedForm(forms.ModelForm):
    """
    This form will show the DefaultFieldDescriptor as a field.
    The DefaultFieldDescriptor is added for models that are internationalised
    with the I18n descriptor.
    """
        
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None, js=None):
        
        locale_data = initial or SortedDict()

        # get all localized fields and their values
        if instance is not None:
            for localized_field in instance.localized_fields:
                if initial: # get value from initial if it is defined
                    local_name = "%s_%s" % (localized_field, get_language()) 
                    locale_data[localized_field] = initial.get(local_name, getattr(instance, localized_field))
                else:
                    locale_data[localized_field] = getattr(instance, localized_field)
            
        super(LocalisedForm, self).__init__(data, files, auto_id, prefix, locale_data,
                                            error_class, label_suffix, empty_permitted, instance)
                                              
    def save(self, commit=True):
        """
        Override save method to also save the localised fields.
        """
        # set the localised fields
        for localized_field in self.instance.localized_fields:
            setattr(self.instance, localized_field, self.cleaned_data[localized_field])

        return super(LocalisedForm, self).save(commit)


def make_localised_form(model, exclude=None):
    """
    This is a factory function that creates a form for a model with internationalised 
    field. The model should be decorated with the L10N decorater.
    """
    newfields = fields_for_model(model, None, exclude)
    js_media = set()
    
    for localized_field in model.localized_fields:
        # use the original formfield for all DefaultFieldDescriptors
        default_field_descriptor = getattr(model, localized_field)
        form_field = default_field_descriptor.form_field
        form_field.descriptor = form_field
        newfields[localized_field] = form_field
        #collect js media definitions
        if hasattr(form_field.widget, 'media'):
            js_media.update(form_field.widget.media._js)
        
    newfields['Media'] = type('Media', tuple(), {'js':js_media})

    return type(model.__name__, (LocalisedForm, ), newfields)
