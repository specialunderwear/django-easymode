from functools import wraps
import os.path
import shutil

from django.contrib.auth.models import User
from django.conf import settings
from easymode.tests.models import *
from easymode.tests.testutils import TestSettingsManager

def initdb(cls):
    """
    This is a class decorator.
    
    Adds a setUp and tearDown method to a TestCase class.
    The setup will add tests to the installed apps, causing
    the models in the tests folder to be loaded.
    
    Then at the end they are removed again.
    """
    
    orig_setup = cls.setUp
    orig_teardown = cls.tearDown
    
    @wraps(orig_setup)
    def setUp(self):
        self.settingsManager = TestSettingsManager()
        self.settingsManager.set(INSTALLED_APPS=settings.INSTALLED_APPS+[
            'easymode',
            'easymode.tests',
            ],
        )
        
        u = User(username="admin")
        u.set_password("admin")
        u.is_staff = True
        u.is_active = True
        u.is_superuser = True 
        u.save()
        
        for skipped_test in getattr(settings , 'SKIPPED_TESTS', []):
            if hasattr(cls, skipped_test):
                setattr(cls, skipped_test, lambda x: True)

        orig_setup(self)
    
    @wraps(orig_teardown)
    def tearDown(self):
        orig_teardown(self)
        # don't try to remove the locale dir in the project dir because it has all translations
        # test cases should have a separate locale dir, preferably in /tmp
        if not (os.path.normpath(settings.LOCALE_DIR) == os.path.normpath(settings.PROJECT_DIR)):
            locale_dir = os.path.join(settings.LOCALE_DIR, 'locale')
            if os.path.exists(locale_dir):
                shutil.rmtree(locale_dir)
        self.settingsManager.revert()
        
    cls.setUp = setUp
    cls.tearDown = tearDown
    return cls
