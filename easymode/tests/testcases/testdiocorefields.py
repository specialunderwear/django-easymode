import re

from django.test import TestCase
from django.utils import translation

from easymode.tests.testcases import initdb
from easymode.tests.models import TestL10nModel
from easymode import tree

@initdb
class TestDiocoreFields(TestCase):
    """docstring for TestDiocoreFields"""
    
    def setup_l10n_model(self):
        translation.activate('en')
        i = TestL10nModel(title="Ik ben de groot moeftie van cambodja", 
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
