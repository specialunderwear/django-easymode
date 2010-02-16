Xslt is for Flash
=================

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

Getting xml from a model
------------------------

There are several ways to obtain such a hierarchical xml tree from a django model.
The first is by decorating a model with the ``toxml`` decorator::

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
relations are followed. (Except for manytomany fields, they are not supported).

The preferred method for calling the ``__xml__`` method is by it's function::

    from easymode.tree import xml
    
    foos = Foo.objects.all()
    rawxml = xml(foos)

Getting xml from several queries
--------------------------------

The next option, which can also be used with multiple queries, is use the
``XmlQuerySetChain``::

    from easymode.tree import xml
    from easymode.tree.query import XmlQuerySetChain
    
    foos = Foo.objects.all()
    qsc = XmlQuerySetChain(foos)
    rawxml = xml(qsc)

Normally you would use th ``XmlQuerySetChain`` to group some querysets together
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

The ``render_to_response`` helper function will take an xslt as a template and a
``XmlQuerySetChain`` or a model/queryset decorated with ``toxml`` to produce it's output.
Additionally you can pass it a dictionary containing xslt parameters. You have to
make sure to use ``easymode.xslt.prepare_string_param`` on any xslt parameter that 
should be passed to the xslt processor as a string.

Other helpers can be found in the ``easymode.xslt.response`` module. 

.. [#f1] Xslt requires a python xslt package. Easymode can work with 
         `lxml <http://codespeak.net/lxml/>`_ , 
         `libxslt <http://xmlsoft.org/XSLT/python.html>`_ and
         `libxsltmod <http://www.rexx.com/~dkuhlman/libxsltmod.html>`_