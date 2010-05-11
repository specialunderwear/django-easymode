Easymode : toolkit for making xml based flash websites
======================================================

Easymode is an aspect oriented toolkit that helps making xml based flash websites easy.
The tools included in the toolkit to help you make these kind of sites include:

.. toctree::
   :maxdepth: 1

    Internationalization of models, with admin support <i18n/index.md>
    Translation of model data using gettext <i18n/translation.md>
    Automatic generation of xml from model trees using xslt<xslt/index.md>
    Admin support for model trees with more than 2 levels of related items <tree/index.md>
    Basic approval support for models <easypublisher.md>

The best way to learn how easymode works, is to read the above topics in sequence
and then look at the :ref:`example_app`.

Version naming convention
-------------------------

* Each update to the development status will increase the first digit. (eg beta or alpha or production ready)
* Each new feature will increase the second digit.
* Each bugfix or refactor will increase the last digit

.. _example_app:

Example
=======

Easymode comes with an example app which is available from github:

http://github.com/LUKKIEN/django-easymode/

To run the example app, you must clone the repository, install the dependencies
and initialize the database::

    git clone http://github.com/LUKKIEN/django-easymode.git
    cd django-easymode
    pip install -r requirements.txt
    cd example
    python manage.py syncdb
    python manage.py loaddata example_data.xml
    python manage.py runserver
    open http://127.0.0.1:8000/
    
Unsupported django features
===========================

The following features, which django supports, are not supported by easymode:

- :attr:`~django.db.models.Options.unique_together`
- :attr:`~django.db.models.Field.unique_for_date`, :attr:`~django.db.models.Field.unique_for_month`,
  :attr:`~django.db.models.Field.unique_for_year`
- :attr:`django.contrib.admin.ModelAdmin.fields`, use :attr:`django.contrib.admin.ModelAdmin.fieldsets` instead.
- Automatic serialization of :class:`~django.db.models.ManyToManyField`. The model tree should 
  be a `DAG <http://en.wikipedia.org/wiki/Directed_acyclic_graph>`_.
- Inheritance for models is restricted to :attr:`~django.db.models.Options.abstract` base classes. 
  This is a direct result of the fact that :class:`~django.db.models.OneToOneField` are *not* supported by
  the serializer.

All these features are not supported because the ammount of work to have them was greater than the benefit of having them.

Known issues
============

- When using the :class:`~easymode.i18n.admin.decorators.L10n` decorator, you can not specify 
  the :attr:`~django.contrib.admin.ModelAdmin.form` of a
  :class:`~django.contrib.admin.ModelAdmin` class, because :class:`~easymode.i18n.admin.decorators.L10n` will
  set this value for you (see `bug 4 <http://github.com/LUKKIEN/django-easymode/issues/#issue/4>`_).
- when using a filter statement in a query for an internationalised field, the real field name in 
  the database should be passed to the filter.
  example::
  
        from easymode.utils.languagecode import get_real_fieldname
        from django.utils.translation import get_language_
        SomeModel.object.filter(title=get_real_fieldname('title', get_language_()))
  
  see :func:`~easymode.utils.languagecode.get_real_fieldname`
- some :class:`~django.contrib.admin.ModelAdmin` properties still need the real field names 
  (title_en instead of title), just like filtering. Most of it is just temporary and can be 
  fixed using :class:`~easymode.i18n.admin.decorators.lazy_localized_list`.
  I just haven't found time yet to fix it. report a bug if you need it fixed.
- There are undocumented features. These are all related to *permissions per field* and SEO.
  Please contact me if you have to know. Easymode can do
  field specific permissions, which can be used to give translators only access to fields
  which are actually translatable.
  (see `bug 2 <http://github.com/LUKKIEN/django-easymode/issues/#issue/2>`_).
  Some of the undocumented features are explained in the example app.
- When easymode has :ref:`auto_catalog` is set to ``True`` and :ref:`master_site` as well, each time
  a model is changed when no translations are done in the catalogs, the new and the old 
  value both remain present in the catalog. It is
  only after translation that easymode (gettext really) will try to update the message id's
  and make the link between the existing value and the new value. This can be overcome by
  turning :ref:`auto_catalog` off when adding the main site content, using :ref:`easy_locale`
  to generate the catalogs when the content has stabilised. This way the catalogs will remain
  free from unused messages.

Additional subjects
===================

.. toctree::
    :maxdepth: 1
    
    settings
    commands
    templatetags
    middlewares <middleware.md>
    Injecting extra data into the XSLT <xslt/helpers.md>

Getting easymode
================

You can download easymode from:

http://github.com/LUKKIEN/django-easymode/downloads/

Or you can do:

- ``pip install django-easymode``

Or:
- ``pip install -e git://github.com/LUKKIEN/django-easymode.git#egg=easymode``

Note the version number in the top left corner and use:

- ``easy_install http://github.com/LUKKIEN/django-easymode/tarball/[VERSION]``

Which, if the version was v0.1.0 would become http://github.com/LUKKIEN/django-easymode/tarball/v0.1.0.

Api docs
========

.. toctree::
    :maxdepth: 2

    i18n/api
    tree/api
    xslt/api
    utils/api
    fields    
    