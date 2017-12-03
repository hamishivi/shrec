import requests


# cache has format url: usage, response
cache = {}
# number of items we want to keep
cache_limit = 50

def get(url, **kwargs):
    try:
        hit, response = cache[url]
        cache[url] = (hit + 1, response)
        return response
    except KeyError:
        response = requests.get(url, **kwargs)
        cache[url] = (0, response)
        # check if hit limit
        if len(cache) > cache_limit:
            cache.pop(min(cache.keys(), key=lambda url: cache[url][0]))
        return response
