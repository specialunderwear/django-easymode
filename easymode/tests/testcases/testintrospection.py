import inspect

from django.test import TestCase
from django.utils.translation import activate

from easymode.i18n.meta import DefaultFieldDescriptor
from easymode.tests.models import ManagerErrorModel
from easymode.tests.testcases import initdb
from easymode.tree import introspection


__all__ = ('TestIntrospection',)

@initdb
class TestIntrospection(TestCase):
    """Tests for the introspection package in easymode"""
    
    fixtures = ['managererrormodel']
    
    def test_there_are_fixtures(self):
        """The fixtures hsould be instantiated coreectly"""
        self.failUnlessEqual(ManagerErrorModel.objects.count(), 2)
    
    def test_introspection_breaks(self):
        "inspect.getmembers should break in ManagerErrorModel"
        self.failUnlessRaises(AttributeError, inspect.getmembers, ManagerErrorModel)
    
    def test_bad_behaving_models_can_be_internationalized(self):
        """
        Models that throw exception when using module introspection,
        should be properly internationalized
        """
        obj = ManagerErrorModel.objects.get(pk=1)
        activate('en')
        self.failUnlessEqual(obj.a, 'english title a')
        self.failUnlessEqual(obj.b, 'uploads/11lekkerECHICKORIG.jpg')
        self.failUnlessEqual(obj.c, 'title c')
        activate('de')
        self.failUnlessEqual(obj.a, 'german titel a')
        self.failUnlessEqual(obj.b, 'uploads/111superlekkerechick.jpg')
        self.failUnlessEqual(obj.c, 'title c')
    
    def test_get_default_field_descriptors(self):
        "See if the DefaultFieldDescriptor is properly found"
        descriptors = introspection.get_default_field_descriptors(ManagerErrorModel)

        for (key, value) in descriptors:
            self.failUnlessEqual(type(value), DefaultFieldDescriptor)
        
        self.failUnlessEqual(len(descriptors), 2)

        descriptors = introspection.get_default_field_descriptors(ManagerErrorModel.objects.get(pk=1))

        for (key, value) in descriptors:
            self.failUnlessEqual(type(value), DefaultFieldDescriptor)
        
        self.failUnlessEqual(len(descriptors), 2)
        
        