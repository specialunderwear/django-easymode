import warnings
from django.conf import settings
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import get_language

from easymode.utils.languagecode import get_real_fieldname
from easymode.tests.models import TestL10nModel
from easymode.tests.testcases import initdb

from easymode.easypublisher.models import EasyPublisherMetaData

import reversion

if not 'easymode.easypublisher' in settings.INSTALLED_APPS:
    raise Exception('''Can not run easypublisher tests without easymode.easypublisher in INSTALLED_APPS.''')
if not 'reversion' in settings.INSTALLED_APPS:
    raise Exception('''Can not run easypublisher tests without reversion in INSTALLED_APPS''')

__all__ = ('TestEasyPublisher',)

@initdb
class TestEasyPublisher(TestCase):
    """Tests for easypublisher"""
    fixtures = ['auth-user', 'auth-group', 'tests-testl10nmodel']
    
    def test_login_as_non_privileged_user(self):
        self.assertTrue( self.client.login(username='editor', password='editor') )
        
    
    def test_publication_workflow(self):
        """
        The editor should save but the live site is not updated, and the
        publisher can save and the live site IS updated
        """
        self.client.login(username='editor', password='editor')
        
        post_data = {
            'price': 100,
            'title': 'Your mother',
            'description': 'lmao',
            'body': 'MY BAR IS LOL HAHA',
        }
        
        admin_url = reverse('admin:tests_testl10nmodel_change', args=[1])
        response = self.client.post(admin_url, post_data)
        self.failUnlessEqual(response.status_code, 302)
        
        # the contents of the first TestL10nModel should not be changed
        data = TestL10nModel.objects.get(pk=1)
        self.failIfEqual(data.price, post_data['price'])
        self.failIfEqual(data.title, post_data['title'])
        self.failIfEqual(data.description, post_data['description'])
        self.failIfEqual(data.body, post_data['body'])

        # there should be a test in reversion
        metas = EasyPublisherMetaData.objects.select_related()
        self.failUnlessEqual(len(metas), 1)

        meta = metas[0]

        for version in meta.revision.version_set.all():
            obj = version.get_field_dict()
            self.failUnlessEqual(obj[get_real_fieldname('title', get_language())], post_data['title'])
            self.failUnlessEqual(obj[get_real_fieldname('description', get_language())], post_data['description'])
            self.failUnlessEqual(obj['price'], post_data['price'])
            self.failUnlessEqual(obj['body'], post_data['body'])
        
        # restoring the item will save the shizz
        for version in meta.revision.version_set.all():
            version.revert()
        
        # and now the database should reflect the post of the editor
        data = TestL10nModel.objects.get(pk=1)
        self.failUnlessEqual(data.price, post_data['price'])
        self.failUnlessEqual(data.title, post_data['title'])
        self.failUnlessEqual(data.description, post_data['description'])
        self.failUnlessEqual(data.body, post_data['body'])
        

    def test_non_privileged_user_can_not_edit_restricted_fields_without_permission(self):
        
        self.client.login(username='editor', password='editor')
        
        admin_url = reverse('admin:tests_testl10nmodel_change', args=[1])
        response = self.client.get(admin_url)
        self.failUnlessEqual(response.status_code, 200)
        
        # the body and price fields should be excluded for this user
        self.assertNotContains(response, '<div class="form-row body">')
        self.assertNotContains(response, '<div class="form-row price">')
