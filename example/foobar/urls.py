from django.conf.urls.defaults import *
import foobar.views

urlpatterns = patterns('',
    (r'^$', foobar.views.index),
    (r'^xslt$', foobar.views.xslt),
)
