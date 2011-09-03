from django.http import HttpResponse
from django.template.loader import find_template_source
from django.test import TestCase

from easymode.tree import xml as tree
from easymode.tests.models import TestModel
from easymode.tests.testcases import initdb
from easymode.utils.languagecode import get_language_codes
from easymode.xslt import response


if 'en-us' not in get_language_codes():
    raise Exception('the language "en-us" must be in your LANGUAGES to run the test suite')

__all__ = ('XsltTest',)

@initdb
class XsltTest(TestCase):
    """
    Test the functionality related to xslt
    """
    
    def setUp(self):
        t = TestModel(charfield='Hoi Ik ben de root node')
        t.save()
        f = t.submodels.create(subcharfield="Hoi Ik ben de first level sub node", subintegerfield=10)
        s = t.submodels.create(subcharfield="Hoi ik ben de tweede first level sub node", subintegerfield=100)
        w = t.secondsubmodels.create(ultrafield="Sed tempor. Ut felis. Maecenas erat.")
        f.subsubmodels.create(subsubcharfield="Hoi ik ben de thord level sub node")
        f.subsubmodels.create(subsubcharfield="Hoi ik ben de third level sub node")
        s.subsubmodels.create(subsubcharfield="Hoi ik ben de third level sub node")
        s.subsubmodels.create(subsubcharfield="Hoi ik ben de third level sub node")        
        t.save()
    
    def test_xsl_template_can_be_found(self):
        """docstring for test_xsl_template_can_be_found"""
        template = find_template_source('xslt/model-to-xml.xsl')
        assert(template)

    def test_xslt_template_will_render_one_object(self):
        """docstring for test_xslt_template_will_render"""
        data = TestModel.objects.get(pk=1)
        resp = response.render_to_response('xslt/model-to-xml.xsl', data)
        assert(resp)

    def test_xslt_changes_the_xml(self):
        """docstring for test_xslt_changes_the_xml"""
        data = TestModel.objects.get(pk=1)
        resp = response.render_to_response('xslt/model-to-xml.xsl', data)
        assert(resp != HttpResponse(tree.xml(data)))

    def test_xslt_will_render_queryset(self):
        """docstring for test_xslt_will_render_queryset"""
        data = TestModel.objects.all()
        resp = response.render_to_response('xslt/model-to-xml.xsl', data)
        assert(resp)