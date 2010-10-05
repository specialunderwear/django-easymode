from django.core.urlresolvers import reverse
from django.test import TestCase

from easymode.tests.testcases import initdb


__all__ = ('TestL10nForm',)

@initdb
class TestL10nForm(TestCase):
    """Tests for the introspection package in easymode"""
    
    fixtures = ['auth-group', 'auth-user', 'formtestmodel']
    
    post_data = {
        'number': 130,
        'other': 'Your mother',
        'another': 'Well well',
    }
    
    username = 'admin'
    password = 'admin'
    
    def test_form_is_overridden(self):
        """The form on the admin should be overridden to have a max value for number"""
        self.assertTrue(self.client.login(username=self.username, password=self.password))
        admin_url = reverse('admin:tests_formtestmodel_change', args=[1])
        response = self.client.get(admin_url)
        self.failUnlessEqual(response.status_code, 200)
        
        # test overridden internationalized field
        self.assertContains(response, 100)
        # test normal field
        self.assertContains(response, 'hello')
        # test normal internationalized field
        self.assertContains(response, 'again')
        
        response = self.client.post(admin_url, self.post_data)
        self.assertContains(response, 130)
        self.assertContains(response, 'Your mother')
        self.assertContains(response, 'Well well')
        
        # the overridden number field should have set an error
        errors = response.context['errors']
        self.assertEquals(len(errors), 1)
        self.assertEquals(len(errors[0]), 1)
        self.assertEquals( errors[0][0], u'Ensure this value is less than or equal to 100.')
