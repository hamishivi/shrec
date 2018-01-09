import csv
from urllib.parse import urljoin
from functools import partial, lru_cache
from app import app, cache


@lru_cache(maxsize=128) # pevents repeated saves - should be replaced by db system
def save_owned_games(steam_id):
    '''
    Create a csv file called training_data with the format: (steamid,gameid,play_time)
    '''
    owned_games = fetch_owned_games(steam_id)
    with open('training_data','a') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for game in owned_games:
            if game['playtime_forever'] > 0:
                writer.writerow([steam_id, game['appid'], game['playtime_forever']])


def filter_unplayed(game_data):
    return [game['appid'] for game in game_data if game['playtime_forever'] == 0]


@lru_cache(maxsize=128) # prevents crawling repeatedly
def fetch_friend_network(steam_id, maxdepth=5, stop=50):
    '''
    Constuct a recursive set of connections up to a certain depth and size
    '''
    visited = {}
    stack = [(steam_id, 0)]
    while stack and len(visited) < stop:
        steam_id, depth = stack.pop()
        if depth > maxdepth or steam_id in visited:
            continue
        visited.add(steam_id)
        for friend in fetch_friends(steam_id):
            stack.append((friend['steamid'], depth + 1))
    return visited


def fetch_owned_games(steam_id):
    '''
    returns json of user games
    '''
    try:
        return cache.get(owned_games_url(steamid=steam_id)).json()['response']['games']
    except KeyError:
        # invalidate cache so we make new request when user retry
        cache.get.cache_clear()
        raise PrivateAccount(steam_id)

def fetch_friends(steam_id):
    '''
    Get a list of friends for a steam user
    '''
    try:
        return cache.get(friend_list_url(steamid=steam_id)).json()['friendslist']['friends']
    except KeyError:
        return []


def construct_steam_url(endpoint, apikey=app.config['STEAM_API_KEY'], **params):
    '''
    Return a formatted endpoint URL from the Steam API
    '''
    params["key"] = apikey
    return urljoin(
        urljoin("http://api.steampowered.com/", endpoint),
        "?" + "&".join([f"{k}={params[k]}" for k in params])
    )


# usage: owned_games_url(steamid=0000000)
owned_games_url = partial(
        construct_steam_url,
        endpoint='IPlayerService/GetOwnedGames/v0001',
        apikey=app.config['STEAM_API_KEY'],
        format='json'
)


# usage: friend_list_url(steamid=0000000)
friend_list_url = partial(
        construct_steam_url,
        endpoint='ISteamUser/GetFriendList/v0001',
        apikey=app.config['STEAM_API_KEY'],
        relationsip='friend'
)

class PrivateAccount(Exception): pass
