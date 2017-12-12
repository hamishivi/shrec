import csv
from app import app, cache

def get_game_info(app_id):
    '''
    returns a tuple (game_name, game_id, game_description, game_image) from steam and IGDB apis.
    '''
    # Make Api call
    g_api = f'http://store.steampowered.com/api/appdetails/?appids={app_id}&format=json'
    game_data = cache.get(g_api).json()
    # Check we actually got game data
    if not game_data or 'data' not in game_data[str(app_id)]:
        # not data from steam, look it up on steam-tracker
        game_name = get_unlisted_name(app_id)
        game_image = "Sorry, no image found"
        # no help here, just gotta report it... :'(
        if game_name is None:
            return ("Broken Game", app_id, "This game doesn't exist!?", "No image found :'(")
    else:
        game_name = game_data[str(app_id)]['data']['name']
        game_image = game_data[str(app_id)]['data']['header_image']

    game_description = get_game_description(game_name, game_data[str(app_id)]['data']['short_description'])

    return (game_name, app_id, game_description, game_image)

def get_game_name(app_id):
    '''
    When we just want to get the name, and avoid unnecessary api calls.
    '''
    g_api = f'http://store.steampowered.com/api/appdetails/?appids={app_id}&format=json'
    game_data = cache.get(g_api).json()
    if not game_data or 'data' not in game_data[str(app_id)]:
        return get_unlisted_name(app_id)
    else:
        return game_data[str(app_id)]['data']['name']

def get_game_description(game_name, steam_description):
    '''
    gets description of game from IGDB, otherwise uses steam description if
    possible.
    '''
    url = f'{app.config["IGDB_API_URL"]}/games/?fields=*&limit=1&search={game_name}'
    headers = {
            'Accept': 'application/json',
            'user-key': app.config['IGDB_API_KEY']
            }
    res = cache.get(url, headers=headers).json()[0]
    # check if we actually found something
    if 'summary' in res.keys():
        return shorten_description(res['summary'])
    # otherwise use steam description
    elif len(steam_description) > 0:
        return shorten_description(steam_description)
    # if no steam description, just tell the user
    else:
        return "Sorry, we couldn't find a description for this game 😥"

def shorten_description(description):
    '''
    A helper method to chop strings more than 200 characters long. It tries to find the closest
    sentence end and then just cut there.
    '''
    if len(description) > 200:
        try:
            num = description.index('. ', 190)
            description = description[:num] + '...'
        except Exception:
            print('Something went wrong with game description extraction')
    return description

def get_unlisted_name(game_id):
    '''
    searches a list of all unlisted games which were on steam for the given game-
    I couldn't find an api that allowed search by id.
    '''
    st_api = 'https://steam-tracker.com/api?action=GetAppList'
    res = cache.get(st_api).json()['removed_apps']
    for app in res:
        if app['appid'] == str(game_id):
            return app['name']
    return None
