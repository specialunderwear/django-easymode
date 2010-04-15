Internationalization and localization of django models
======================================================

.. _internationalization_of_models:

Internationalization of models
------------------------------

Django supports internationalization of text in templates and code by means of
gettext. For internationalization of dynamic model data, easymode offers simple
decorators to enable internationalized fields.

The only requuirement fields have to satisfy to be able to be internationalised
by easymode, is that their :func:`~django.db.models.to_python` method may not access ``self``.

suppose we have the following model.

::
    
    from django.db import models

    class Foo(models.Model):
        bar = models.CharField(max_length=255, unique=True)
        barstool = models.TextField(max_length=4)
        website = models.URLField()
        address = models.CharField(max_length=32)
        city = models.CharField(max_length=40)


In different languages the city could have a different name, so we would like to 
make it translatable (eg. internationalize the city field). This can be done using
the :class:`~easymode.i18n.decorators.I18n` decorator. Decorating the model as 
follows makes the field translatable::

    from django.db import models
    from easymode.i18n.decorators import I18n

    @I18n('city')
    class Foo(models.Model):
        bar = models.CharField(max_length=255, unique=True)
        barstool = models.TextField(max_length=4)
        website = models.URLField()
        address = models.CharField(max_length=32)
        city = models.CharField(max_length=40)
    
Now the ``city`` field is made translatable. As soon as you register this model 
with the admin, you will notice this fact. Depending on how many languages you got
in ``LANGUAGES`` this is how your change view will look:

.. image:: non-localized.png

While useful, the interface can become very cluttered when more fields need to
be internationalized. To make the interface less cluttered the admin class that
belongs to the model, can be *Localized* making it show only the fields in the
current language.

.. _localization_of_admin:

Localization of models in django admin
--------------------------------------

As there are several options to register a model for inclusion in django's admin,
there are also several options to localize the admin classes.

The simplest way to make a model editable in the admin is::

    from django.contrib import admin
    from foobar.models import Foo

    admin.site.register(Foo)

Since the admin class is implicit here, there is no way we can localize the
admin class this way. The next simplest way is::

    from django.contrib import admin
    from foobar.models import Foo

    admin.site.register(Foo, models.ModelAdmin)

Here the admin class is explicit, so we can modify it. The way this is done is by
using the :class:`~easymode.i18n.admin.decorators.L10n` class decorator::

    from django.contrib import admin
    from easymode.i18n.admin.decorators import L10n
    from foobar.models import Foo

    admin.site.register(Foo, L10n(Foo, models.ModelAdmin))

Note that the decorator needs the model to determine which fields are localized, so
it must be passed as a parameter. Now the change view in the admin looks as follows:

.. image:: localized.png

All the 'city' fields are hidden, except for the field in the current language. Note
That all fields which can be translated are marked with ∴ . To edit the content for 
the other languages, the current language must be switched. Please refer to 
:ref:`translation_of_contents` for more details.

There is one more way a models can be registered for the admin and that is by creating
a new descendant of :class:`~django.contrib.admin.ModelAdmin` for a specific model. You can now also use the 
:class:`~easymode.i18n.admin.decorators.L10n` decorator with the new class decorator syntax::

    from django.contrib import admin
    from easymode.i18n.admin.decorators import L10n

    from foobar.models import Foo

    @L10n(Foo)
    class FooAdmin(admin.ModelAdmin):
        """Generic Admin class not specific to any model"""
        pass
    
    admin.site.register(Foo, FooAdmin)

Note that you still have to pass the model class as a parameter to the decorator.

For admin classes that specify the :attr:`~django.contrib.admin.ModelAdmin.model` attribute you can leave that out::

    from django.contrib import admin
    from easymode.i18n.admin.decorators import L10n

    from foobar.models import Foo

    @L10n
    class FooAdmin(admin.ModelAdmin):
        """Admin class for the Foo model"""
        model = Foo

    admin.site.register(Foo, FooAdmin)

As you can see there isn't much to making models translatable this way.

Inline and GenericInline ModelAdmin
-----------------------------------

All easymode's localization mechanisms fully support django's flavors of
:class:`~django.contrib.admin.options.InlineModelAdmin`, both normal and generic. While there is no need to
register these types of ModelAdmin classes, you still need to decorate them
with :class:`~easymode.i18n.admin.decorators.L10n` if you need them to 
be localized.

Fieldsets are also supported
----------------------------

:attr:`~django.contrib.admin.ModelAdmin.fieldsets` are supported for admin classes decorated with 
:class:`~easymode.i18n.admin.decorators.L10n`. However :attr:`~django.contrib.admin.ModelAdmin.fields`
is not supported, because easymode uses it to hide fields. Since you can do the exact
same thing with fieldsets, this should not be a problem.