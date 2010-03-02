from django.conf.urls.defaults import *
from django.conf import settings
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
from easymode.utils.languagecode import get_language_codes_as_disjunction


admin.autodiscover()

languages = get_language_codes_as_disjunction()

urlpatterns = patterns('',
    # Example:
    # (r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    (r'^', include('foobar.urls')),
    
    # These are the url patterns for the internationalised urls.
    ('^(%(languages)s)/admin/' % locals(), include(admin.site.urls)),
    ('^(%(languages)s)/' % locals(), include('foobar.urls'))
    
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^media/(?P<path>.*)$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'show_indexes': True}),        
    )