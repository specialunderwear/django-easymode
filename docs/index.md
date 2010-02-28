Unsupported django features
===========================

The following features, which django supports, are not supported by easymode:

- ``Model.Meta.unique_together``
- ``Field.unique_for_date``, ``Field.unique_for_month``, ``Field.unique_for_year``
- ``ModelAdmin.fields``, use ``ModelAdmin.fieldsets`` instead.
- Automatic serialization of ``ManyToManyField``. The model tree should be a `DAG <http://en.wikipedia.org/wiki/Directed_acyclic_graph>`_.

All these features are not supported because the ammount of work to have them was greater than the benefit of having them.

Easymode : toolkit for making xml based flash websites
======================================================

Easymode is a toolkit that helps making xml based flash websites easy.
The tools included in the toolkit to help you make these kind of sites include:

.. toctree::
   :maxdepth: 1

    Internationalisation of models, with admin support <i18n/index.md>
    Translation of model data using gettext <i18n/translation.md>
    Automatic generation of xml from model trees <xslt/index.md>
    Admin support for model trees with more than 2 levels of related items <tree/index.md>
    Basic approval support for models <easypublisher.md>
    
Additional subjects
===================

.. toctree::
    :maxdepth: 1
    
    settings
    commands
    middlewares <middleware.md>
    helpers <xslt/helpers.md>

Getting easymode
================

You can download easymode from:

http://github.com/LUKKIEN/django-easymode/downloads/

Or you can do::

- ``pip install -e git://github.com/LUKKIEN/django-easymode.git#egg=easymode``
- ``pip install http://github.com/LUKKIEN/django-easymode/tarball/v0.4.0``
- ``easy_install http://github.com/LUKKIEN/django-easymode/tarball/v0.4.0``

Api docs
========

.. toctree::
    :maxdepth: 2

    i18n/api
    tree/api
    xslt/api
    utils/api
    fields    
    