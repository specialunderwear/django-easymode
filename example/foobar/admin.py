from django.contrib import admin
from easymode.i18n.admin.decorators import L10n

from foobar.models import Foo, Bar

@L10n
class FooAdmin(admin.ModelAdmin):
    """Admin class for the Foo model"""
    model = Foo
    fieldsets = (
        (None, {
            'fields': ('bar', 'barstool')
        }),
        ('An thingy', {
            'fields': ('website', 'city', 'address')
        }),
    )

admin.site.register(Foo, FooAdmin)
admin.site.register(Bar)