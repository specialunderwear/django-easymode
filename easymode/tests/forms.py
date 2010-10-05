from django import forms as django_forms

class OverrideForm(django_forms.ModelForm):
    number = django_forms.IntegerField(max_value=100)