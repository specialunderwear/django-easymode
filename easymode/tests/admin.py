from django.contrib import admin

from easymode.easypublisher.admin import EasyPublisher
from easymode.i18n.admin.decorators import L10n
from easymode.tests import models as test_models
from easymode.tests import forms as test_forms
from easymode.tree.admin import relation


class TestSubModelInline(admin.StackedInline):
    """docstring for TestSubModelInline"""
    model = test_models.TestSubModel
    extra = 1
    order_field = 'order'


class TestModelAdmin(relation.ForeignKeyAwareModelAdmin):
    """docstring for TestModelAdmin"""

    inlines = [TestSubModelInline]
    
    children = [test_models.TestSubModel,test_models.TestSecondSubmodel]
    invisible_in_admin = False


class SelfAwareTestModelAdmin(relation.ForeignKeyAwareModelAdmin):
    model = test_models.TestModel

@L10n(test_models.TestL10nModel)
class TestL10nModelAdmin(EasyPublisher):
    pass

class TestEasypublisherInline(admin.StackedInline):
    model = test_models.TestEasypublisherRelatedModel

class TestEasypublisherAdmin(EasyPublisher):
    inlines = [TestEasypublisherInline]

@L10n
class FormTestAdmin(admin.ModelAdmin):
    form = test_forms.OverrideForm
    model = test_models.FormTestModel

admin.site.register(test_models.TestModel, TestModelAdmin)
admin.site.register(test_models.TestSubModel)
admin.site.register(test_models.TestSecondSubmodel)
admin.site.register(test_models.TestL10nModel, TestL10nModelAdmin)
admin.site.register(test_models.TestEasypublisherModel, TestEasypublisherAdmin)
admin.site.register(test_models.ManagerErrorModel)
admin.site.register(test_models.FormTestModel, FormTestAdmin)