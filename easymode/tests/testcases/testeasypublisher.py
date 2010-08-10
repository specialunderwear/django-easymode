import warnings
from django.conf import settings
from django.test import TestCase
from django.conf import settings
from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from django.contrib.auth.models import User, Permission

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
    
    post_data = {
        'price': 100,
        'title': 'Your mother',
        'description': 'lmao',
        'body': 'MY BAR IS LOL HAHA',
    }
    
    username = 'editor'
    password = 'editor'
    
    def test_login_as_non_privileged_user(self):
        "It should be possible to log in as editor"
        self.assertTrue( self.client.login(username=self.username, password=self.password) )
    
    def test_login_and_post(self):
        "An editor should be able to post to the change_view of TestL10nModel"
        self.test_login_as_non_privileged_user()
                
        admin_url = reverse('admin:tests_testl10nmodel_change', args=[1])
        response = self.client.post(admin_url, self.post_data)
        self.failUnlessEqual(response.status_code, 302)
    
    def test_non_privileged_user_can_not_change_model(self):
        "All changes done by an editor to TestL10nModel should not be saved to the model table"
        self.test_login_and_post()
        
        # the contents of the first TestL10nModel should not be changed
        data = TestL10nModel.objects.get(pk=1)
        self.failIfEqual(data.price, self.post_data['price'])
        self.failIfEqual(data.title, self.post_data['title'])
        self.failIfEqual(data.description, self.post_data['description'])
        self.failIfEqual(data.body, self.post_data['body'])
    
    def test_only_one_easy_publisher_meta_data_was_created(self):
        "For each draft created by an editor, an EasyPublisherMetaData object should be created"
        self.test_non_privileged_user_can_not_change_model()
        
        # there should be a test in reversion
        metas = EasyPublisherMetaData.objects.select_related()
        self.failUnlessEqual(len(metas), 1)

        return metas[0]
        
    def test_reversion_has_the_draft(self):
        "A data belonging to a draft should be in reversion as a version"
        meta = self.test_only_one_easy_publisher_meta_data_was_created()
        
        for version in meta.revision.version_set.all():
            obj = version.get_field_dict()
            self.failUnlessEqual(obj[get_real_fieldname('title', get_language())], self.post_data['title'])
            self.failUnlessEqual(obj[get_real_fieldname('description', get_language())], self.post_data['description'])
        
    def test_publication_workflow(self):
        "After the draft is saved/published, the data should be in the model table"
        
        meta = self.test_only_one_easy_publisher_meta_data_was_created()
        
        # restoring the item will save the shizz
        for version in meta.revision.version_set.all():
            version.revert()
        
        # and now the database should reflect the post of the editor
        data = TestL10nModel.objects.get(pk=1)
        self.failUnlessEqual(data.title, self.post_data['title'])
        self.failUnlessEqual(data.description, self.post_data['description'])
        return data
        
    def test_publisher_ui_works(self):
        pass
    
    def test_non_privileged_user_can_not_edit_restricted_fields_without_permission(self):
        """If a user does not have the can_edit_global_fields permission for a
        model, untranslated fields should be hidden"""
        
        self.client.login(username=self.username, password=self.username)
        
        admin_url = reverse('admin:tests_testl10nmodel_change', args=[1])
        response = self.client.get(admin_url)
        self.failUnlessEqual(response.status_code, 200)
        
        # the body and price fields should be excluded for this user
        self.assertNotContains(response, '<div class="form-row body">')
        self.assertNotContains(response, '<div class="form-row price">')
        
        data = self.test_publication_workflow()
        self.failIfEqual(data.price, self.post_data['price'])
        self.failIfEqual(data.body, self.post_data['body'])
    
    def test_if_editor_has_permission_he_can_edit_all_fields(self):
        # give the editor permission
        editor = User.objects.get(username=self.username)
        perm = Permission.objects.get(codename='can_edit_untranslated_fields_of_testl10nmodel')
        editor.user_permissions.add(perm)
        editor.save()

        data = self.test_publication_workflow()
        self.failUnlessEqual(data.price, self.post_data['price'])
        self.failUnlessEqual(data.body, self.post_data['body'])
