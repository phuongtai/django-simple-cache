from django.utils.decorators import decorator_from_middleware_with_args
from .middleware import CacheMiddleware, UpdateSingleCacheMiddleware, FetchFromCacheMiddleware


def cache_api(timeout=None, cache=None, key_prefix=None):

    return decorator_from_middleware_with_args(CacheMiddleware)(
        cache_timeout=timeout, cache_alias=cache, key_prefix=key_prefix
    )


def cache_update(key_prefix, timeout=None, cache=None):
    '''
    Decorator use for some actions: POST, PUT, PATCH, DELETE
    @params:
        - `timeout`: time to live
        - `cache`: Backend class of cache which define at settings.CACHES['default']
        - `key_prefix`: in this instance `key_prelix` is model's name.
    @result:
        POST: Set a new key, value to cache.
        PUT, PATCH: Set with existed key with new value to cache.
        DELETE: Clear key and value.
    '''

    return decorator_from_middleware_with_args(UpdateSingleCacheMiddleware)(
        key_prefix=key_prefix, cache_timeout=timeout, cache_alias=cache
    )


def cache_fetch(key_prefix, timeout=None, cache=None):
    '''
    Decorator use for some actions: GET with single record.
    @params:
        - `key_prefix`: in this instance `key_prelix` is model's name.
        - `timeout`: time to live
        - `cache`: Backend class of cache which define at settings.CACHES['default']
    @result:
        If cache is existed: return response.
        Else: Fetch from database.
    '''
    return decorator_from_middleware_with_args(FetchFromCacheMiddleware)(
        cache_timeout=timeout, cache_alias=cache, key_prefix=key_prefix
    )
