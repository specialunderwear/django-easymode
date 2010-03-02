from django.conf.urls.defaults import *
import foobar.views

urlpatterns = patterns('',
    (r'^$', foobar.views.index),
    (r'^raw$', foobar.views.raw),
    (r'^chain$', foobar.views.chain),
    (r'^xslt$', foobar.views.xslt),
)
