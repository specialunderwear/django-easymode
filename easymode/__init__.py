"""
Easymode is an aspect oriented toolkit that helps making xml based flash websites easy.
The tools included in the toolkit to help you make these kind of sites include:

* Internationalization of models, with admin support
* Translation of model data using gettext
* Automatic generation of xml from model trees using xslt
* Admin support for model trees with more than 2 levels of related items
* Basic approval support for models

documentation at http://packages.python.org/django-easymode/

release notes at http://packages.python.org/django-easymode/changes.html
"""

# monkey patch a bug in django's SubfieldBase
# See easymode.hacks.SubfieldBaseFix 
from easymode.hacks import SubfieldBaseFix
import django.db.models.fields.subclassing
django.db.models.fields.subclassing.SubfieldBase = SubfieldBaseFix
import django.db.models
django.db.models.SubfieldBase = SubfieldBaseFix
