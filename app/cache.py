import requests


# cache has format url: usage, response
cache = {}
# number of items we want to keep
cache_limit = 50

def get(url, **kwargs):
    if url in cache:
        return cache[url][1]
    else:
        response = requests.get(url, **kwargs)
        cache[url] = (0, response)
        # check if hit limit
        if len(cache) > cache_limit:
            # remove least used item from cache
            pop_url = list(cache.keys())[0]
            least_used = cache[pop_url][0]
            for url in cache:
                if cache[url][0] < least_used:
                    least_used = cache[url][0]
                    pop_url = url
            cache.pop(url)
        return response
