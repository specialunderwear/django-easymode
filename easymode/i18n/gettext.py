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
from django.template.loader import find_template_source
from django.utils.translation import templatize, to_locale, get_language
from django.utils import tzinfo
from django.template.defaultfilters import slugify
from django.template.loader import render_to_string
from django.utils.encoding import smart_unicode

from rosetta import polib

from easymode.xslt import transform
from easymode.i18n import serializers
from easymode.utils import mutex
from easymode.utils.languagecode import get_language_codes

DEFAULT_XSLT = 'xslt/gettext.xslt'

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

        
class PoStream(polib._POFileParser):
    """Create a POFile object from a StringIO"""
    
    def __init__(self, fpath, stream, encoding='utf-8', wrapwidth=78):
        """a pofileparser that can read from a stream"""
        self.fhandle = stream
        self.instance = polib.POFile(fpath=fpath, encoding=encoding)
        self.instance.wrapwidth = wrapwidth
        self.transitions = {}
        self.current_entry = polib.POEntry()
        self.current_state = 'ST'
        self.current_token = None
        self.msgstr_index = 0
        self.entry_obsolete = 0
        all_ = ['ST', 'HE', 'GC', 'OC', 'FL', 'TC', 'MS', 'MP', 'MX', 'MI']

        self.add('TC', ['ST', 'HE'],                                     'HE')
        self.add('TC', ['GC', 'OC', 'FL', 'TC', 'MS', 'MP', 'MX', 'MI'], 'TC')
        self.add('GC', all_,                                             'GC')
        self.add('OC', all_,                                             'OC')
        self.add('FL', all_,                                             'FL')
        self.add('MI', ['ST', 'HE', 'GC', 'OC', 'FL', 'TC', 'MS', 'MX'], 'MI')
        self.add('MP', ['TC', 'GC', 'MI'],                               'MP')
        self.add('MS', ['MI', 'MP', 'TC'],                               'MS')
        self.add('MX', ['MI', 'MX', 'MP', 'TC'],                         'MX')
        self.add('MC', ['MI', 'MP', 'MS', 'MX'],                         'MC')
 
 
class MakeModelMessages(object):
    """
    Class that can be set as a post_save signal handler.
    If done so, it will create and update a django.po file
    for each language in settings. But only if the model is
    create newly, not when it is updated manually.    
    """

    def __init__(self, location=None, sender=None, xslt=DEFAULT_XSLT):

        if location is None:
            self.location = (hasattr(settings, 'LOCALE_DIR') and settings.LOCALE_DIR) or settings.PROJECT_DIR
        elif os.path.isdir(location) is False and os.path.exists(location):
            self.location = os.path.dirname(location)
        else:
            self.location = location
            
        self.sender = sender
        self.xslt = xslt

    
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
                            fp.write(smart_unicode(po_form))
                            
                    else: 
                        #merge existing translation with the new one
                        msg = self.msgmerge(locale_file, po_form)
                        if msg:
                            postream = self.po_stream(msg)
                            if len(postream):
                                # add the new entry to the po file
                                with codecs.open(locale_file, 'a', 'utf-8') as fp:
                                    for entry in postream:
                                        fp.write("\n")
                                        fp.write(smart_unicode(entry))
                                        
                                # filter away duplicates  
                                msg = self.msguniq(locale_file)
                                # save entire po file once more and overwrite with filtered shizzle
                                with open(locale_file, 'w') as fp:
                                    fp.write(msg)                                

    
    def poify(self, model):
        """turn a django model into a po file."""

        xml = u'<root/>'
        try:
            xml = serializers.serialize_with_locale([model])
        except AttributeError as e:
            print e
            return None
        
        xslt_path = find_template_source(self.xslt)[0]
        result = transform(xml, xslt_path)

        po = self.xgettext(result)
        po = source_re.sub('#: ' + str(slugify(model)) + ':\\1'  , po)
        po = po.replace('charset=CHARSET', 'charset=UTF-8')
        return po


    def xgettext(self, template):
        """Extracts to be translated strings from template and turns it into po format."""
        
        cmd = 'xgettext -d django -L Python --keyword=gettext_noop --keyword=gettext_lazy --keyword=ngettext_lazy:1,2 --from-code=UTF-8 --output=- -'

        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (msg, err) = p.communicate(input=templatize(template))
        
        if err:
            # dont raise exception, some stuff in stderr are just warmings
            logging.debug(err)

        if XGETTEXT_REENCODES_UTF8:
            return msg.decode('utf-8').encode('iso-8859-1')
                    
        return msg

    
    def po_stream(self, po_string):
        """make a po stream object from a po_string"""
        return PoStream(None, StringIO.StringIO(po_string)).parse()


    def msgmerge(self, locale_file, po_string):
        """
        Runs msgmerge on a locale_file and po_string
        """
        
        cmd = "msgmerge -q %s -" % locale_file
        p = subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE) 
        (msg, err) = p.communicate(input=po_string)
        
        if err:
            # dont raise exception, some stuff in stderr are just warmings
            logging.debug(err)
        
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
            logging.debug(err)
            raise CommandError("error happened while running msguniq on: " + locale_file + err + open(locale_file, 'r').read())

        return msg
        
            
    @property
    def po_header(self):
        localtime = tzinfo.LocalTimezone( datetime.now() )
        now = datetime.now(localtime)
        po_header = render_to_string('i18n/po_header.txt', { 
            'creation_date': now,
            'revision_date': now,
            'last_translator' : u'anonymous',
            'last_translator_email' : u'anonymous@example.com',
            'language_team' : u'anonymous',
            'language_team_email': u'anonymous@example.com',
        })

        return po_header
