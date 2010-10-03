import inspect

from django.conf import settings
from django.test import TestCase
from django.utils.translation import activate
from django.db.models.query_utils import CollectedObjects

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
