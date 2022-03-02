import hashlib
import logging
try:
    import importlib
except ImportError:
    from django.utils import importlib

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.encoding import force_bytes

from rest_framework.request import Request
from rest_framework.response import Response


log = logging.getLogger('cache')


def import_class(path):
    module_name, class_name = path.rsplit('.', 1)
    try:
        module = importlib.import_module(module_name)
    except ImportError:
        raise ImproperlyConfigured('Could not find module "%s"' % module_name)
    else:
        try:
            return getattr(module, class_name)
        except AttributeError:
            raise ImproperlyConfigured('Cannot import "%s"' % class_name)


def find(key, data):
    for k, v in data.items():
        if k == key:
            yield v
        if isinstance(v, dict):
            for result in find(key, v):
                yield result
        elif isinstance(v, list):
            for d in v:
                for result in find(key, d):
                    yield result


def _generate_cache_key(request, key_prefix, extra=str):
    """Return a cache key from the headers given in the header list."""
    ctx = hashlib.md5()
    ctx.update(force_bytes(extra))
    cache_key = 'cache_one.{}.{}'.format(key_prefix, ctx.hexdigest())
    return cache_key


def _generate_cache_header_key(key_prefix, request):
    """Return a cache key for the header cache."""
    # url = hashlib.md5(force_bytes(iri_to_uri(request.build_absolute_uri())))
    cache_key = 'cache.cache_header.%s.' % (
        key_prefix)
    return cache_key


def get_cache_key(request, key_prefix=None, cache=None):
    indentify_value = ''
    if request.method == 'GET' and isinstance(request, Request):
        parser_context = request.parser_context
        kwargs = parser_context.get('kwargs')
        for key, val in kwargs.items():
            indentify_value = '{}.{}'.format(key, val)
    if key_prefix is None:
        key_prefix = settings.CACHE_MIDDLEWARE_KEY_PREFIX
    return _generate_cache_key(request, key_prefix, extra=indentify_value)


def learn_cache_key(request, response, cache_timeout=None, key_prefix=None, cache=None):
    '''
    `learn_cache_key` help you define the cache key with key_prefix and indentify object (id, uid)
    '''
    try:
        indentify_value = ''
        method_update = ['GET', 'PUT', 'PATCH', 'DELETE']
        if request.method in method_update and isinstance(request, Request):
            parser_context = request.parser_context
            kwargs = parser_context.get('kwargs')
            for key, val in kwargs.items():
                indentify_value = '{}.{}'.format(key, val)
        if request.method == 'POST' and isinstance(response, Response):
            # receive data a instance of rest_framework.response.Response.
            content = response.data
            # Get lookup_field ===== begin
            renderer_context = getattr(response, 'renderer_context', None)
            assert renderer_context is not None, ".renderer_context not set on Response"
            view = renderer_context.get('view')
            assert view is not None, ".view not set in renderer_context"
            lookup_field = getattr(view, 'lookup_field')
            assert lookup_field is not None, ".lookup_field not set on {}".format(view.__class__.__name__)
            # Get lookup_field  ===== end
            # Find indentify data in content of the response
            value = next(find(lookup_field, content))
            indentify_value = '{}.{}'.format(lookup_field, value)

    except Exception as e:
        log.error(str(e))
        pass

    return _generate_cache_key(request, key_prefix, extra=indentify_value)
