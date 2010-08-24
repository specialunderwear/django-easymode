Management Commands
===================

.. _easy_locale:

easy_locale
-----------

Easy locale will update the gettext catalogs with content from the database.
This can be specific to a single app or model.

Help output::

    Usage: manage.py easy_locale [options] 


            easy_locale <targetdir> <applabel>

            Will create a folder locale in targetdir with locales parsed
            from the models in applabel.

            example:
            ./manage.py easy_locale myapp myapp

            will create myapp/locale/ with po files in it.


..  _easy_reset_language:

easy_reset_language
-------------------

This command will clear the database fields in one langugage for a specific app
or model, so the translation will once again come from the catalog, instead of
the database.

Help output::

    Usage: manage.py easy_reset_language [options] 


            easy_reset_language <target locale> <app>

            will clear all fields for the locale in question so the values will be read from
            the locale again.

            example:
            ./manage.py easy_reset_language en myapp.mymodel

            This will clear myapp.mymodel in the en locale so all values
            will be fetched by gettext instead of being overridden.
    
