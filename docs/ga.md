Google Analytics
================

Easymode has middleware to support of caching in combination with google analytics.
Google analytics updates a session cookie on each request. Because django's
``SessionMiddleWare`` places cookie in it's vary header, *you will save every single
request to the cache* if you use it.

NoVaryOnCookieSessionMiddleWare
-------------------------------

Easymode comes with ``easymode.middleware.NoVaryOnCookieSessionMiddleWare`` which
solves this problem.
