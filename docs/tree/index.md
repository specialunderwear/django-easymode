.. _tree_explanation:

Admin support for model trees with more than 2 levels of related items
======================================================================

Easymode has full admin support. Since content easymode was designed to handle
is heavy hierarchic, easymode can also support this in the admin.

The single most annoying problem you will encounter when building django apps,
is that after you discovered the niceties of InlineModelAdmin, you find out it
can only support 1 level of inlines. It does not support any form of recursion.

Easymode can not make InlineModelAdmin recursive either, because that would become
a mess. What is *can* do, is display links to all related models. This way you have
them in reach where you need them. There is no need to go back to the admin and
select a different section to edit the related models.

.. image:: related.png

In the above picture, at the bottom of the ``Bars`` fieldset, there is a small
*+* button. Using this button you can create new ``Bar`` objects which have a
relation to the current ``Foo`` object. Just like with foreign key fields, the
*+* button opens a popup in which you can create a new related item. 

The items above the *+* button are all ``Bar`` objects that have a foreign key
which points to the current ``Foo`` object. Clicking them will let you edit them.

Implementing the tree
---------------------

To implement the tree first of all, you have to ensure that ``easymode`` comes
before ``django.contrib.admin`` in the ``INSTALLED_APPS`` section of your settings
file. This is because easymode needs to override the `admin/index.html` template.
Since the related items that point to ``Foo`` can now be accessed from the ``foo``
change_view, it is nolonger needed that ``Bar`` is displayed in editable models list
of the ``Foobar`` app. Just like :class:`InlineModelAdmin` we want the 'inlined'
models to be excluded from the app list.

.. image:: invisible.png

This is how we want the ``Foobar`` app listing to look, with ``Foo`` visible and
``Bar`` excluded from the listing. In fact, that is what you can do with the
``ModelAdmin`` classes inside :mod:`easymode.tree.admin.relation`, as long as
you make sure that the `admin/index.html` template is read from the ``easymode``
templates folder.

This is how the admin is defined to get the screenshots::

    from django.contrib import admin
    from easymode.i18n.admin.decorators import L10n
    from easymode.tree.admin.relation import *

    from foobar.models import Foo, Bar

    @L10n
    class FooAdmin(ForeignKeyAwareModelAdmin):
        """Admin class for the Foo model"""
        model = Foo
        invisible_in_admin = False
    
        fieldsets = (
            (None, {
                'fields': ('bar', 'barstool')
            }),
            ('An thingy', {
                'fields': ('website', 'city', 'address')
            }),
        )

    class BarAdmin(InvisibleModelAdmin):
        model = Bar
        parent_link = 'foo'

    admin.site.register(Foo, FooAdmin)
    admin.site.register(Bar, BarAdmin)

As you can see the ``ModelAdmin`` classes used are 
:class:`~easymode.tree.admin.relation.InvisibleModelAdmin` and
:class:`~easymode.tree.admin.relation.ForeignKeyAwareModelAdmin`.

:class:`~easymode.tree.admin.relation.ForeignKeyAwareModelAdmin` is aware
of the models that have a ``ForeignKey`` pointing to the model which it
makes editable. 

In this case, ``FooAdmin`` makes ``Foo`` editable, and ``Bar`` has a 
``ForeignKey`` which points to ``Foo``. ``FooAdmin`` is fully aware of
this! In fact it will make you aware as well, because it will display
all the related ``Bar`` models in ``Foo``'s change_view.

As said we'd like to have ``Bar`` be invisible in the ``Foobar`` app listing.
That is where :class:`~easymode.tree.admin.relation.InvisibleModelAdmin`
comes into play. Using :class:`~easymode.tree.admin.relation.InvisibleModelAdmin`
instead of a normal `admin.ModelAdmin` will hide the model from the app listing.

You could even use a :class:`~easymode.tree.admin.relation.ForeignKeyAwareModelAdmin`
in place of the :class:`~easymode.tree.admin.relation.InvisibleModelAdmin`
because it can be made invisible as well. Using these 2 ``ModelAdmin`` classes,
mixed with regular ``InlineModelAdmin`` you can create deep trees and manage them
too.