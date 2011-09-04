from django.core.urlresolvers import reverse
from django.test import TestCase
from django.utils.translation import get_language, activate

from easymode.tests.testcases import initdb
from easymode.utils.languagecode import fix_language_code


ADD_BUTTON = """<a href="%s" class="add-another" onclick="return showAddAnotherPopup(this);">
    <img src="/admin/media/img/admin/icon_addlink.gif" width="10" height="10" """

__all__ = ('TestRelatedAdmin',)

@initdb
class TestRelatedAdmin(TestCase):
    fixtures = ['auth-user', 'tests-top-bottom']
    
    def test_the_tree_templates_get_called(self):
        "the tree templates should be called for models with tree admins"
        
        if self.client.login(username='admin', password='admin'):
            url = reverse('admin:tests_topmodel_change', args=[1])
            response = self.client.get(url)

            self.assertTemplateUsed(response, 'tree/admin/change_form_with_parent_link.html')
            self.assertTemplateUsed(response,'tree/admin/edit_inline/link_inline.html')
            self.assertTemplateUsed(response, 'tree/admin/widgets/add_widget.html')
            self.assertTemplateUsed(response, 'tree/admin/widgets/link_widget.html')
        else:
            self.fail('Can not login with admin:admin')
    
    def test_adding_new_inline_adds_it_in_the_top_model_view(self):
        "adding a bottom model should make it appear in inlines"
        
        if self.client.login(username='admin', password='admin'):
            top_url = reverse('admin:tests_topmodel_change', args=[1])
            response = self.client.get(top_url)
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, 'Chicken is good')
            
            bottom_url = reverse('admin:tests_bottommodel_add')
            data = {
                'top':1,
                'comment':'Chicken is good',
            }
            response = self.client.post(bottom_url, data)
            self.assertEqual(response.status_code, 302)
            
            response = self.client.get(top_url)
            self.assertContains(response, 'Chicken is good')
        else:
            self.fail('Can not log in with admin:admin')
    
    def test_the_plus_button_goes_to_the_correct_add_view(self):
        "There should be a plus button for the inline group that goes to the correct add view"
        if self.client.login(username='admin', password='admin'):
            top_url = reverse('admin:tests_topmodel_change', args=[1])
            response = self.client.get(top_url)
            self.assertEqual(response.status_code, 200)
            
            #/en/admin/tests/bottommodel/add/?top=1
            add_url = "%s?top=1" % reverse('admin:tests_bottommodel_add')
            localized_add_url = fix_language_code(add_url, get_language())
            
            self.assertContains(response, ADD_BUTTON % localized_add_url)
            
            # test the same for a different locale
            activate('de')
            self.assertEqual('de', get_language())
            localized_add_url = fix_language_code(add_url, get_language())
            localized_top_url = fix_language_code(top_url, get_language())
            response = self.client.get(localized_top_url)
            self.assertEqual(response.status_code, 200)
            self.assertContains(response, ADD_BUTTON % localized_add_url)
            
        else:
            self.fail('Can not log in with admin:admin')

    def test_add_button_is_not_shown_in_add_view(self):
        "The add button must be hidden in the add view because you can't add nothing to an object that does not exist yet"
        if self.client.login(username='admin', password='admin'):
            top_url = reverse('admin:tests_topmodel_add')
            response = self.client.get(top_url)
            
            add_url = "%s?top=None" % reverse('admin:tests_bottommodel_add')
            localized_add_url = fix_language_code(add_url, get_language())
            
            self.assertNotContains(response, ADD_BUTTON % localized_add_url)