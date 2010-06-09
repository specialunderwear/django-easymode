Easymode : toolkit for making xml based flash websites
======================================================

Easymode is an aspect oriented toolkit that helps making xml based flash websites easy.

The tools easymode provides are centered around the concept of hierarchy.
The basic structure of a flash frontend is hierarchical, because of
the hierarchical nature of the display list. The data that feeds such a frontend,
then will become hierarchical very quickly, should a site need to be mostly dynamic.

To enable a fully dynamic flash website, the technology used should support:

1. Rapid creation/modification of data structures.
2. A mechanism to organise these data structures in a hierarchy.
3. Enable administration of these data structures with minimal effort.
4. Enable transportation of all the information in such a hierarchical
   data set to a flash frontend.

When sites need to be internationalized, a fifth requirement forms:

5. Individual components of a hierarchy should be internationalized.

The last statement says *individual components* because the entire hierarchy
need not change amongst different localizations, only the components in the
hierarchy.

Django provides requirement 1,2 and 3:

1. Django models are the data structures, they are compact and are easily changed.
2. Foreign keys can be used as a child parent relation to create a hierarchy.
3. The django admin enables administration of models with minimal effort.

Easymode provides requirement 4 and 5:

4. An entire hierarchy of django models can be turned into xml by easymode and 
   transformed using xslt (:ref:`auto_xml`).
5. Easymode provides full internationalization of models, integrated into the django admin with support
   for hierarchical data (:ref:`internationalization_of_models`, :ref:`localization_of_admin`, :ref:`tree_explanation`).

Ofcoure, easymode also streamlines some of the things django provides, by integrating models,
hierarchy by foreign key relations and admin support.

The benefits of using django with easymode to create flash backends are:

1. A sane database, which can also feed a different frontend.
2. Easy maintenance because of simplicity of django models.
3. Code can be reused easily, because of modularity of django apps.
4. Data transport layer can be very simple because of the functional
   nature of xslt, which fits hierarchical data perfectly. (Can also be reused very easy)
5. Because the data is transported as xml, flash developers can start
   development using static xml before the backend is finished.
6. Actual mechanism to translate the content from one language to another 
   (:ref:`translation_of_contents`)
7. Structure is uniform in all layers of the application. (backend, transport, frontend)

Table of contents
=================

.. toctree::
    :maxdepth: 2
   
    i18n/index
    i18n/translation
    xslt/index
    tree/index
    easypublisher
    settings
    commands
    templatetags
    Middlewares <middleware.md>
    xslt/helpers
    changes

The best way to learn how easymode works, is to read the above topics in sequence
and then look at the :ref:`example_app`.


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
- Inheritance for models is restricted to :attr:`~django.db.models.Options.abstract` base classes. 
  This is a direct result of the fact that :class:`~django.db.models.OneToOneField` are *not* supported by
  the serializer.

All these features are not supported because the ammount of work to have them was greater than the benefit of having them.

Api docs
========

.. toctree::
    :maxdepth: 2

    i18n/api
    tree/api
    xslt/api
    utils/api
    fields    

Version naming convention
-------------------------

* Each update to the development status will increase the first digit. (eg beta or alpha or production ready)
* Each new feature will increase the second digit.
* Each bugfix or refactor will increase the last digit

    