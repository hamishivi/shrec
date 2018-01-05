import requests
import functools

get = functools.lru_cache(maxsize=128)(requests.get)

class HashableDict(dict):
    def __setitem__(self, key, value):
        raise TypeError('Hashable means Immutable')

    def __hash__(self):
        return hash(frozenset(self.items()))