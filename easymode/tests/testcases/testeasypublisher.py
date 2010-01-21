import warnings
from django.test import TestCase
from django.conf import settings
from easymode.tests.testcases import initdb
import reversion

@initdb
class TestEasyPublisher(TestCase):
    """Tests for easypublisher"""
    
    def test_it_works(self):
        pass
        
    def test_tests_are_implemented(self):
        """Test any tests are implemented for easypublisher."""
        assert("There are no tests yet" is None)

    