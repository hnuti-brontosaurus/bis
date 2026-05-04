from django.core.cache import cache
from django.views.decorators.cache import cache_page


def _version_key(namespace):
    return f"cache_version:{namespace}"


def invalidate_cache(namespace):
    try:
        cache.incr(_version_key(namespace))
    except ValueError:
        cache.set(_version_key(namespace), 1)


class CachedViewSetMixin:
    cache_namespace = ""
    cache_timeout = 60 * 60

    def dispatch(self, request, *args, **kwargs):
        version = cache.get(_version_key(self.cache_namespace)) or 0
        key_prefix = f"{self.cache_namespace}:v{version}"
        return cache_page(self.cache_timeout, key_prefix=key_prefix)(super().dispatch)(
            request, *args, **kwargs
        )
