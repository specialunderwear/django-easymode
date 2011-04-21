Easymode : toolkit for making xml based flash websites
======================================================

With easymode you can create backends for dynamic flash/flex websites.
Easymode makes internationalization simple and outputs xml by
default. To tailor the xml to your application, you can transform
it using xslt templates, which easymode integrates.

For more info, look at :ref:`solipsism`

Manual
======

.. toctree::
    :maxdepth: 1
   
    changes
    i18n/index
    i18n/translation
    xslt/index
    tree/index
    easypublisher/index
    settings
    commands
    templatetags
    Middlewares <middleware.rst>
    xslt/helpers

The best way to learn how easymode works, is to read the above topics in sequence
and then look at the :ref:`example_app`. If you have questions please send them
to the mailing list at easymode@librelist.com.

Installation
============

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

If you want to use easymode's xslt fascilities, make sure to install either
`lxml <http://codespeak.net/lxml/>`_ or 
`libxslt <http://xmlsoft.org/XSLT/python.html>`_.

If you want to make use of :ref:`easypublisher`, make sure you've got
`django-reversion <http://code.google.com/p/django-reversion/>`_ installed.

Requirements
============

Easymode requires python 2.6, furthermore the following packages must be installed:

- Django

The following packages might also be required, depending on what features you
are using.

- lxml
- polib
- django-reversion


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

Actionscript bindings
=====================

If you are developing flex or flash sites with easymode, you are invited to try
out the new actionscript bindings at

http://github.com/specialunderwear/robotlegs-dungdungdung

These integrate object creation and databinding for easymode's xml output.

Api docs
========

.. toctree::
    :maxdepth: 2

    api
    i18n/api
    tree/api
    xslt/api
    easypublisher/api
    utils/api
    fields
    debug    

Version naming convention
-------------------------

* Each update to the development status will increase the first digit. (eg beta or alpha or production ready)
* Each new feature will increase the second digit.
* Each bugfix or refactor will increase the last digit
* An update to a 'big' digit, resets the 'smaller' digits.

