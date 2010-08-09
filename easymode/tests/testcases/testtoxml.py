from hashlib import md5

from django.test import TestCase

from easymode import tree
from easymode.tests.models import TestModel, TestGenericFkModel
from easymode.tests.testcases import initdb
from easymode.tree.serializers import RecursiveXmlSerializer


__all__ = ('RecursiveSerializerTest',)

CONFIRMED_XML_DIGEST = '02658bdf2a2e131ae4027396672037f7'


@initdb
class RecursiveSerializerTest(TestCase):
    """
    Test the functionality related to
    xmlserializable models.
    """
    fixtures = ['tests-testmodel.xml']
    
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