.. django-easymode documentation master file, created by
   sphinx-quickstart on Thu Dec 31 10:16:20 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Unsupported django features
===========================

The following features django supports, are not supported by easymode:

- ``Model.Meta.unique_together``
- ``ModelField.unique_for_date``, ``ModelField.unique_for_date``, ``ModelField.unique_for_year``
- ``ModelAdmin.fields``, use ``ModelAdmin.fieldsets`` instead.
- Automatic serialization of ``ManyToManyField``. The model tree should be a `DAG <http://en.wikipedia.org/wiki/Directed_acyclic_graph>`_.

All these features are not supported because the ammount of work to have them was greater than the benefit of having them.

Easymode : toolkit for making xml based flash websites
======================================================

Easymode is a toolkit that helps making xml based flash websites easy.
The tools included in the toolkit to help you make these kind of sites include:

.. toctree::
   :maxdepth: 1

    Internationalisation of models <i18n/index.md>
    Translation of model data using gettext <i18n/translation.md>
    Automatic generation of xml from model trees <xslt/index.md>
    Admin support for model trees with more than 2 levels of related items <tree/index.md>
    Admin support for internationalised models <i18n/index.md>
    Basic approval support for models <easypublisher.md>
    
Additional subjects
-------------------

.. toctree::
    :maxdepth: 1
    
    settings
    commands
    middlewares <middleware.md>
    helpers <xslt/helpers.md>

Api docs
--------

.. toctree::
    :maxdepth: 2
    
    i18n/api
    tree/api
    xslt/api
    