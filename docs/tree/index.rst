.. _tree_explanation:

Admin support for model trees with more than 2 levels of related items
======================================================================

.. note::
    
    This is the documentation for the **new** tree, which is much more flexible
    and powerful as the old one. for the old docs, see :ref:`tree_explanation`

Easymode has full admin support. Since content easymode was designed to handle
is heavy hierarchic, easymode can also support this in the admin.

The single most annoying problem you will encounter when building django apps,
is that after you discovered the niceties of 
:attr:`~django.contrib.admin.ModelAdmin.inlines`, you find out that only
1 level of :attr:`~django.contrib.admin.ModelAdmin.inlines`
is supported. It does not support any form of recursion.

Easymode gives you the :mod:`easymode.tree.admin` package which gives you two
baseclasses you can use to make recursive inlines possible. Django let's you
pff i'm going to stop now.

TODO::

finish this.
