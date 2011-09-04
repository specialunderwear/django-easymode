from django.core.urlresolvers import reverse
from django.test import TestCase

from easymode.tests.models import TestL10nModel
from easymode.tests.testcases import initdb


__all__ = ('TestSafeFields',)

@initdb
class TestSafeFields(TestCase):
    "Test for fields that strip cariage returns."
    
    fixtures = ['auth-user', 'tests-testl10nmodel']
    
    def test_safe_fields_strip_cariage_returns(self):
        "Safe fields should strip cariage returns from the input"
                
        h = {
            'title': "Ik ben de groot moeftie van oeral",
            'description': "Ik weet\r weinig tot niks van brei \rcursussen",
            'body':"Het zou kunnen dat\r linksaf\r slaan hier een goede keuze is.",
            'price':34.0,
        }
        
        if self.client.login(username='admin', password='admin'):
            
            add_view_url = reverse("admin:tests_testl10nmodel_add")            
            response = self.client.post(add_view_url, h)

            i = TestL10nModel.objects.get(pk=3)

            assert(i.title == 'Ik ben de groot moeftie van oeral')
            assert(i.description == "Ik weet weinig tot niks van brei cursussen")
            assert(i.body == "Het zou kunnen dat linksaf slaan hier een goede keuze is.")
        else:
            self.fail("can not login to backend using admin/admin")
