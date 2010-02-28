Basic approval support for models
=================================

Easymode comes with :mod:`~easymode.easypublisher`, a very simple approval 
application. It uses
`django-reversion <http://code.google.com/p/django-reversion/>`_ to store drafted
content. This has the very nice side effect that all drafts are in your history.

There is only one layer of approval, either you've got publishing rights or you
don't. Anyone with publisher rights can move content from draft to published, 
as long as they've got permission to modify the content. To use the publisher you
may use :class:`~easymode.easypublisher.admin.EasyPublisher` instead of 
:class:`~django.contrib.admin.ModelAdmin`::

    from django.contrib import admin
    from foobar.models import *
    from easymode.easypublisher.admin import EasyPublisher
    
    class FooAdmin(EasyPublisher):
        model = Foo
    
    admin.site.register(Foo, FooAdmin)

In case you want to use easypublisher together with :mod:`easymode.tree.admin.relation`
you will find that multiple inheritance doesn't work due to conflict. Instead,
use :class:`easymode.easypublisher.admin.EasyPublisherFKAModelAdmin` where you would
use :class:`~easymode.tree.admin.relation.ForeignKeyAwareModelAdmin` and 
:class:`easymode.easypublisher.admin.EasyPublisherInvisibleModelAdmin` where you would
use :class:`~easymode.tree.admin.relation.InvisibleModelAdmin`. More info about these
admin classes is in :ref:`tree_explanation`.