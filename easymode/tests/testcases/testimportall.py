import sys
from django.test import TestCase

error_while_importing = None

try:
    from easymode import *
    from easymode.admin import *
    from easymode.admin.forms import *
    from easymode.admin.models import *
    from easymode.debug import *
    from easymode.i18n import *
    from easymode.i18n.admin import *
    from easymode.management import *
    from easymode.middleware import *
    from easymode.management.commands import *
    from easymode.templatetags import *
    from easymode.tree import *
    from easymode.tree.admin import *
    from easymode.tree.admin.widgets import *
    from easymode.urls import *
    from easymode.utils import *
    from easymode.views import *
    from easymode.xslt import *
except Exception as e:
    error_while_importing = e

__all__ = ('TestImportAll',)

class TestImportAll(TestCase):
    """Check if the import all works for every package in easymode"""

    def test_import_all(self):
        """All easymode packages should be importable with * without any errors""" 
        if error_while_importing is not None:
            self.fail("%s: %s" % (type(e).__name__, error_while_importing))