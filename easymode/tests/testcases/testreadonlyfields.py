from django.contrib import admin
from django.contrib.admin import AdminSite
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.handlers.base import BaseHandler
from django.db import models
from django.test import TestCase, RequestFactory

from easymode.i18n.admin.decorators import L10n
from easymode.i18n.decorators import I18n


__all__ = ('EasyModeReadOnlyFieldsTest',)


class RequestMock(RequestFactory):
    """
    Construct a generic request object, with session support. """
    def request(self, **request):
        request = RequestFactory.request(self, **request)
        handler = BaseHandler()
        handler.load_middleware()
        for middleware_method in handler._request_middleware:
            if middleware_method(request):
                raise Exception("Couldn't create request mock object - "
                                "request middleware returned a response")
        return request


@I18n('computer', 'says', 'no')
class ComputerSaysNo(models.Model):
    """ Demo model. No-field is readonly in admin. """
    computer = models.CharField(max_length=255)
    says = models.CharField(max_length=255)
    no = models.CharField(max_length=255)

    class Meta:
        ordering = ('id',)

@L10n
class ComputerSaysNoAdmin(admin.ModelAdmin):
    """ Has one readonly field. """
    model = ComputerSaysNo
    readonly_fields = ('no',)


class EasyModeReadOnlyFieldsTest(TestCase):

    def setUp(self):
        self.site = AdminSite()
        self.request = None
        self.factory = RequestMock()
        self.u1 = User.objects.create_superuser(
            username='harry',
            email='bla',
            password='bla'
        )
        self.u1.backend = 'django.contrib.auth.backends.ModelBackend'

    def test_form_submit_submit_readonly(self):
        """
        Tests if form submit works with readonly fields.
        """
        ma = ComputerSaysNoAdmin(ComputerSaysNo, self.site)
        request = self.factory.get('/admin/foobar/')
        login(request, self.u1)
        form = ma.get_form(request)
        f = form({'computer': 'hallo', 'says': 'hello'})
        self.assertTrue(f.is_valid(), str(f.errors.as_text()))

    def test_form_submit_submit_no_readonly(self):
        """
        Tests if form submit works when no readonly fields are present
        """
        ma = ComputerSaysNoAdmin(ComputerSaysNo, self.site)

        request = self.factory.get('/admin/foobar/')
        login(request, self.u1)
        form = ma.get_form(request)
        f = form({'computer': 'hallo', 'says': 'hello', 'no': 'hello'})
        self.assertTrue(f.is_valid(), str(f.errors.as_text()))
