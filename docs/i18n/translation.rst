.. _translation_of_contents:

Translation of database content using gettext
=============================================

When using the :ref:`i18n <internationalization_of_models>` and 
:ref:`l10n <localization_of_admin>` features of easymode, you can use gettext's
standard translation features to translate all the database content.

.. _auto_catalog_ref:

Automatic catalog management
----------------------------

If the :ref:`master_site` and :ref:`auto_catalog` directive are set to True,
every time a model decorated with :class:`~easymode.i18n.decorators.I18n` is
saved, easymode wil add an entry to the corresponding gettext catalog [#f0]_.
(for all the options related to the location of the catalogs please refer to
:doc:`/settings`). The default for :ref:`auto_catalog` is ``False``, the default
for :ref:`master_site` is also ``False``.

For each language in your ``LANGUAGES`` directive, a catalog will be created.
This way you can translate all the content using something like 
`poedit <http://www.poedit.net/>`_ or 
`rosetta <http://code.google.com/p/django-rosetta/>`_. This is especially
convenient when a new site is created, for the first *big batch* of translations.

For modifications afterward, you can just use the admin interface, which will
show the translations from the gettext catalog if they exist.

TAKE CARE
---------

The translation mechanism using gettext is best used when a site is initially
going to be translated to other languages. After this fase, content will most likely be
edited directly in the admin interface, and you can have issues with translations not
showing up. This can happen when content was allready stored in the database, as 
described in :ref:`database_rules_all`. In effect any changes made to the gettext
catalog after editors are changing content in the admin interface has a very low
probability of being shown on the website [#f1]_. However, easymode will help you,
showing you the origin of a value in the admin, by displaying symbols next to the
input fields:

- If a value is from the gettext catalog or fallback, easymode will display **∴°**
- If a value is from the database, but the catalog has a different value, easymode will
  display **∴⁺** . You can hover over this symbol to see the catalog value.
- If a value is from the database and there is no conflict with the catalog, easymode will
  display only **∴**

It takes proper planning to make full use of the
gettext capabilities of easymode. The proper workflow is:

1. edit and add base content of the website, **ALL OF IT** and make sure you don't want
   to modify it anymore.
2. translate content using gettext, and **completely stop all editing, just 
   lock up the site during translation!** [#f2]_ [#f3]_
3. edit and modify all you like in the admin, all translations will be there. [#f4]_  

If you choose to deviate from this workflow be sure to understand all the next topics
and learn how to use :ref:`easy_reset_language`.

Translation mechanism explained
-------------------------------

It is important to realise, that allthough you can make translations using gettext,
the catalog is not the only place where translations are stored. The 
:ref:`I18n decorator<internationalization_of_models>` not only registers a model
for catalog management, it also modifies the model.

suppose we have a model as follows:

::

    @I18n('bar')
    class Foo(models.Model):
        bar = models.CharField(max_length=255)
        foobar = models.TextField()

Normally the database would look like this:

.. code-block:: sql

    CREATE TABLE "foobar_foo" (
        "id" integer NOT NULL PRIMARY KEY,
        "bar" varchar(255) NOT NULL,
        "foobar" text NOT NULL
    )

The :ref:`I18n decorator<internationalization_of_models>` modiefies the model,
given we've got both 'en' and 'yx' in out ``LANGUAGES`` directive this is what
the model would look like on the database end:

.. code-block:: sql

    CREATE TABLE "foobar_foo" (
        "id" integer NOT NULL PRIMARY KEY,
        "bar_en" varchar(255) NULL,
        "bar_yx" varchar(255) NULL,
        "foobar" text NOT NULL
    )

On the model end you would not see this, because you will still access ``bar`` 
like this::

    >>> m = Foo.objects.get(pk=1)
    >>> m.bar = 'hello'
    >>> print m.bar
    hello

Any field that is internationalized using the 
:ref:`I18n decorator<internationalization_of_models>` will always return the 
field in the current languge, both on read and on write.

.. _database_rules_all:

Database is bigger than gettext
-------------------------------

**Only when a field is empty** (``None``) **in the database for the current language, the
gettext catalog will be consulted for a translation**

This way, a model has exactly the same semantics as before, in that we can read
and write to the property, the way we defined it in it's declaration. We 
still get the gettext goodies, which is nice when large ammounts of text must be
translated. 

If the gettext catalog would be the only place where the translations
would be stored, having proper write semantics would become very difficult.

Example::

    >>> from django.utils.translation import activate
    
    >>> m = Foo()
    >>> m.bar = 'hello'
    >>> m.bar
    'hello'
    >>> activate('yx')
    >>> m.bar
    'hello'
    >>> m.bar = 'xy says hello'
    >>> m.bar
    'xy says hello'
    >>> activate('en')
    >>> m.bar
    'hello'

What you'll notice is that ``m.bar`` is allready available in the language 'yx'
even though we did't specify it's value yet. This is because the normal behaviour
of gettext is to return the ``msgid`` if the ``msgstr`` is not yet available. 
This is because the value for ``m.bar`` in language 'yx' was resolved as follows:

* see if the database value bar_yx is not null, if so return bar_yx
* see if the ``msgstr`` for 'hello' (The value of ``m.bar`` in the 
  :ref:`msgid_language`) exists if so return ugettext('hello')
* otherwise return the value in the :ref:`fallback language <fallback_langugaes>`

.. _implicit_translation:

Importing translations is implicit
----------------------------------

One thing that follows from the mechanics as described above, is that there is
no need to explicitly import translations from gettext catalogs into the database.

Importing does take place however, each time a model is saved in the admin, the
translations are written to the database. 

This is because the translations from the gettext catalog *ARE* displayed in the 
admin, which means they *ARE* present in the form, but since the database column 
itself is *EMPTY* it will be marked as a change and written to the appropriate 
field.

This implicit import could pose a problem. If for example a model was edited in the
admin, *BEFORE* the gettext catalog was properly translated and imported, it could
be that the wrong value, from some :ref:`fallback language <fallback_langugaes>`
got written to the database. Because the database get's precedence over the 
gettext catalog, the new translation would never show up.

This inconvenience can be resolved using the :ref:`easy_reset_language` command

.. [#f0] It is possible to have more finegrained control over which models
    should be automatically added to the catalog by settings :ref:`auto_catalog` to
    ``False`` and using :func:`easymode.i18n.register` to register individual models.
    More info in the :ref:`auto_catalog` docs.

.. [#f1]  Obviously, other gettext
    catalogs, generated from static content, that are not managed by easymode are unaffected.
.. [#f2] You can make sure nobody goes into the admin to edit things, by commenting out the admin
    routes in urls.py    the new message id. Unless the content is allready saved in the database (:ref:`database_rules_all`).
.. [#f3] If you don't lock up the admin you might have issues with
    translations not showing up. Someone could for some reason save an item in the wrong language.
    This means the value in the database will be used instead of the translation in the catalig. 
    You can detect when this has happened by looking for a ∴⁺ sign in the admin next to the untranslated field.
    Hover over the field to see the value in the catalog.
.. [#f4] Watch out
    when  you completely replace existing content in the :ref:`msgid_language`. The
    :ref:`msgid_language` is used for the message id's in the catalogs. When you completely
    replace the existing message id with something different, gettext will see that as adding
    a new message instead of changing an existing message. When this happens, translations
    can nolonger be associated with the new message and all languages will fall back to
