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

Xslt is a functional programming language, specifically designed to be used to
transform one type of xml into another. So if we can reduce django's template
rendering process to transforming one type of xml to another, xslt would be a
dead on match for the job.

In fact we can. Easymode comes with a couple of serializers. These serializers
differ from the normal django serializers, in that they treat a foreign key
relation as a child parent relation. So while django's standard serializers
output is flat xml, easymode's serializers output hierarchical xml.

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
relations are followed. (Except for :class:`~django.db.models.ManyToManyField`, they are not supported).

The preferred method for calling the ``__xml__`` method is by it's function::

    from easymode.tree import xml
    
    foos = Foo.objects.all()
    rawxml = xml(foos)

Getting xml from several queries
--------------------------------

The next option, which can also be used with multiple queries, is use the
:class:`~easymode.tree.query.XmlQuerySetChain`::

    from easymode.tree import xml
    from easymode.tree.query import XmlQuerySetChain
    
    foos = Foo.objects.all()
    qsc = XmlQuerySetChain(foos)
    rawxml = xml(qsc)

Normally you would use the :class:`~easymode.tree.query.XmlQuerySetChain` to group some :class:`~django.db.models.QuerySet` objects together
into a single xml::

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

Easymode comes with one xslt that can give good results, depending on your needs::

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

.. [#f1] Xslt requires a python xslt package. Easymode can work with 
         `lxml <http://codespeak.net/lxml/>`_ , 
         `libxslt <http://xmlsoft.org/XSLT/python.html>`_ and
         `libxsltmod <http://www.rexx.com/~dkuhlman/libxsltmod.html>`_