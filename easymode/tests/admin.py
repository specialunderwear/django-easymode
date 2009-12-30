
from django.contrib import admin

from easymode.tests.models import TestSubModel, TestModel, TestSecondSubmodel, TestL10nModel
from easymode.tree.admin import relation

from easymode.i18n.admin.decorators import L10n
from easymode.easypublisher.admin import EasyPublisher

class TestSubModelInline(admin.StackedInline):
# class TestSubModelInline(inline.RecursiveInline):
# class TestSubModelInline(admin.SelectorInline):
    """docstring for TestSubModelInline"""
    model = TestSubModel
    extra = 1
    order_field = 'order'

        
class TestModelAdmin(relation.ForeignKeyAwareModelAdmin):
# class TestModelAdmin(admin.ModelAdmin):
    """docstring for TestModelAdmin"""
    # fieldsets = [
    #     ('main name', {'fields': ['charfield'], 'classes': ['collapse']})
    # ]
    inlines = [TestSubModelInline]
    
    children = [TestSubModel,TestSecondSubmodel]
    invisible_in_admin = False
    
class SelfAwareTestModelAdmin(relation.ForeignKeyAwareModelAdmin):
    model = TestModel

@L10n(TestL10nModel)
class TestL10nModelAdmin(EasyPublisher):
    pass


admin.site.register(TestModel, TestModelAdmin)
admin.site.register(TestSubModel)
admin.site.register(TestSecondSubmodel)
admin.site.register(TestL10nModel, TestL10nModelAdmin)
