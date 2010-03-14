from django.conf.urls.defaults import *
import foobar.views

urlpatterns = patterns('',
    url(r'^$', foobar.views.index, name='index'),
    url(r'^raw\.xml$', foobar.views.raw, name='raw'),
    url(r'^chain\.xml$', foobar.views.chain, name='chain'),
    url(r'^xslt\.xml$', foobar.views.xslt, name='xslt'),
    url(r'^frontend/$', foobar.views.frontend, {'format':'html',}, name='frontend_html'),
    url(r'^frontend/data\.(?P<format>(xml))', foobar.views.frontend, name='frontend'),
)
