Easymode : toolkit for making xml based flash websites
======================================================

With easymode you can create backends for dynamic flash/flex websites.
Easymode makes internationalization simple and outputs xml by
default. To tailor the xml to your application, you can transform
it using xslt templates, which easymode integrates.

For more info, look at :ref:`solipsism`

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
- :attr:`django.contrib.admin.ModelAdmin.prepopulated_fields` is not supported.

Most these features are not supported because the ammount of work to have them
was greater than the benefit of having them. However, it could also be that I
just `didn't need it yet <http://c2.com/xp/YouArentGonnaNeedIt.html>`_.

Api docs
========

.. toctree::
    :maxdepth: 2

    i18n/api
    tree/api
    xslt/api
    utils/api
    fields
    debug    

Version naming convention
-------------------------

* Each update to the development status will increase the first digit. (eg beta or alpha or production ready)
* Each new feature will increase the second digit.
* Each bugfix or refactor will increase the last digit
* An update to a 'big' digit, resets the 'smaller' digits.

