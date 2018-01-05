from typing import Sequence
from app import app, cache
from contextlib import suppress
from collections import namedtuple


def fetch_game_info(app_id : int):
    '''
    returns a tuple (game_name, game_id, game_description, game_image) from steam and IGDB apis.
    '''
    app_id = str(app_id)
    data = cache.get(steam_api_url(app_id)).json()
    name = extract_name(data, app_id) or fetch_unlisted_name(app_id)
    if name:
        description = fetch_description(name, data, app_id)
        image = data[app_id]['data']['header_image']
    else:
        name = 'Broken Game'
        description = "This game doesn't exists!?"
        image = "No image found :'("
    return GameInfo(name, app_id, description, image)

GameInfo = namedtuple('GameInfo', 'name, app_id, description, image')


def fetch_game_name(app_id : int):
    '''
    When we just want to get the name, and avoid unnecessary api calls.
    '''
    app_id = str(app_id)
    return extract_name(
        cache.get(steam_api_url(app_id)).json(), app_id
    ) or fetch_unlisted_name(app_id) or f'invalid steam id: {app_id}'


def fetch_description(game_name, steam_data, app_id : str):
    '''
    gets description of game from IGDB, otherwise uses steam description if
    possible.
    '''
    try:
        steam_description = steam_data[app_id]['data']['short_description']
    except:
        steam_description = ''

    IGDB_data = cache.get(IGDB_api_url(game_name), headers=IGDB_HEADERS).json()[0]
    if 'summary' in IGDB_data:
        return shorten_desc(IGDB_data['summary'])
    elif len(steam_description) > 0:
        return shorten_desc(steam_description)
    else:
        return "Sorry, we couldn't find a description for this game 😥"


def steam_api_url(app_id):
    return  f'http://store.steampowered.com/api/appdetails/?appids={app_id}&format=json'


IGDB_HEADERS = cache.HashableDict({
    'Accept' : 'application/json',
    'user-key' : app.config['IGDB_API_KEY']
})


def IGDB_api_url(game_name):
    return f'{app.config["IGDB_API_URL"]}/games/?fields=*&limit=1&search={game_name}'


def extract_name(game_data : dict, app_id : str):
    with suppress(KeyError, TypeError):
        return game_data[app_id]['data']['name']


def fetch_unlisted_name(app_id : str):
    return find_removed_name(cache.get(STEAM_TRACKER_API).json()['removed_apps'], app_id)

STEAM_TRACKER_API = 'https://steam-tracker.com/api?action=GetAppList'


def find_removed_name(removed_apps : Sequence[dict], app_id : str):
    '''
    searches a list of all unlisted games which were on steam for the given game
    I couldn't find an api that allowed search by id.
    '''
    for game_data in removed_apps:
        if game_data['appid'] == app_id:
            return app['name']


def shorten_desc(description : str):
    '''
    A helper method to chop strings more than 200 characters long.
    It tries to find the closest sentence end and then just cut there.
    '''
    try:
        if len(description) > 200:
            cutoff = description.index('. ', 190)
            description = description[:cutoff] + '...'
    finally:
        return description