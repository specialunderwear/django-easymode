import re
import warnings

from django.test import TestCase
from django.utils import translation
from django.forms.models import model_to_dict
from django.core.urlresolvers import reverse

from easymode.tests.testcases import initdb
from easymode.tests.models import TestL10nModel
from easymode import tree

@initdb
class TestDiocoreFields(TestCase):
    """docstring for TestDiocoreFields"""
    
    def setup_l10n_model(self):
        translation.activate('en')
        i = TestL10nModel(title='Ik ben de groot moeftie van cambodja', 
            description="Ik weet weinig tot niks van brei cursussen",
            body="Het zou kunnen dat linksaf slaan hier een goede keuze is.",
            price=12.0,
            )
        i.save()
        return i
        
        
    def test_diocore_fields_are_special(self):
        """Diocore fields should have a font attribute after serialization"""
        i = self.setup_l10n_model()
        xml = tree.xml(i)

        title_has_font = re.search(r'field font="arial" type="CharField" name="title"', xml)
        body_has_font = re.search(r'field font="arial" type="TextField" name="body"', xml)

        self.assertTrue(title_has_font)
        self.assertTrue(body_has_font)
    
    def test_diocore_fields_strip_cariage_returns(self):
        "Diocore fields should strip cariage returns from the input"
                
        h = {
            'title': "Ik ben de groot moeftie van oeral",
            'description': "Ik weet\r weinig tot niks van brei \rcursussen",
            'body':"Het zou kunnen dat\r linksaf\r slaan hier een goede keuze is.",
            'price':34.0,
        }
        
        if self.client.login(username='admin', password='admin'):
            
            add_view_url = reverse("admin:tests_testl10nmodel_add")            
            response = self.client.post(add_view_url, h)

            i = TestL10nModel.objects.get(pk=1)

            assert(i.title == 'Ik ben de groot moeftie van oeral')
            assert(i.description == "Ik weet weinig tot niks van brei cursussen")
            assert(i.body == "Het zou kunnen dat linksaf slaan hier een goede keuze is.")
        else:
            self.fail("can not login to backend using admin/admin")