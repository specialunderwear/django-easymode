import re
import time

from django.conf import settings
from django.utils import translation
from django.utils.http import cookie_date
from django.contrib.sessions.middleware import SessionMiddleware
from django.middleware.locale import LocaleMiddleware
from easymode.utils.languagecode import get_short_language_codes, get_language_code_from_shorthand, get_shorthand_from_language_code

USE_SHORT_LANGUAGE_CODES = getattr(settings, 'USE_SHORT_LANGUAGE_CODES', False)

################################################################################
# Compiled regular expressions
################################################################################

MATCH_LANGUAGE_CODE = re.compile(r"^/(%s)/.*" % "|".join(map(lambda l: l[0], settings.LANGUAGES)))
MATCH_SHORT_LANGUAGE_CODE = re.compile(r"^/(%s)/.*" % "|".join(get_short_language_codes()))

if USE_SHORT_LANGUAGE_CODES:
    HREF_REGEX = re.compile(ur'<a([^>]+)href="/(?!(%s|%s|%s))([^"]*)"([^>]*)>' % (
        "|".join(map(lambda l: l + "/" , get_short_language_codes())), 
        settings.MEDIA_URL[1:], 
        settings.ADMIN_MEDIA_PREFIX[1:]
    ))
    FORM_REGEX = re.compile(ur'<form([^>]+)action="/(?!(%s|%s|%s))([^"]*)"([^>]*)>' % (
        "|".join(map(lambda l: l + "/" , get_short_language_codes())),
         settings.MEDIA_URL[1:],
         settings.ADMIN_MEDIA_PREFIX[1:]
    ))
else:
    HREF_REGEX = re.compile(ur'<a([^>]+)href="/(?!(%s|%s|%s))([^"]*)"([^>]*)>' % (
        "|".join(map(lambda l: l[0] + "/" , settings.LANGUAGES)), 
        settings.MEDIA_URL[1:], 
        settings.ADMIN_MEDIA_PREFIX[1:]
    ))
    FORM_REGEX = re.compile(ur'<form([^>]+)action="/(?!(%s|%s|%s))([^"]*)"([^>]*)>' % (
        "|".join(map(lambda l: l[0] + "/" , settings.LANGUAGES)),
         settings.MEDIA_URL[1:],
         settings.ADMIN_MEDIA_PREFIX[1:]
    ))

################################################################################
# helper functions
################################################################################

def has_lang_prefix(path):
    if USE_SHORT_LANGUAGE_CODES:
        check = MATCH_SHORT_LANGUAGE_CODE.match(path)
        
        if check is not None:
            return get_language_code_from_shorthand(check.group(1))
    else:
        check = MATCH_LANGUAGE_CODE.match(path)
        if check is not None:
            return check.group(1)
        
        return False

################################################################################
# middlewares
################################################################################

class NoVaryOnCookieSessionMiddleWare(SessionMiddleware):
    """
    Works like django's :class:`django.middleware.SessionMiddleWare`, but it does not
    add cookie to the vary header. You need this if you use google
    analytics and want to use django site caching.
    """

    def process_response(self, request, response):
        """
        If ``request.session was modified``, or if the configuration is to save the
        session every time, save the changes and set a session cookie.
        """
        try:
            modified = request.session.modified
        except AttributeError:
            pass
        else:
            if modified or settings.SESSION_SAVE_EVERY_REQUEST:
                if request.session.get_expire_at_browser_close():
                    max_age = None
                    expires = None
                else:
                    max_age = request.session.get_expiry_age()
                    expires_time = time.time() + max_age
                    expires = cookie_date(expires_time)
                # Save the session data and refresh the client cookie.
                request.session.save()
                response.set_cookie(settings.SESSION_COOKIE_NAME,
                        request.session.session_key, max_age=max_age,
                        expires=expires, domain=settings.SESSION_COOKIE_DOMAIN,
                        path=settings.SESSION_COOKIE_PATH,
                        secure=settings.SESSION_COOKIE_SECURE or None)
        return response

class LocaleFromUrlMiddleWare(LocaleMiddleware):
    """
    Like :class:`django.middleware.LocaleMiddleware` this middleware activates the current language.
    It does not try to guess the language from the request headers, it looks
    for it in the url, or it defaults to ``settings.LANGUAGE_CODE``.
    
    Also we don't use the accept language to determine the language of the page anymore,
    so the Accept-Language is nolonger considered for the vary headers.
    """
    def process_request(self, request):
        language = has_lang_prefix(request.path_info)
        
        if not language:
            language = settings.LANGUAGE_CODE
        
        if hasattr(request, "session"):
            request.session["django_language"] = language
        else:
            request.set_cookie("django_language", language)
        
        translation.activate(language)
        request.LANGUAGE_CODE = translation.get_language()
    
    def process_response(self, request, response):
        if 'Content-Language' not in response:
            response['Content-Language'] = translation.get_language()
        translation.deactivate()
        return response
    

class LocaliseUrlsMiddleware(object):
    """
    This middleware replaces all anchor tags with localised versions, ugly
    but it works.
    
    Don't put any vary header for the Accept-Language because the language does
    not depend on the vary header, the language is in the url.
    """
    
    def process_response(self, request, response):
        translation.deactivate()
        path = unicode(request.path)

        if not path.startswith(settings.MEDIA_URL) and \
                not path.startswith(settings.ADMIN_MEDIA_PREFIX) and \
                response.status_code == 200 and \
                response._headers['content-type'][1].split(';')[0] == "text/html":
                
            response.content = HREF_REGEX.sub(
                ur'<a\1href="/%s/\3"\4>' % get_shorthand_from_language_code(request.LANGUAGE_CODE), 
                response.content.decode('utf-8'))
            response.content = FORM_REGEX.sub(
                ur'<form\1action="/%s/\3"\4>' % get_shorthand_from_language_code(request.LANGUAGE_CODE), 
                response.content.decode('utf-8'))
                
        if (response.status_code == 301 or response.status_code == 302 ):
            location = response._headers['location']
            prefix = has_lang_prefix(location[1])
            if not prefix and location[1].startswith("/") and \
                    not location[1].startswith(settings.MEDIA_URL) and \
                    not location[1].startswith(settings.ADMIN_MEDIA_PREFIX):
                response._headers['location'] = (location[0], "/%s%s" % (get_shorthand_from_language_code(request.LANGUAGE_CODE), location[1]))
        return response

################################################################################
# Shorthand versions of locale middlewares.
# These versions only add the language part of the langugae code and omit the 
# country
################################################################################

class ShortLocaleFromUrlMiddleWare(LocaleFromUrlMiddleWare):
    """
    Same as :class:`LocaliseUrlsMiddleware` but it uses the shorthand version of the language code.
    
    This means that if the language code is en-gb, only 'en' will be added to the urls.    
    """
    def process_request(self, request):
        super(ShortLocaleFromUrlMiddleWare, self).process_request(request)

class ShortLocaleLocaliseUrlsMiddleware(LocaliseUrlsMiddleware):
    """
    Same as :class:`LocaliseUrlsMiddleware`, however it uses the shorthand version of the language code.
    
    This means that if the language code is en-gb, only 'en' will be added to the urls.
    """
    def process_response(self, request, response):
        return super(ShortLocaleLocaliseUrlsMiddleware, self).process_response(request, response)
