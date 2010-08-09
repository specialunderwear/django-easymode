from hashlib import md5

from django.test import TestCase

from easymode import tree
from easymode.utils.languagecode import get_real_fieldname
from easymode.tests.models import TestModel, TestGenericFkModel, TagModel
from easymode.tests.testcases import initdb
from easymode.tree.serializers import RecursiveXmlSerializer


__all__ = ('RecursiveSerializerTest',)

CONFIRMED_XML_DIGEST = '2caeeae817ed103f8c92020717460a9d'


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
        xml = TestGenericFkModel.objects.all().__xml__()
        assert(xml.index( 'ik ben cool') != -1)
        assert(xml.index( 'ik ben graaf') != -1)
        r.relateds.create(name='ik lust spruitjes')
        r.save()
        xml = TestGenericFkModel.objects.all().__xml__()
        assert(xml.index( 'ik lust spruitjes') != -1)
    
    def test_natural_keys(self):
        "natural keys will show up in the xml"
        
        xml_with_natural_keys = tree.xml(TestModel.objects.all())
        assert(xml_with_natural_keys.find('<natural>In lectus est, viverra a, ultricies ut, pulvinar vitae, tellus.</natural>') != -1)
    
    def test_many_to_many_field(self):
        "ManyToManyField should be followed in one direction, like foreign keys"
        
        data = tree.xml(TestModel.objects.all())
        assert(data.index('<field type="CharField" name="value">good</field>')!= -1)
        assert(data.index('<field type="CharField" name="value">ugly</field>')!= -1)
        
        bad_tag = TagModel.objects.get(value_en='bad')
        first_item = TestModel.objects.get(pk=1)
        first_item.tags.add(bad_tag)
        first_item.save()
        data = tree.xml(TestModel.objects.all())
        assert(data.index('<field type="CharField" name="value">bad</field>')!= -1)