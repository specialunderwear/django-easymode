# Create your views here.
from django.http import HttpResponse

from easymode import tree
from easymode.tree.query import XmlQuerySetChain
from easymode.xslt.response import render_to_response

from foobar import models as foobar_models

def index(request):
    """shows untransformed hierarchical xml output"""
    foos = foobar_models.Foo.objects.all()
    return HttpResponse(tree.xml(foos), mimetype='text/xml')

def chain(request):
    """shows how the XmlQuerySetChain can be used instead of @toxml decorator"""
    bars = foobar_models.Bar.objects.all()
    qsc = XmlQuerySetChain(bars)
    return HttpResponse(tree.xml(qsc))
    
def xslt(request):
    """Shows xml output transformed with standard xslt"""
    foos = foobar_models.Foo.objects.all()
    return render_to_response('xslt/model-to-xml.xsl', foos)

