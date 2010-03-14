# Create your views here.
from django.http import HttpResponse
from django.shortcuts import render_to_response
from django.template import RequestContext

from easymode import tree
from easymode.tree.query import XmlQuerySetChain
from easymode.xslt.response import render_to_response as render_xslt_to_response
from foobar import models as foobar_models

def index(request):
    """shows an informative page"""
    return render_to_response('index.html', {}, context_instance=RequestContext(request))
    
def raw(request):
    """shows untransformed hierarchical xml output"""
    foos = foobar_models.Foo.objects.all()
    return HttpResponse(tree.xml(foos), mimetype='text/xml')

def chain(request):
    """shows how the XmlQuerySetChain can be used instead of @toxml decorator"""
    bars = foobar_models.Bar.objects.all()
    bazs = foobar_models.Baz.objects.all()
    qsc = XmlQuerySetChain(bars, bazs)
    return HttpResponse(tree.xml(qsc), mimetype='text/xml')
    
def xslt(request):
    """Shows xml output transformed with standard xslt"""
    foos = foobar_models.Foo.objects.all()
    return render_xslt_to_response('xslt/model-to-xml.xsl', foos)

def frontend(request, format='html'):
    if format == 'xml':
        return xslt(request)
    
    foos = foobar_models.Foo.objects.all()
    return render_xslt_to_response('frontend.xsl', foos)