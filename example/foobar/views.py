# Create your views here.
from django.http import HttpResponse

from easymode import tree
from easymode.tree.query import XmlQuerySetChain
from easymode.xslt.response import render_to_response

from foobar import models as foobar_models

def index(request):
    """index view function"""
    foos = foobar_models.Foo.objects.all()
    return HttpResponse(tree.xml(foos), mimetype='text/xml')
    
def xslt(request):
    """test xml output view function"""
    foos = foobar_models.Foo.objects.all()
    return render_to_response('xslt/model-to-xml.xsl', foos)