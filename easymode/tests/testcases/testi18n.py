# -*- coding: utf-8 -*-
import warnings
import re
import shutil
import os
import errno
import gc
import time

import gettext as gettext_module
from hashlib import sha1

from os.path import join, isdir


from django.test import TestCase
from django.db.models.signals import post_save
from django.conf import settings
from django.utils import translation
from django.utils.translation import trans_real

if 'rosetta' in settings.INSTALLED_APPS:
    from rosetta import polib
else:
    import polib

from easymode.utils import first_match, mutex, SemaphoreException
from easymode.utils.languagecode import get_language_codes
from easymode.i18n import meta
from easymode.tests.testcases import initdb
from easymode.tests import models
from easymode.i18n.gettext import MakeModelMessages
from easymode.i18n import gettext
from easymode.tests.testutils.scriptutil import ffindgrep
from easymode import tree

if 'de' not in get_language_codes():
    raise Exception('the language "de" must be in your LANGUAGES to run the test suite')
if 'en-us' not in get_language_codes():
    raise Exception('the language "en-us" must be in your LANGUAGES to run the test suite')

if settings.LANGUAGE_CODE is not 'en':
    raise Exception('To run the test suite the LANGUAGE_CODE must be set to "en"')

@initdb
class Testi18n(TestCase):
    """tests for the internationalisation/localisation support"""

    def extraSetUp(self):        
        gc.collect()
        translation.activate(settings.LANGUAGE_CODE)
        
        try:
            t = models.TestModel(charfield='Hoi Ik ben de root node')
            t.save()
            f = t.submodels.create(subcharfield="Hoi Ik ben de first level sub node", subintegerfield=10)
            s = t.submodels.create(subcharfield="Hoi ik ben de tweede first level sub node", subintegerfield=100)
            w = t.secondsubmodels.create(ultrafield="Sed tempor. Ut felis. Maecenas erat.")
            f.subsubmodels.create(subsubcharfield="Hoi ik ben de thord level sub node")
            f.subsubmodels.create(subsubcharfield="Hoi ik ben de third level sub node")
            s.subsubmodels.create(subsubcharfield="Hoi ik ben de third level sub node")
            s.subsubmodels.create(subsubcharfield="Hoi ik ben de third level sub node")        
            t.save()            
        except OSError as e:
            if e.errno == 24:
                print "hai er zit een bug in de mutex"

    # some vars
    title_en = 'HI I GUESS I AM THE TITLE IN ENGLISH'
    title_de = 'ICH LIEBE DICH'

    arr = [None, None, None, 'hai', 'True', True, 'last']
    
    def setup_l10n_model(self):
        translation.activate('en')
        i = models.TestL10nModel(title="Ik ben de groot moeftie van cambodja", 
            description="Ik weet weinig tot niks van brei cursussen", 
            body="Het zou kunnen dat linksaf slaan hier een goede keuze is.",
            price=12.0,
            )
        i.save()
        return i
    
    def setup_mofile_with_entry(self, poentry, language='en'):
        locale_location = join(settings.LOCALE_DIR, 'locale', language, 'LC_MESSAGES')
        pofile = polib.pofile(join(locale_location, 'django.po'))

        pofile.append(poentry)
        pofile.save()
        pofile.save_as_mofile(join(locale_location, 'django.mo'))
        
        jit_locale = gettext_module.translation('django', join(settings.LOCALE_DIR, 'locale'), [trans_real.to_locale(language)], trans_real.DjangoTranslation)
        jit_locale.set_language(language)
        
        locale = trans_real.translation(language)
        locale.merge(jit_locale)
        
    
    def test_locale_dir_is_not_project_dir(self):
        """The locale dir should be somewhere safe"""
        assert(not (os.path.normpath(settings.LOCALE_DIR) == os.path.normpath(settings.PROJECT_DIR)))
        
    def test_save_signal_is_caught(self):
        """when a model is saved a signal should be caught"""

        def stub(sender, **kwargs):
            self.save_was_caught = True
            self.save_was_a_created = kwargs['created']

        self.save_was_caught = False
            
        post_save.connect(stub, models.TestModel)
        i = models.TestModel.objects.get(pk=1)
        i.charfield = 'hai mom'
        i.save()
        assert(self.save_was_caught)
        
    def test_created_property_is_set(self):
        """A signal sent when a model is created should have the created property set to true"""
        def stub(sender, **kwargs):
            self.save_was_caught = True
            self.save_was_a_created = kwargs['created']

        self.save_was_caught = False
        self.save_was_a_created = False
        
        post_save.connect(stub, models.TestModel)
        i = models.TestModel(charfield='hai mother')
        i.save()
        assert(self.save_was_caught)
        assert(self.save_was_a_created)

    def test_we_have_the_proper_version_of_gettext(self):
        """The proper version of xgettext (>= 0.15) should be installed on the server."""
        
        if gettext.XGETTEXT_REENCODES_UTF8 is True:
            warnings.warn('while not fatal it is better to install a version of gettext \
                higher or equal to 0.15')
                    
    def test_model_can_be_serialized(self):
        """A model should be serializable to po"""
        db_gettext = MakeModelMessages()
        i = models.TestModel.objects.get(pk=1)

        m = str(db_gettext.poify(i))

        assert(m.index('msgid "Hoi Ik ben de root node"') is not None)
    
    def test_model_to_po(self):
        """A newly created model should be serialized to po"""
        locale_dir = join(settings.LOCALE_DIR, 'locale')
        if isdir(locale_dir):
            shutil.rmtree(locale_dir)
            
        assert(not isdir(locale_dir))
        i = models.TestModel(charfield='ik word serialized to po')
        i.save()
        assert(isdir(locale_dir))
        
        result = ffindgrep(locale_dir, ['^msgid "ik word serialized to po"$'])
        assert(result != {})
        
    def test_meta(self):
        """Transmeta should have a title_en as well as a title is default locale is en"""
        i = self.setup_l10n_model()
        
        assert(i.title_en == i.title == 'Ik ben de groot moeftie van cambodja')
    
    def test_first_true(self):

        assert(first_match(lambda x: x or None, self.arr))

    def test_meta_field_finder(self):
        """The correct localised version of the title property should be found"""
        field = meta.get_localized_property(self, 'title')
        assert(field == self.title_en)
        translation.activate('de')
        field = meta.get_localized_property(self, 'title')
        assert(field == self.title_de)

    def test_meta_get_localized_field_name(self):
        """Transmeta's get_localized_field_name should return the correct localized property name"""
        field = meta.get_localized_field_name(self, 'title')
        assert(field == 'title_en')
            
    def test_meta_now_selects_correct_field_on_propert_write(self):
        """Transmeta should write to title_en if language is en and property is title"""            
        i = self.setup_l10n_model()
        i.title = 'ik wijzig em ff ok?'
        i.save()
        assert(i.title == i.title_en == 'ik wijzig em ff ok?')
    
    def test_ugettext_lazy(self):
        """ugettext_lazy should return translated strings, if they are in the locale"""

        self.setup_l10n_model()
        
        poentry = polib.POEntry(msgid='test string', msgstr='LOL DID YOU REALLY THINK I WAS NUB?')
        
        self.setup_mofile_with_entry(poentry)
        
        lol = translation.ugettext_lazy("test string")
        assert(unicode(lol) == u'LOL DID YOU REALLY THINK I WAS NUB?')
    
    def test_adding_l10n_decorator_means_model_gets_rendered_to_po_file(self):
        """If a model is created, which is decorated with l10n, it should be added to the po file"""
        self.setup_l10n_model()

        result = ffindgrep(join(settings.LOCALE_DIR, 'locale'), 
            ['^msgid "Ik ben de groot moeftie van cambodja"$'])
        assert(result != {})
        
    def test_nulled_translations_get_translated_from_po_file(self):
        """If a property which is a translation is accessed but it is None, the translation from the po file should be used"""
        i = self.setup_l10n_model()
        
        assert(i.title == i.title_en == u'Ik ben de groot moeftie van cambodja')
        
        poentry = polib.POEntry(msgid=u'Ik ben de groot moeftie van cambodja', msgstr=u'Ik ben een zwerver')        
        self.setup_mofile_with_entry(poentry, 'de')
        
        translation.activate('de')

        assert(i.title_de is None)
        assert(i.title == u'Ik ben een zwerver')
    
    def test_translations_that_are_not_null_should_not_come_from_the_po_file(self):
        """If a translation is not null, that value should be returned."""
        i = self.setup_l10n_model()
        i.title_de = u'Ik ben een konijntje'
        i.save()
        
        assert(i.title == i.title_en == u'Ik ben de groot moeftie van cambodja')
        poentry = polib.POEntry(msgid=u'Ik ben de groot moeftie van cambodja', msgstr=u'Ik ben een zwerver')        
        self.setup_mofile_with_entry(poentry, 'de')
        
        translation.activate('de')

        assert(i.title_de is not None)
        assert(not (i.title == u'Ik ben een zwerver'))
        assert(i.title == u'Ik ben een konijntje')
        
    def test_translated_fields_handle_correctly_under_to_xml(self):
        """A field that is translated should show the correct value when converted to xml"""

        i = self.setup_l10n_model()

        poentry = polib.POEntry(msgid=u'Ik ben de groot moeftie van cambodja', msgstr=u'Ik ben een zwerver')        
        self.setup_mofile_with_entry(poentry, 'de')

        xml_representation = tree.xml(i)

        # todo:
        # DefaultFieldDescriptor is now serialized as a charfield type.
        # add the different serializable types to the xslt and the test should be able
        # to verify the correct workings then.
        # contains_default_field_descriptor = re.search(r'DefaultFieldDescriptor', xml_representation)
        # self.assertTrue(contains_default_field_descriptor)
        
        contains_moeftie = re.search(r'Ik ben de groot moeftie van cambodja', xml_representation)
        contains_konijntje = contains_konijntje = re.search(r'Ik ben een konijntje', xml_representation)        
        self.assertTrue(contains_moeftie)
        self.assertFalse(contains_konijntje)

        translation.activate('de')
        i.title = u'Ik ben een duits konijntje'
        xml_representation = tree.xml(i)
        contains_konijntje = re.search(r'Ik ben een duits konijntje', xml_representation)
        self.assertTrue(contains_konijntje)

        i.title_de = u'Ik ben geen konijntje'
        i.save()

        xml_representation = tree.xml(i)
        contains_konijntje = re.search(r'Ik ben geen konijntje', xml_representation)
        self.assertTrue(contains_konijntje)
                
    def test_semaphore(self):
        """the semaphore should bind a file to the context and hold on to it untill after the context is closed"""
        lockfile = join('/tmp', sha1(settings.SECRET_KEY).hexdigest() +'.semaphore')
        for a in range(1, 4):
            with mutex():
                assert(os.path.isfile(lockfile))
        
            assert(not os.path.exists(lockfile))

    def test_semaphore_exception(self):
        """The semaphore should throw an exception when the wait time is over"""
        lockfile = join('/tmp', sha1(settings.SECRET_KEY).hexdigest() +'.semaphore')
        try:
            with mutex(max_wait=0, lockfile=lockfile):
                with mutex(max_wait=0, lockfile=lockfile):
                    pass
        except SemaphoreException as e:
            pass
        else:
            self.fail('Should have triggered SemaphoreException')
        self.assertFalse(os.path.exists(lockfile))
        
    def test_fdopen_works_correctly(self):
        """fdopen should allow proper locking"""
        lockfile = join('/tmp', sha1(settings.SECRET_KEY).hexdigest() +'.semaphore')
        
        try:
            ty = os.open(lockfile, os.O_EXCL | os.O_RDWR | os.O_CREAT)
            fd = os.open(lockfile, os.O_EXCL | os.O_RDWR | os.O_CREAT)
        except OSError as e:
            self.assertEqual(e.errno, errno.EEXIST)
        else:
            self.fail("If the file exists an OSError should be thrown")
        finally:
            os.remove(lockfile)