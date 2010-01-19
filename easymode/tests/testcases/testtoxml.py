from hashlib import md5

from django.test import TestCase

from easymode.tree.serializers import RecursiveXmlSerializer

from easymode.tests.models import *
from easymode.tests.testcases import initdb
from easymode.utils.languagecode import get_language_codes
from easymode import tree

if 'en-us' not in get_language_codes():
    raise Exception('the language "en-us" must be in your LANGUAGES to run the test suite')

# CONFIRMED_XML_DIGEST = 'ffcb6719a199ffc189ae35bff10a29d0'
CONFIRMED_XML_DIGEST = '02658bdf2a2e131ae4027396672037f7'
@initdb
class RecursiveSerializerTest(TestCase):
    """
    Test the functionality related to
    xmlserializable models.
    """
    
    def extraSetUp(self):
        t = TestModel(charfield='In lectus est, viverra a, ultricies ut, pulvinar vitae, tellus.')
        t.save()
        f = t.submodels.create(subcharfield="Quisque facilisis erat a dui.", subintegerfield=10)
        s = t.submodels.create(subcharfield="Hoi ik ben de tweede first level sub node", subintegerfield=100)
        w = t.secondsubmodels.create(ultrafield="Sed tempor. Ut felis. Maecenas erat.")
        f.subsubmodels.create(subsubcharfield="Cras eu mauris.")
        f.subsubmodels.create(subsubcharfield="Etiam imperdiet urna sit amet risus.")
        s.subsubmodels.create(subsubcharfield="Proin tincidunt, velit vel porta elementum, magna diam molestie sapien, non aliquet massa pede eu diam.")
        s.subsubmodels.create(subsubcharfield="Ut felis.")        
        t.save()
    
    
    def test_create_test_models(self):
        """create test models"""
        assert(TestModel.objects.all().count() == 1)
        
    def test_tree_serialize(self):
        """test serialization of models with foreign keys"""
        ser = RecursiveXmlSerializer()
        res = TestModel.objects.all()
        xml = ser.serialize(res)
        assert(md5(xml).hexdigest() == CONFIRMED_XML_DIGEST)
        
    def test_model_to_xml(self):
        """test the __xml__ method added to the model"""
        xml = TestModel.objects.get(pk=1).__xml__()
        assert( md5(xml).hexdigest() == CONFIRMED_XML_DIGEST)
 
    def test_model_to_xml_with_xml_function(self):
        """test the xml function in package tree"""
        xml = tree.xml(TestModel.objects.get(pk=1))
        assert( md5(xml).hexdigest() == CONFIRMED_XML_DIGEST)
        
    def test_query_set_to_xml(self):
        """Test the __xml__ method on querysets"""
        xml = TestModel.objects.all().__xml__()
        assert( md5(xml).hexdigest() == CONFIRMED_XML_DIGEST)
    
    def test_generic_relations_also_work(self):
        """Generic relations should also be converted to xml properly"""
        r = TestGenericFkModel(name='ik ben cool')
        r.save()
        r.relateds.create(name='ik ben graaf')
        r.save()
        # print r
        # print "\n"
        # print r.__dict__
        # print "\n"
        # print r.__class__.__dict__
        # print "\n"
        # print r.__xml__()
        assert("This test must be implemented, it does work!" is False)