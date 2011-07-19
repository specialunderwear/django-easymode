"""
Fields used by easymode's i18n.meta package which modifies a class to enable i18n.
"""
from django.conf import settings
from django.utils import translation
from django.utils.encoding import force_unicode
from django.utils.translation.trans_real import translation as translation_catalogs

from easymode.i18n.meta.value import GettextVO
from easymode.i18n.meta.utils import get_localized_property, valid_for_gettext, \
    get_fallback_languages, get_localized_field_name
from easymode.utils.languagecode import get_real_fieldname
from easymode.utils.standin import standin_for

class DefaultFieldDescriptor(property):
    """
    Descriptor that implements access to the default language.
    It inherits property because django wants that, it doesn't process
    it as a field if it is not isinstance(self, property)
    """

    def __init__(self, name, **kwargs):
        """The name param is the name of the field the descriptor is emulating."""
        self.name = name
        self.__dict__.update(kwargs)

    def __get__(self, obj, typ=None):
        """
        Read the localised version of the field this descriptor emulates.
        First try to see if the localised field is really set.
        If not, then use ugettext_lazy to find a tranlation in the current language
        for this field.
        """
        # self must be returned in a getattr context.
        if obj is None:
            return self

        current_language = translation.get_language()
        real_field_name = get_real_fieldname(self.name, current_language)

        vo = GettextVO()
        
        # first check if the database contains the localized data
        vo.stored_value = getattr(obj, real_field_name)

        # the database does not have our localized data.
        # check if we have a translation, first get the msgid, as a unicode string.
        vo.msgid = get_localized_property(obj, self.name, getattr(settings, 'MSGID_LANGUAGE', settings.LANGUAGE_CODE))

        # check the translation in the current language
        # but avoid empty string and None 
        if valid_for_gettext(vo.msgid):
            vo.msg = self.to_python(translation.ugettext(force_unicode(vo.msgid)))
        elif valid_for_gettext(vo.stored_value):
            # we can not use the msgid for gettext but we did find a valid
            # translation in the database. Fine we stop here and return that
            # value. No need for a standin, because we don't have a catalog value.
            return vo.stored_value
        else:
            # we can not use the msgid for gettext lookups, so there is no
            # point in trying. Check for fallback languages in database.
            vo.fallback = get_localized_property(obj, self.name)
            
            if not valid_for_gettext(vo.fallback):
                # Also if we are sure we don't have any old
                # translations in the catalog or something for the fallback
                # languages in the database, we do not need to return a standin either
                return vo.msgid
        
        # we got here so we've got a valid messageid. Now collect data from the catalog(s)
        
        # if there isn't anything new in the catalog belonging to the current language:
        if vo.msg == vo.msgid:
            # maybe we have a translation in any of the fallback languages.
            if hasattr(settings, 'FALLBACK_LANGUAGES'):
                # first check if the database has the localized data in
                # any of the fallback languages.
                vo.fallback = get_localized_property(obj, self.name)
                
                # if the fallback is the same as the msgid, go and look in the catalog
                if vo.fallback == vo.msgid:
                    # there might be a translation in any
                    # of the fallback languages.
                    for fallback in get_fallback_languages():
                        catalog = translation_catalogs(fallback)
                        msg = catalog.ugettext(force_unicode(vo.msgid))
                        if self.to_python(msg) != vo.msgid:
                            vo.fallback = self.to_python(msg)
                            break
                elif vo.fallback:
                    # if a valid fallback is found, then, since the msg is equal
                    # to the msgid, the fallback is the winner.
                    vo.msg = vo.fallback

        # if we came here we collected data from the catalog and we should return
        # a standin. A standin is the return value, with some extra properties.
        # see GettextVO for the extra properties added.
        if valid_for_gettext(vo.stored_value):
            vo.standin_value_is_from_database = True
            # database always wins
            return standin_for(vo.stored_value, **vo.__dict__)
        elif valid_for_gettext(vo.msg):
            # runner up is the translation in the native language
            return standin_for(vo.msg, **vo.__dict__)
        elif valid_for_gettext(vo.fallback):
            # and last is the translation in a fallback language
            return standin_for(vo.fallback, **vo.__dict__)

        assert(valid_for_gettext(vo.msgid))

        # there is a very very small probability that the translation of
        # a valid msgid evaluates to empty string or None (after to_python).
        # If that happened, we got here. I choose to return None, because i like
        # to be like that
        return None

    def __set__(self, obj, value):
        """Write the localised version of the field this descriptor emulates."""
        local_property = get_localized_field_name(obj, self.name)
        setattr(obj, local_property, value)

    def get_internal_type(self):
        """Used to describe the type while serializing."""
        return "CharField"

    def value_to_string(self, obj):
        """This descriptor acts as a Field, as far as the serializer is concerned."""
        try:
            return force_unicode(self.__get__(obj))
        except TypeError:
            return str(self.__get__(obj))
