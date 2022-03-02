from django.utils.encoding import smart_text


class CacheKey(object):
    """
    A stub string class that we can use to check if a key was created already.
    """
    def __init__(self, key, versioned_key):
        self._original_key = key
        self._versioned_key = versioned_key

    def __eq__(self, other):
        return self._versioned_key == other

    def __unicode__(self):
        return smart_text(self._versioned_key)

    def __hash__(self):
        return hash(self._versioned_key)

    __repr__ = __str__ = __unicode__
