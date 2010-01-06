"""
A framework for integrating django wih flash.

Features:
Support for diocore actionscript framework.
Localisation of django models.
Translation via po files or django admin.
Hierarchical serialization of django models.
Hierarchical organisation of madels in the admin.
Xslt transformation of serialized model xml.
django commands for administration.
"""
import warnings
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if not hasattr(settings, 'PROJECT_DIR'):
    raise ImproperlyConfigured(
        """
        PLEASE DEFINE PROJECT_DIR AS: 
        PROJECT_DIR = os.path.dirname(__file__) 
        in your settings.py
        """)
    
if not 'rosetta' in settings.INSTALLED_APPS:
    raise ImproperlyConfigured(
        """
        Please install django-rosetta: 
        http://code.google.com/p/django-rosetta/
        or easymode won't work"""
    )

try:
    import tinymce
except ImportError:
    warnings.warn(
        """
        Without tinymce most of the fields related to rich text do not work, 
        this will also cause lots of tests to fail!!
        http://code.google.com/p/django-tinymce/
        """
    )   
    