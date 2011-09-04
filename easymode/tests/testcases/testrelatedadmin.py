from django.core.urlresolvers import reverse
from django.test import TestCase

from easymode.tests.testcases import initdb


__all__ = ('TestRelatedAdmin',)

@initdb
class TestRelatedAdmin(TestCase):
    fixtures = ['auth-user', 'tests-top-bottom']
    
    def test_the_tree_templates_get_called(self):
        "the tree templates should be called for models with tree admins"
        
        if self.client.login(username='admin', password='admin'):
            url  = reverse('admin:tests_topmodel_change', args=[1])
            response = self.client.get(url)
        
            self.assertTemplateUsed(response,'tree/admin/edit_inline/link_inline.html')
            self.assertTemplateUsed(response, 'tree/admin/widgets/add_widget.html')
            self.assertTemplateUsed(response, 'tree/admin/widgets/link_widget.html')
        else:
            self.fail('Can not login with admin:admin')
    

        