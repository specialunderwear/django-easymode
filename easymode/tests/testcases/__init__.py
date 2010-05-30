import os.path
import shutil

from django.contrib.auth.models import User
from django.conf import settings

from easymode.tests.models import *

def initdb(cls):
    """
    This is a class decorator.
    
    Adds a setUp and tearDown method to a TestCase class.
    The setup will add tests to the installed apps, causing
    the models in the tests folder to be loaded.
    
    Then at the end they are removed again.
    """
    from easymode.tests.testutils import TestSettingsManager
    
    # return cls
    mgr = TestSettingsManager()
    
    def setUp(self):
        mgr.set(INSTALLED_APPS=settings.INSTALLED_APPS+[
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
            
        if hasattr(self, 'extraSetUp'):
            self.extraSetUp()
    
    def  tearDown(self):
        # don't try to remove the locale dir in the project dir because it has all translations
        # test cases should have a separate locale dir, preferably in /tmp
        if not (os.path.normpath(settings.LOCALE_DIR) == os.path.normpath(settings.PROJECT_DIR)):
            locale_dir = os.path.join(settings.LOCALE_DIR, 'locale')
            if os.path.exists(locale_dir):
                shutil.rmtree(locale_dir)
        mgr.revert()
        
    cls.setUp = setUp
    cls.tearDown = tearDown
    return cls
