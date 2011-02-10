import warnings
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from easymode.tests.testcases import initdb

from easymode.utils import recursion_depth

__all__ = ('TestSuperRecusionLoop',)

@initdb
class TestSuperRecusionLoop(TestCase):
    
    fixtures = ['managererrormodel', 'auth-user', 'auth-group',]
    
    def test_recursion_error_by_super(self):
        "Calling super of an admin method should not cause infinite recursion"
        self.assertTrue( self.client.login(username='admin', password='admin') )
        
        admin_url = reverse('admin:tests_managererrormodel_delete', args=(1,))
        try:
            response = self.client.post(admin_url)
            self.failUnlessEqual(response.status_code, 200)
        except RuntimeError as e:
            self.fail(e)
    