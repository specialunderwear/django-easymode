from django.forms.models import ModelFormMetaclass
from django.forms.util import ErrorList, ValidationError
from django.utils.datastructures import SortedDict
from django.utils.translation import get_language

from easymode.i18n.admin.widgets import WidgetWrapper
from easymode.utils.languagecode import get_real_fieldname


__all__ = ('make_localised_form',)


class LocalisedForm(object):
    """
    This form will show the DefaultFieldDescriptor as a field.
    The DefaultFieldDescriptor is added for models that are internationalised
    with the I18n descriptor.
    """
        
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=ErrorList, label_suffix=':',
                 empty_permitted=False, instance=None, js=None):
        
        # store language so it can be used later
        self.language = get_language()
        
        locale_data = initial or SortedDict()

        # Set up the initial data for the form
        for localized_field in self.localized_fields:
            # determine localized name of the field, because it is called like
            # that in the initial dict
            local_name = get_real_fieldname(localized_field, self.language)

            if initial: # get value from initial if it is defined
                initial_value = initial.get(local_name)
                if not initial_value and instance: # try model if defined
                    initial_value = getattr(instance, localized_field)
                locale_data[localized_field] = initial_value
            elif instance is not None:
                locale_data[localized_field] = getattr(instance, localized_field)
            
        super(LocalisedForm, self).__init__(data, files, auto_id, prefix,
                                            locale_data, error_class, 
                                            label_suffix, empty_permitted, 
                                            instance)
                                              
    def save(self, commit=True):
        """
        Override save method to also save the localised fields.
        """
        # set the localised fields
        for localized_field in self.instance.localized_fields:
            setattr(self.instance, localized_field, self.cleaned_data[localized_field])

        return super(LocalisedForm, self).save(commit)

    def validate_unique(self):
        """
        Validates the uniqueness of fields, but also handles the localized_fields.
        """
        form_errors = []
        try:
            super(LocalisedForm, self).validate_unique()
        except ValidationError as e:
            form_errors += e.messages

        # add unique validation for the localized fields.
        localized_fields_checks = self._get_localized_field_checks()
        bad_fields = set()

        field_errors, global_errors = self._perform_unique_localized_field_checks(localized_fields_checks)
        bad_fields.union(field_errors)
        form_errors.extend(global_errors)
        
        for field_name in bad_fields:
            del self.cleaned_data[field_name]
        if form_errors:
            # Raise the unique together errors since they are considered
            # form-wide.
            raise ValidationError(form_errors)
    
    def _get_localized_field_checks(self):
        """
        Get the checks we must perform for the localized fields.
        """
        localized_fields_checks = []
        for localized_field in self.instance.localized_fields:
            if self.cleaned_data.get(localized_field) is None:
                continue
            f = getattr(self.instance.__class__, localized_field, None)
            if f and f.unique:
                if f.unique:
                    local_name = get_real_fieldname(localized_field, self.language)
                    localized_fields_checks.append((localized_field, local_name))
                    
        return localized_fields_checks

    def _perform_unique_localized_field_checks(self, unique_checks):
        """
        Do the checks for the localized fields.
        """
        bad_fields = set()
        form_errors = []

        for (field_name, local_field_name) in unique_checks:
            
            lookup_kwargs = {}
            lookup_value = self.cleaned_data[field_name]
            # ModelChoiceField will return an object instance rather than
            # a raw primary key value, so convert it to a pk value before
            # using it in a lookup.
            lookup_value = getattr(lookup_value, 'pk', lookup_value)
            lookup_kwargs[str(local_field_name)] = lookup_value

            qs = self.instance.__class__._default_manager.filter(**lookup_kwargs)

            # Exclude the current object from the query if we are editing an
            # instance (as opposed to creating a new one)
            if self.instance.pk is not None:
                qs = qs.exclude(pk=self.instance.pk)

            # This cute trick with extra/values is the most efficient way to
            # tell if a particular query returns any results.
            if qs.extra(select={'a': 1}).values('a').order_by():
                self._errors[field_name] = ErrorList([self.unique_error_message([field_name])])
                bad_fields.add(field_name)
                
        return bad_fields, form_errors

def make_localised_form(model, form, exclude=None):
    """
    This is a factory function that creates a form for a model with internationalised 
    field. The model should be decorated with the L10N decorater.
    """
    
    newfields = {}  
    
    for localized_field in model.localized_fields:
        # get the descriptor, which contains the form field
        default_field_descriptor = getattr(model, localized_field)
        
        # See if we've got overridden fields in a custom form.
        if hasattr(form, 'declared_fields'):
            form_field = form.declared_fields.get(
                localized_field, default_field_descriptor.form_field)
        else:
            form_field = default_field_descriptor.form_field
         
        # wrap the widget to show the origin of the value;
        # either database, catalog or fallback.
        if type(form_field.widget) is not WidgetWrapper:
            form_field.widget = WidgetWrapper(form_field.widget)
         
        newfields[localized_field] = form_field
 
    if hasattr(form, 'Meta'):
         setattr(form.Meta, 'model', model)
    else:
         newfields['Meta'] = type('Meta', tuple(), {'model':model})
    
    newfields['localized_fields'] = model.localized_fields
    
    return ModelFormMetaclass(model.__name__, (LocalisedForm, form), newfields)
