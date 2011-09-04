from django.core.urlresolvers import reverse
from django.test import TestCase

from easymode.tests.testcases import initdb


__all__ = ('TestL10nForm',)

@initdb
class TestL10nForm(TestCase):
    fixtures = ['auth-user', 'tests-top-bottom']
    