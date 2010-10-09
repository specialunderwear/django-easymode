Management Commands
===================

.. _easy_locale:

easy_locale
-----------

.. note::

    Easy locale will update the gettext catalogs with content from the database.
    This can be specific to a single app or model.

.. automodule:: easymode.management.commands.easy_locale

..  _easy_reset_language:

easy_reset_language
-------------------

.. note::

    This command will clear the database fields in one language for a specific app
    or model, so the translation will once again come from the catalog, instead of
    the database.

.. automodule:: easymode.management.commands.easy_reset_language