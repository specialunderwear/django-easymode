"""
When ``get_absolute_url`` is defined on a model, django will place a
*view on site* link in the ``change_view`` of the model. 

If you are using easymode's multilanguage features and especially 
:class:`~easymode.middleware.LocaleFromUrlMiddleWare` and
:class:`~easymode.middleware.LocaliseUrlsMiddleware` you will find that the
*view on site* link will not point to the correct (current) language.

The routes specified here will override the default admin routes and
make the *view on site* link take the current language into account.

include the urls in your urlconf like this::

    (r'^', include('easymode.urls')),

"""
from django.conf.urls.defaults import *

from easymode.utils.languagecode import get_language_codes_as_disjunction

languages = get_language_codes_as_disjunction()

urlpatterns = patterns('easymode.views',
    (r'^admin/r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$', 'preview'),
    (r'^(%(languages)s)/admin/r/(?P<content_type_id>\d+)/(?P<object_id>.+)/$' % locals(), 'preview'),
)
