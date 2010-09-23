"""
These urls will be used when previewing a draft.
An extra query parameter will be passed to the view:

?preview=revision_id

Also the shortcut is not named 'r' but 'p' for preview.

include these urls in your urlconf like this::

    (r'^', include('easymode.easypublisher.urls')),

"""
from django.conf.urls.defaults import *

from easymode.utils.languagecode import get_language_codes_as_disjunction

languages = get_language_codes_as_disjunction()

urlpatterns = patterns('easymode.easypublisher.views',
    url(r'^admin/p/(?P<content_type_id>\d+)/(?P<object_id>.+)/(?P<revision_id>.+)/$', 'preview_draft', name='preview_draft'),
    (r'^(%(languages)s)/admin/p/(?P<content_type_id>\d+)/(?P<object_id>.+)/(?P<revision_id>.+)/$' % locals(), 'preview_draft'),
)
