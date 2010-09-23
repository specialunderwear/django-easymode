:mod:`easymode.middleware`
==========================

Google Analytics
----------------

Easymode has middleware to support caching in combination with google analytics.
Google analytics updates a session cookie on each request. Because django's
:class:`~django.contrib.sessions.middleware.django.contrib.sessions.middleware.SessionMiddleware` places cookie in it's vary header, *you will save every single
request to the cache* if you use it.

.. autoclass:: easymode.middleware.NoVaryOnCookieSessionMiddleWare

Internationalization related middleware
---------------------------------------

When using the internationalization middlewares, you should include *easymode.urls*
in your url conf::

    (r'^', include('easymode.urls')),

This will make sure that when you have defined *get_abolute_url* on your model,
the *view on site* button will lead you to the page in the language you have currently
selected.

.. automodule:: easymode.middleware
    :members: LocaleFromUrlMiddleWare, LocaliseUrlsMiddleware, ShortLocaleFromUrlMiddleWare, ShortLocaleLocaliseUrlsMiddleware
