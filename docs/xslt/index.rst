.. _auto_xml:

Automatic generation of xml from models using xslt
==================================================

Most of the data being transferred to a flash frontend is in xml. This is both
because xml is very well supported by Flash (e4x) and because hierarchical data
is easily mapped to xml. Most data used for flash sited is hierarchical in nature, 
because the display list -flash it's version of html's DOM- is  hierarchical 
as well.

What easymode tries to do is give you a basic hierarchical xml document that
mirrors your database model, which you can then transform using xslt [#f1]_.

Why Xslt?
---------

Xslt is a functional programming language, specifically designed to
transform one type of xml into another. So if we can reduce django's template
rendering process to transforming one type of xml to another, xslt would be a
dead on match for the job.

In fact we can. Easymode comes with a special xml serializer. This serializer
differs from the normal django serializers, in that it treats a foreign key
relation as a child parent relation. So while django's standard serializers
output is flat xml, easymode's serializer outputs hierarchical xml.

Relations must be organized as a DAG
------------------------------------

In order for easymode to be able to do it's work, the model tree should be organised
as a `DAG <http://en.wikipedia.org/wiki/Directed_acyclic_graph>`_. if you accidently 
created a cycle (using :class:`~django.db.models.ManyToManyField` relations), easymode 
will let you know and throw an exception. Any :class:`~django.db.models.ManyToManyField`
that is related to "self" will be ignored by the serializer.

Most of the time you don't really need the cyclic relation at all. You just need to do
some preprocessing of the data. You can render a piece of xml yourself, without using
easymode's serializers and pass it to the xslt, see :doc:`helpers`.

Getting xml from a model
------------------------

There are several ways to obtain such a hierarchical xml tree from a django model.
The first is by decorating a model with the :func:`~easymode.tree.decorators.toxml` decorator::

    from easymode.tree.decorators import toxml
    
    @toxml
    class Foo(models.ModelAdmin):
        title = models.CharField(max_length=255)
        content = TextField()
        
    class Bar(models.ModelAdmin):
        foo = models.ForeignKey(Foo, related_name=bars)
        
        label = models.CharField(233)

The ``Foo`` model has now gained a ``__xml__`` method on both itself as on the
queryset it produces. Calling it will produce hierarchical xml, where all inverse
*ForeignKey* [#f2]_ relations are followed (easymode's serializer follows the
managers on a related model).

The preferred method for calling the ``__xml__`` method is by it's function::

    from easymode.tree import xml
    
    foos = Foo.objects.all()
    rawxml = xml(foos)

Getting xml from several queries
--------------------------------

The next option, which can also be used with multiple queries, is use the
:class:`~easymode.tree.query.XmlQuerySetChain` ::

    from easymode.tree import xml
    from easymode.tree.query import XmlQuerySetChain
    
    foos = Foo.objects.all()
    qsc = XmlQuerySetChain(foos)
    rawxml = xml(qsc)

Normally you would use the :class:`~easymode.tree.query.XmlQuerySetChain` to 
group some :class:`~django.db.models.QuerySet` objects together into a single
xml::

    from easymode.tree import xml
    from easymode.tree.query import XmlQuerySetChain

    foos = Foo.objects.all()
    hads = Had.objects.all()
    
    qsc = XmlQuerySetChain(foos, hads)
    rawxml = xml(qsc)

Using xslt to transform the xml tree
------------------------------------

Now you know how to get the xml as a tree from the models, it is time to show
how xslt can be used to transform this tree into something a flash developer can
use for his application.

Easymode comes with one xslt template [#f3]_ that can give good results,
depending on your needs::

    from easymode.xslt.response import render_to_response
    
    foos = foobar_models.Foo.objects.all()
    return render_to_response('xslt/model-to-xml.xsl', foos)

The :func:`~easymode.xslt.response.render_to_response` helper function will take an xslt as a template and a
:class:`~easymode.tree.query.XmlQuerySetChain` or a model/queryset decorated with 
:func:`~easymode.tree.decorators.toxml` to produce it's output.
Additionally you can pass it a :class:`dict` containing xslt parameters. You have to
make sure to use :func:`~easymode.xslt.prepare_string_param` on any xslt parameter that 
should be passed to the xslt processor as a string.

Other helpers can be found in the :mod:`easymode.xslt.response` module.

.. _nofollow:

Exclude certain relations from being followed by the serializer
---------------------------------------------------------------

Sometimes you want to have a simple foreign key relation, but you
don't need the data of the related object in your xml. As a matter of fact,
it would degrade the performance of your view. You could mark the
:class:`~django.db.models.ForeignKey` as ``serialize=False`` but that would make
the field simply disappear from the xml. You might only want to exclude it from
being rendered as a child of the parent object, but on the object itself you want
the foreign key rendered as usual.

You can mark any foreign key with a ``nofollow`` attribute and it will not be
followed, when the parent is serialized::

    class Bar(models.ModelAdmin):
        foo = models.ForeignKey(Foo, related_name=bars)
        foo.nofollow = True
        
        label = models.CharField(233)

The foreign key will still be serialized as it always would, but the related
object will not be expanded on the parent. This means if I query ``Foo``::

    xml(Foo.objects.all())

I will not see any ``Bar`` objects as children of foo. But when querying ``Bar``::

    xml(Bar.objects.all())

You will still see that the foreign key is included in the xml.

----

.. [#f1] Xslt requires a python xslt package to be installed. Easymode can work with 
     `lxml <http://codespeak.net/lxml/>`_ , 
     `libxslt <http://xmlsoft.org/XSLT/python.html>`_

.. [#f2]  While :class:`~django.db.models.ForeignKey` relations are followed
    'inverse' by the managers on the related model, this is not the case
    for :class:`~django.db.models.ManyToManyField`. Instead they are
    followed 'straight'. 

    Easymode does not follow 'straight' foreigkey relations because that
    would cause a cycle, instead it only takes the value of the foreignkey,
    which is an integer. If you do need some data from the related object
    in your xml, you can define the
    `natural_key <http://docs.djangoproject.com/en/dev/topics/serialization/#serialization-of-natural-keys>`_
    method on the related model. The output of that method will become
    the value of the foreignkey, instead of an integer. This way you can
    include data from a 'straight' related model, without introducing
    cyclic relations.

.. [#f3] The default xslt, with template path: *'xslt/model-to-xml.xsl'* comes 
    with easymode and looks like this:

.. literalinclude:: ../../easymode/templates/xslt/model-to-xml.xsl
    :language: xslt
