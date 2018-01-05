import requests
import functools

get = functools.lru_cache(maxsize=128)(requests.get)
