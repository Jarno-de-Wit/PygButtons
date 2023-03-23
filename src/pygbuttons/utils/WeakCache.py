from weakref import WeakValueDictionary
from functools import wraps

def weak_cache(func):
    cache = WeakValueDictionary()
    sentinel = object()
    def wrapper(*args):
        key = args
        result = cache.get(key, sentinel)
        if result is not sentinel:
            return result
        result = func(*args)
        cache[key] = result
        return result
    return wrapper
