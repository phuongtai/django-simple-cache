"""
The revolution middleware has a different from django's CacheMiddle.
That's cache single, just one record in database

"""
from django.conf import settings
from django.core.cache import DEFAULT_CACHE_ALIAS, caches

from .utils import learn_cache_key, get_cache_key


class BaseCachedMiddleware:
    def __init__(self, cache_timeout=None,
            cache_alias=None,
            key_prefix=None,
            get_response=None):
        self.cache_timeout = cache_timeout or settings.CACHE_MIDDLEWARE_SECONDS
        self.key_prefix = key_prefix or settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.cache_alias = cache_alias or settings.CACHE_MIDDLEWARE_ALIAS
        self.cache = caches[self.cache_alias]
        self.get_response = get_response


class UpdateSingleCacheMiddleware(BaseCachedMiddleware):
    def __init__(self, cache_timeout=None,
            cache_alias=None,
            key_prefix=None,
            get_response=None):
        super().__init__(
            cache_timeout=cache_timeout,
            cache_alias=cache_alias,
            key_prefix=key_prefix,
            get_response=get_response
        )

    def process_response(self, request, response):
        """Set the cache, if needed."""
        timeout = None  # Never expire
        if response.status_code in [200, 201]:
            cache_key = learn_cache_key(request, response, timeout, self.key_prefix, cache=self.cache)
            if hasattr(response, 'render') and callable(response.render):
                response.add_post_render_callback(
                    lambda r: self.cache.set(cache_key, r)
                )
            else:
                self.cache.set(cache_key, response)

        if request.method == 'DELETE':
            cache_key = learn_cache_key(request, response, timeout, self.key_prefix, cache=self.cache)
            self.cache.delete(cache_key)

        return response


class FetchFromCacheMiddleware(BaseCachedMiddleware):
    def __init__(self, cache_timeout=None,
            cache_alias=None,
            key_prefix=None,
            get_response=None):
        super().__init__(
            cache_timeout=cache_timeout,
            cache_alias=cache_alias,
            key_prefix=key_prefix,
            get_response=get_response
        )

    def process_request(self, request):
        """
        Check whether the page is already cached and return the cached
        version if available.
        """

        cache_key = get_cache_key(request, self.key_prefix, cache=self.cache)
        if cache_key is None:
            return None
        response = self.cache.get(cache_key)
        if response is None:
            return None
        return response


class CacheMiddleware(UpdateSingleCacheMiddleware, FetchFromCacheMiddleware):
    """
    Cache middleware that provides basic behavior for many simple sites.

    Also used as the hook point for the cache decorator, which is generated
    using the decorator-from-middleware utility.
    """
    def __init__(self, get_response=None, cache_timeout=None, **kwargs):
        self.get_response = get_response
        # We need to differentiate between "provided, but using default value",
        # and "not provided". If the value is provided using a default, then
        # we fall back to system defaults. If it is not provided at all,
        # we need to use middleware defaults.

        try:
            key_prefix = kwargs['key_prefix']
            if key_prefix is None:
                key_prefix = ''
        except KeyError:
            key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
        self.key_prefix = key_prefix

        try:
            cache_alias = kwargs['cache_alias']
            if cache_alias is None:
                cache_alias = DEFAULT_CACHE_ALIAS
        except KeyError:
            cache_alias = settings.CACHE_MIDDLEWARE_ALIAS
        self.cache_alias = cache_alias

        if cache_timeout is None:
            cache_timeout = settings.CACHE_MIDDLEWARE_SECONDS
        self.cache_timeout = cache_timeout
        self.cache = caches[self.cache_alias]
