from django.contrib import admin
from easymode.i18n.admin.decorators import L10n
from easymode.tree.admin.relation import ForeignKeyAwareModelAdmin, InvisibleModelAdmin

from foobar.models import Foo, Bar

class BarAdmin(InvisibleModelAdmin):
    model = Bar
    parent_link = 'foo'

@L10n
class FooAdmin(ForeignKeyAwareModelAdmin):
    """Admin class for the Foo model"""
    model = Foo
    invisible_in_admin = False
    
    fieldsets = (
        (None, {
            'fields': ('bar', 'barstool')
        }),
        ('An thingy', {
            'fields': ('website', 'city', 'address')
        }),
    )

admin.site.register(Foo, FooAdmin)
admin.site.register(Bar, BarAdmin)