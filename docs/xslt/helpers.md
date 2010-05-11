Injecting extra data into the XSLT
==================================

If you want to have some extra data passed to the xslt, which
can not be obtained by the serializer you can make some view
helpers that create xml and pass it as a stringparam to the xslt.

Reasons why you would need this: 

- You've got a model that has a foreign key to itself. You need this if you
  want some kind of hierarchical page tree or something. You might want to
  put the self referencing :class:`~django.db.models.ForeignKey` to ``serialize=False``. This
  way it can not mess up the serializer, but you don't have a hierarchic structure
  in your xml.
- You pull data from an external source.
- You have to do some processing on the models before they get turned into xml.
- You have some data not coming from models that needs to be passed to the xslt.

In all these cases you can use :class:`~easymode.utils.xmlutils.XmlPrinter` to
make some well formed unicode safe xml you can feed to the xslt.

Here is an example where some static strings get passed to the xslt. These
strings are translatable using django's regular i18n mechanism, but they are
not in the database::

    from django.utils.translation import ugettext as _
    
    stringlib = dict(
        close_button = _('Close'), 
        next_button = _('Next'), 
        the_end = _("That's all folks")
    )
    
    def render_stringlib_xml():
        """Renders the stringlib xml"""
        stream = StringIO()
        xml = XmlPrinter(stream, settings.DEFAULT_CHARSET)
        xml.startElement('stringlib', {'id':'stringlib'})
        for (key, value) in stringlib.iteritems():
            xml.startElement(key, {})
            xml.characters(value)
            xml.endElement(key)
        xml.endElement('stringlib')

        byte_string = stream.getvalue()
        return byte_string.decode('utf-8')
    
Before you pass the rendered xml string, you should prepare it using
:func:`~easymode.xslt.prepare_string_param`::

    from easymode.xslt import prepare_string_param as q
    from easymode.xslt.response import render_to_response
    
    params = {
        'stringlib' : q(render_stringlib_xml()),
    }
    
    qs = Foo.objects.all()
    
    return render_to_response('xslt/model-to-xml.xsl', qs, params)
    
    