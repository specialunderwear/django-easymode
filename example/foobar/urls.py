from django.conf.urls.defaults import *
import foobar.views

urlpatterns = patterns('',
    (r'^$', foobar.views.index),
    (r'^chain$', foobar.views.chain),
    (r'^xslt$', foobar.views.xslt),
)
