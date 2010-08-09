import os.path
import shutil
from functools import wraps

from django.conf import settings

from easymode.tests.testutils import TestSettingsManager


def initdb(cls):
    """
    This is a class decorator.
    
    Adds a setUp and tearDown method to a TestCase class.
    The setup will add tests to the installed apps, causing
    the models in the tests folder to be loaded.
    
    Then at the end they are removed again.
    """
    
    orig_pre_setup = getattr(cls, '_pre_setup')
    orig_post_teardown = getattr(cls, '_post_teardown')
    
    @wraps(orig_pre_setup)
    def _pre_setup(self):
        self.settingsManager = TestSettingsManager()
        self.settingsManager.set(INSTALLED_APPS=settings.INSTALLED_APPS+[
            'easymode',
            'easymode.tests',
            ],
        )
                
        for skipped_test in getattr(settings , 'SKIPPED_TESTS', []):
            if hasattr(cls, skipped_test):
                setattr(cls, skipped_test, lambda x: True)
        
        if orig_pre_setup:
            orig_pre_setup(self)
    
    @wraps(orig_post_teardown)
    def _post_teardown(self):
        if orig_post_teardown:
            orig_post_teardown(self)
        # don't try to remove the locale dir in the project dir because it has all translations
        # test cases should have a separate locale dir, preferably in /tmp
        if not (os.path.normpath(settings.LOCALE_DIR) == os.path.normpath(settings.PROJECT_DIR)):
            locale_dir = os.path.join(settings.LOCALE_DIR, 'locale')
            if os.path.exists(locale_dir):
                shutil.rmtree(locale_dir)
        self.settingsManager.revert()
        
    cls._pre_setup = _pre_setup
    cls._post_teardown = _post_teardown
    return cls
