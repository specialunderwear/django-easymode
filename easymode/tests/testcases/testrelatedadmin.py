from hashlib import md5

from django.test import TestCase
from django.contrib import admin
from django.forms.formsets import BaseFormSet
from django.test.client import Client

from easymode.tests.models import *
from easymode.tests.admin import TestModelAdmin, SelfAwareTestModelAdmin
from easymode.tests.testcases import initdb

from easymode.tree.admin.widgets import foreignkey
# from tree.admin import forms
from easymode.tree.admin import relation
OUTPUT = """    <a href=""></a><br>
"""

@initdb
class TestRelatedAdmin(TestCase):
    
    def extraSetUp(self):
        t = TestModel(charfield='Hoi Ik ben de root node')
        t.save()
        f = t.submodels.create(subcharfield="Hoi Ik ben de first level sub node", subintegerfield=10)
        s = t.submodels.create(subcharfield="Hoi ik ben de tweede first level sub node", subintegerfield=100)
        w = t.secondsubmodels.create(ultrafield="Sed tempor. Ut felis. Maecenas erat.")
        f.subsubmodels.create(subsubcharfield="Hoi ik ben de thord level sub node")
        f.subsubmodels.create(subsubcharfield="Hoi ik ben de third level sub node")
        s.subsubmodels.create(subsubcharfield="Hoi ik ben de third level sub node")
        s.subsubmodels.create(subsubcharfield="Hoi ik ben de third level sub node")        
        t.save()
            
    def test_empty_widget(self):
        dummy = foreignkey.EmptyWidgetThatDoesNothing()
        output = dummy.render("fieldname", "field value")
        assert(output == OUTPUT)
        
    def test_related_admin(self):
        rel = TestModelAdmin(TestModel, admin.site)
        formset_array = rel.extra_forms(1)
        assert(isinstance(formset_array[0], BaseFormSet))
    
    def test_there_are_two_forms(self):
        """because there are two models marked as chlidren in the modelamin"""
        rel = TestModelAdmin(TestModel, admin.site)
        formset_array = rel.extra_forms(1)
        assert(len(formset_array) == 2)
        
    def test_self_aware_related_admin(self):
        rel = SelfAwareTestModelAdmin(TestModel, admin.site)
        formset_array = rel.extra_forms(1)
        assert(isinstance(formset_array[0], BaseFormSet))
    
    def test_admin_with_extra_fields_are_displayed(self):
        response = self.client.login(username='admin', password='admin')
        response = self.client.get('/admin/tests/testmodel/1/')
        self.assertTemplateUsed(response, 'tree/admin/widgets/foreignkeylink.html')
        self.assertContains(response, 'Sed tempor. Ut felis. Maecenas erat.')
    
    def test_there_are_more_than_one_forms(self):
        rel = SelfAwareTestModelAdmin(TestModel, admin.site)
        formset_array = rel.extra_forms(1)
        assert(isinstance(formset_array[0], BaseFormSet))
        assert(isinstance(formset_array[1], BaseFormSet))
        
    def test_admin_template_for_change_is_different(self):        
        response = self.client.login(username='admin', password='admin')
        response = self.client.get('/admin/tests/testmodel/1/')
        self.assertTemplateUsed(response,'tree/admin/change_form_with_related_links.html')
        
