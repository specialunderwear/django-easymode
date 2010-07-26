"""
Replacements for django middlewares that allow you to see what is put in to the cache
and comes out of the cache.
"""
import logging

from django.conf import settings
from django.core.cache import cache
from django.utils.cache import get_cache_key, learn_cache_key, patch_response_headers, get_max_age, _generate_cache_header_key

def get_cache_key_parameters(request):
    result = []
    key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
    result.append("key_prefix: %s" % key_prefix)
    cache_key = _generate_cache_header_key(key_prefix, request)
    headerlist = cache.get(cache_key, None)
    if headerlist:
        for header in headerlist:
            value = request.META.get(header, None)
            if value is not None:
                result.append("%s = %s" % (header, value))
    return result
    
class DebugUpdateCacheMiddleware(object):
    """
    Same as :class:`~django.middleware.cache.django.middleware.cache.UpdateCacheMiddleware` but is shows you
    when something is put into the cache.
    """
    def __init__(self):
        self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)

    def process_response(self, request, response):
        """Sets the cache, if needed."""
        if not hasattr(request, '_cache_update_cache') or not request._cache_update_cache:
            # We don't need to update the cache, just return.
            return response
        if request.method != 'GET':
            # This is a stronger requirement than above. It is needed
            # because of interactions between this middleware and the
            # HTTPMiddleware, which throws the body of a HEAD-request
            # away before this middleware gets a chance to cache it.
            return response
        if not response.status_code == 200:
            return response
        # Try to get the timeout from the "max-age" section of the "Cache-
        # Control" header before reverting to using the default cache_timeout
        # length.
        timeout = get_max_age(response)
        if timeout == None:
            timeout = self.cache_timeout
        elif timeout == 0:
            # max-age was set to 0, don't bother caching.
            return response
        patch_response_headers(response, timeout)
        if timeout:
            cache_key = learn_cache_key(request, response, timeout, self.key_prefix)
            cache.set(cache_key, response, timeout)
            logging.debug("UpdateCacheMiddleware: setting %s -> %s params are: %s" % (cache_key, request.path, get_cache_key_parameters(request)))
        return response

class DebugFetchFromCacheMiddleware(object):
    """
    Same as :class:`~django.middleware.cache.django.middleware.cache.FetchFromCacheMiddleware` but it shows
    you what it is retrieving from the cache if it can find something.
    """
    def __init__(self):
        self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)

    def process_request(self, request):
        """
        Checks whether the page is already cached and returns the cached
        version if available.
        """
        if self.cache_anonymous_only:
            assert hasattr(request, 'user'), "The Django cache middleware with CACHE_MIDDLEWARE_ANONYMOUS_ONLY=True requires authentication middleware to be installed. Edit your MIDDLEWARE_CLASSES setting to insert 'django.contrib.auth.middleware.AuthenticationMiddleware' before the CacheMiddleware."

        if not request.method in ('GET', 'HEAD') or request.GET:
            request._cache_update_cache = False
            return None # Don't bother checking the cache.

        if self.cache_anonymous_only and request.user.is_authenticated():
            request._cache_update_cache = False
            return None # Don't cache requests from authenticated users.

        cache_key = get_cache_key(request, self.key_prefix)
        if cache_key is None:
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.

        response = cache.get(cache_key, None)
        if response is None:
            logging.debug("FetchFromCacheMiddleware: %s is %s.  paramters(%s)" % ( cache_key, request.path, get_cache_key_parameters(request)))
            request._cache_update_cache = True
            return None # No cache information available, need to rebuild.
        logging.debug("Found %s -> %s in the cache. parameters(%s)" % (cache_key, request.path, get_cache_key_parameters(request)))
        request._cache_update_cache = False
        return response

class DebugCacheMiddleware(DebugUpdateCacheMiddleware, DebugFetchFromCacheMiddleware):
    """
    combines :class:`~easymode.debug.middleware.DebugFetchFromCacheMiddleware` and 
    :class:`easymode.debug.middleware.DebugUpdateCacheMiddleware`
    """
    def __init__(self, cache_timeout=None, key_prefix=None, cache_anonymous_only=None):
        self.cache_timeout = cache_timeout
        if cache_timeout is None:
            self.cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = key_prefix
        if key_prefix is None:
            self.key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        if cache_anonymous_only is None:
            self.cache_anonymous_only = getattr(settings, 'CACHE_MIDDLEWARE_ANONYMOUS_ONLY', False)
        else:
            self.cache_anonymous_only = cache_anonymous_only
