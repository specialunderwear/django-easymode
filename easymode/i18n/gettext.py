"""
Gettext related functionality.
"""
import os
import re
import subprocess
import codecs
import logging
import StringIO

from datetime import datetime

from django.conf import settings
from django.core.management.base import CommandError
from django.utils.translation import templatize, to_locale, get_language
from django.utils import tzinfo
from django.template.loader import render_to_string

from easymode.tree import introspection
from easymode.utils import mutex
from easymode.utils.languagecode import get_language_codes
from easymode.utils import polib as polib_extensions

try:
    from rosetta import polib
except ImportError:
    import polib

source_re = re.compile(r'#: .*?:(\d+)', re.UNICODE)

# check if we have a crap version of xgettext
XGETTEXT_REENCODES_UTF8 = False
p = subprocess.Popen('xgettext --version', shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
(msg, err) = p.communicate()
match = re.search(r'(?P<major>\d+)\.(?P<minor>\d+)', msg)
if match:
    xversion = (int(match.group('major')), int(match.group('minor')))
    if xversion < (0, 15):
        XGETTEXT_REENCODES_UTF8 = True
 
 
class MakeModelMessages(object):
    """
    Class that can be set as a post_save signal handler.
    If done so, it will create and update a django.po file
    for each language in settings. But only if the model is
    create newly, not when it is updated manually.    
    """

    def __init__(self, location=None, sender=None):

        if location is None:
            self.location = (hasattr(settings, 'LOCALE_DIR') and settings.LOCALE_DIR) or settings.PROJECT_DIR
        elif os.path.isdir(location) is False and os.path.exists(location):
            self.location = os.path.dirname(location)
        else:
            self.location = location
            
        self.sender = sender

    
    def __call__(self, instance, sender=None, **kwargs):
        """
        Handler for the post_save signal.
        Will create a django.po file in each language,
        in the directory specified by self.location.
        """

        # no need to create translation files if not in the master site
        if not getattr(settings, 'MASTER_SITE', False):
            return
            
        if hasattr(instance, 'language') and instance.language != settings.LANGUAGE_CODE:
            return
        
        if get_language() != settings.LANGUAGE_CODE:
            return

        po_form = self.poify(instance)
        if po_form is not None:
            # for each language create a po file
            for language in get_language_codes():
                
                locale_dir = os.path.join( self.location , 'locale', to_locale(language), 'LC_MESSAGES')
                locale_file = os.path.join( locale_dir, 'django.po')

                # create locale dir if not available
                if not os.path.isdir(locale_dir):
                    os.makedirs(locale_dir)
                    
                # acquire exclusive lock this should only be run
                # by one process at a time                
                with mutex(max_wait=30):
                    # write proper header if the file is new
                    # this header contains the character set.
                    write_header = not os.path.exists(locale_file)
                    
                    if write_header: # write header and po stuffz0r
                        with codecs.open(locale_file, 'w', 'utf-8') as fp:
                            fp.write(polib_extensions.po_to_unicode(po_form))
                            
                    else: 
                        #merge existing translation with the new one
                        msg = self.msgmerge(locale_file, polib_extensions.po_to_unicode(po_form).encode('utf-8'))
                        if msg:
                            if len(po_form):
                                # add the new entries to the po file
                                with codecs.open(locale_file, 'a', 'utf-8') as fp:
                                    for entry in po_form: # this avoids printing the header
                                        fp.write(u"\n")
                                        fp.write(polib_extensions.po_to_unicode(entry))
                                        
                                # filter away duplicates  
                                msg = self.msguniq(locale_file)
                                # save entire po file once more and overwrite with filtered shizzle
                                with open(locale_file, 'w') as fp:
                                    fp.write(msg)                                

    
    def poify(self, model):
        """turn a django model into a po file."""
        if not hasattr(model, 'localized_fields'):
            return None
        
        # create po stream with header
        po_stream = polib_extensions.PoStream(StringIO.StringIO(self.po_header)).parse()
        
        for (name, field) in introspection.get_default_field_descriptors(model):
            occurrence = u"%s.%s.%s" % (model._meta.app_label, model.__class__.__name__, name)
            value = field.value_to_string(model)
            
            # only add empty strings
            if value != "":                
                entry = polib.POEntry(msgid=value, occurrences=[(occurrence, model.pk)])
                # make sure no duplicate entries in the po_stream
                existing_entry = po_stream.find(entry.msgid)
                if existing_entry is None:
                    po_stream.append(entry)
                else:
                    # no really, existing_entry.merge does not merge the occurrences.
                    existing_entry.occurrences += entry.occurrences
        
        return po_stream
    

    def xgettext(self, template):
        """Extracts to be translated strings from template and turns it into po format."""
        
        cmd = 'xgettext -d django -L Python --keyword=gettext_noop --keyword=gettext_lazy --keyword=ngettext_lazy:1,2 --from-code=UTF-8 --output=- -'

        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (msg, err) = p.communicate(input=templatize(template))
        
        if err:
            # dont raise exception, some stuff in stderr are just warmings
            logging.warning(err)

        if XGETTEXT_REENCODES_UTF8:
            return msg.decode('utf-8').encode('iso-8859-1')
                    
        return msg

    
    def po_stream(self, po_string):
        """make a po stream object from a po_string"""
        return polib_extensions.PoStream(StringIO.StringIO(po_string)).parse()


    def msgmerge(self, locale_file, po_string):
        """
        Runs msgmerge on a locale_file and po_string
        """
        
        cmd = "msgmerge -q %s -" % locale_file
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        (msg, err) = p.communicate(input=po_string)
        
        if err:
            # dont raise exception, some stuff in stderr are just warmings
            logging.warning("%s \nfile: %s\npostring: %s" % (err, locale_file, po_string))
        
        return msg

        
    def msguniq(self, locale_file):
        """
        run msgunique on the locale_file
        """
        
        # group related language strings together.
        # except if no real entries where written or the header will be removed.
        p = subprocess.Popen('msguniq --to-code=utf-8 %s' % (locale_file,), shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE )
        (msg, err) = p.communicate()
    
        if err:
            # raise exception, none of the stuff in stderr are just warmings
            logging.error(err)
            try:
                err = unicodedata.normalize('NFKD', err.decode('utf-8')).encode('ascii','ignore')
            except UnicodeError:
                err = "can not decode error message"
            raise CommandError(u"error happened while running msguniq on: %s %s" % (locale_file, err))

        return msg
        
            
    @property
    def po_header(self):
        localtime = tzinfo.LocalTimezone( datetime.now() )
        now = datetime.now(localtime).isoformat()
        po_header = render_to_string('i18n/po_header.txt', { 
            'creation_date': now,
            'revision_date': now,
            'last_translator' : u'anonymous',
            'last_translator_email' : u'anonymous@example.com',
            'language_team' : u'anonymous',
            'language_team_email': u'anonymous@example.com',
        })

        return po_header
