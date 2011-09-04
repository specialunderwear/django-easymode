from django.contrib import admin

from easymode.i18n.admin.decorators import L10n
from easymode.tests import models as test_models, forms as test_forms
from easymode.tree.admin import relation
from easymode.tree.admin.relation import InvisibleModelAdmin
from easymode.tree.admin.abstract import LinkedItemAdmin, LinkInline
from easymode.tests.models import BottomModel, TopModel


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
class TestL10nModelAdmin(admin.ModelAdmin):
    pass


@L10n
class FormTestAdmin(admin.ModelAdmin):
    form = test_forms.OverrideForm
    model = test_models.FormTestModel


@L10n
class ManagerErrorModelAdmin(admin.ModelAdmin):
    model = test_models.ManagerErrorModel
    
    def delete_view(self, request, object_id, extra_context=None):
        return super(ManagerErrorModelAdmin, self).delete_view(request, object_id, extra_context)


class BottomAdmin(InvisibleModelAdmin):
    """
    I am using InvisibleModelAdmin as a base class here so I can get the
    parent_link functionality and also that BottomAdmin is not visible in
    the admin listing (see old tree for more info). I could've used
    LinkedItemAdmin as well, if I would've been interested in parent_link
    only. This is the change view for the inlined item.
    """
    parent_link = 'top'


class BottomLinkInline(LinkInline):
    """
    This is the inline view of the inlined item. It will de rendered as a
    link to the change view or add view of the inlined item.
    
    NOTE that you MUST define fields, which must only include the foreign key.
    Ofcourse you might want to include some more fields and put them as
    read_only_fields, to give a bit more info.
    """
    fields = ('top',)
    model = BottomModel


class TopAdmin(LinkedItemAdmin):
    """
    This is the top view that has the inlines. It has a special form and
    template to make it display the foreign key fields as links.
    """
    inlines = [BottomLinkInline]

admin.site.register(test_models.TestModel, TestModelAdmin)
admin.site.register(test_models.TestSubModel)
admin.site.register(test_models.TestSecondSubmodel)
admin.site.register(test_models.TestL10nModel, TestL10nModelAdmin)
admin.site.register(test_models.ManagerErrorModel, ManagerErrorModelAdmin)
admin.site.register(test_models.FormTestModel, FormTestAdmin)
admin.site.register(TopModel, TopAdmin)
admin.site.register(BottomModel, BottomAdmin)
