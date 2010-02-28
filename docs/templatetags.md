Easyfilters
===========

Easymode comes with 3 templatetags that can be used to modify
existing templates so they can be used in a multilingual 
environment.

:func:`~easymode.templatetags.easyfilters.strip_locale`
-------------------------------------------------------

:func:`~easymode.templatetags.easyfilters.strip_locale` will
have an url as an argument and if there is a locale in the url,
it will be stripped::

    {% load 'easyfilters' %}
    
    {{ 'http://example.com/en/greetings'|strip_locale }}

this will render as: ``http://example.com/greetings`` so the 'en'
part will be removed from the url.

You can use this filter in combination with
:class:`~easymode.middleware.LocaliseUrlsMiddleware`. The middleware
will add the current language to any urls that do not have the
language code in the url yet.

:func:`~easymode.templatetags.easyfilters.fix_locale_from_request`
------------------------------------------------------------------

Fixes the language code as follows:

If there is only one language used in the site, it strips the language code.
If there are more languages used, it will make sure that the url has the current
language as a prefix.

usage::

    {% load 'easyfilters' %}
    
    {{ 'http://example.com/en/greetings'|fix_locale_from_request:request.LANGUAGE_CODE }}

Suppose ``request.LANGUAGE_CODE`` was 'ru' then the output would become::

    http://example.com/ru/greetings

Suppose ``settings.LANGUAGES`` contained only one language, the output
would become::

    http://example.com/greetings

You probably do not need this templatetag if you are using
:class:`~easymode.middleware.LocaliseUrlsMiddleware`.

:func:`~easymode.templatetags.easyfilters.fix_shorthand`
--------------------------------------------------------

Use this if you want to use :ref:`short_language_codes`.

:func:`~easymode.templatetags.easyfilters.fix_shorthand` 
will always return the correct locale to use in an url,
depending on your settings of :ref:`short_language_codes`.

usage::

    {% load 'easyfilters' %}
    
    {{ request.lANGUAGE_CODE|fix_shorthand }}

Suppose ``request.LANGUAGE_CODE`` is 'fr-be' and 
:ref:`short_language_codes` is set to ``True``,
the output would become::

    fr

If :ref:`short_language_codes` is set to ``False``
the output would be::

    fr-be

If ``request.LANGUAGE_CODE`` is not a five letter language code, nothing
happens.