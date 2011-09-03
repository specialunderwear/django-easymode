from django.conf import settings
from django.http import HttpResponse
from django.test import TestCase
from django.utils.decorators import decorator_from_middleware

from easymode import middleware
from easymode.tests.testcases import initdb
from easymode.utils import languagecode


__all__ = ('TestLocaliseUrlsMiddleware', 'TestLocaleFromUrlMiddleWare')

@decorator_from_middleware(middleware.LocaliseUrlsMiddleware)
def localise_urls_middleware_view(request):
    return HttpResponse("""
    <a href="/example/modifyme.html">hhh</a>
    <a href="/en/example/staysthesame.html">hhh</a>
    <a href="/xx/notareallangugaecode.html"/>
    <a href="/de/reallanguagecode.html"/>
    """)

@initdb
class TestLocaliseUrlsMiddleware(TestCase):
    """Test the middlewares that come with easymode"""

    def tearDown(self):
        self.settingsManager.revert()
        reload(languagecode)
        
    def test_localise_urls_middleware(self):
        "The LocaliseUrlsMiddleware should insert the languagecode as a slug in all anchor tags"
                
        result = localise_urls_middleware_view(type('RequestMock', tuple(), {'path':'koek', 'LANGUAGE_CODE':'en'}))
                
        self.assertContains(result,'href="/en/example/modifyme.html')
        self.assertContains(result, 'href="/en/example/staysthesame.html')
        self.assertContains(result, 'href="/en/xx/notareallangugaecode.html')
        self.assertContains(result, 'href="/de/reallanguagecode.html"')
        
        result = localise_urls_middleware_view(type('RequestMock', tuple(), {'path':'koek', 'LANGUAGE_CODE':'xx'}))
        
        self.assertContains(result,'href="/xx/example/modifyme.html')
        self.assertContains(result, 'href="/en/example/staysthesame.html')
        self.assertContains(result, 'href="/xx/xx/notareallangugaecode.html')
        self.assertContains(result, 'href="/de/reallanguagecode.html"')


    def test_localise_urls_middleware_use_short_language_codes(self):
        """
        The LocaliseUrlsMiddleware should insert a short version of the
        languagecode as a slug in all anchor tags that do not yet have a
        langugage
        """
        
        self.settingsManager.set(USE_SHORT_LANGUAGE_CODES=True)
        reload(languagecode)

        result = localise_urls_middleware_view(type('RequestMock', tuple(), {'path':'koek', 'LANGUAGE_CODE':'en-us'}))
            
        self.assertContains(result,'href="/en/example/modifyme.html')
        self.assertContains(result, 'href="/en/example/staysthesame.html')
        self.assertContains(result, 'href="/en/xx/notareallangugaecode.html')
        self.assertContains(result, 'href="/de/reallanguagecode.html"')


@decorator_from_middleware(middleware.LocaleFromUrlMiddleWare)
def locale_from_url_middle_ware_view(request):
    return HttpResponse(request.LANGUAGE_CODE)

@initdb
class TestLocaleFromUrlMiddleWare(TestCase):
    "Test the LocaleFromUrlMiddleWare"
    
    def setUp(self):
        self.RequestMockShort = type('RequestMockShort', tuple(), {'path_info':'/en/hi.html', 'set_cookie':lambda x, y, z: x})
        self.RequestMockLong = type('RequestMockLong', tuple(), {'path_info':'/en-us/hi.html', 'set_cookie':lambda x, y, z: x})
    
    def tearDown(self):
        self.settingsManager.revert()
        reload(languagecode)
        reload(middleware)
        
    def test_locale_from_url_middle_ware_normal(self):
        """When USE_SHORT_LANGUAGE_CODES=False languages in urls should be
        resolved as themselves"""
        
        self.settingsManager.set(USE_SHORT_LANGUAGE_CODES=False)
        reload(languagecode)
        reload(middleware)

        result = locale_from_url_middle_ware_view(self.RequestMockShort())
        self.assertEqual(result.content, 'en')
        
        result =  locale_from_url_middle_ware_view(self.RequestMockLong())
        self.assertEqual(result.content, 'en-us')
        
        
    def test_locale_from_url_middle_ware_short(self):
        """When USE_SHORT_LANGUAGE_CODES=True languages in urls should be
        treated as shorthands for longer language codes."""
        
        self.settingsManager.set(USE_SHORT_LANGUAGE_CODES=True,
            LANGUAGE_CODE='de',
            LANGUAGES=(
                ('de', 'German'),
                ('en-us', 'usa'),
            )
        )
        reload(languagecode)
        reload(middleware)
        
        # if the url is prefixed with a known shorthand
        # the language is returned
        result = locale_from_url_middle_ware_view(self.RequestMockShort())
        self.assertEqual(result.content, 'en-us')

        # if the url is not prefixed with a known shorthand
        # the LANGUAGE_CODE is returned.
        result = locale_from_url_middle_ware_view(self.RequestMockLong())
        self.assertEqual(result.content, settings.LANGUAGE_CODE)

