from django.contrib import admin
from easymode.i18n.admin.decorators import L10n

from foobar.models import Foo

@L10n
class FooAdmin(admin.ModelAdmin):
    """Admin class for the Foo model"""
    model = Foo

admin.site.register(Foo, FooAdmin)