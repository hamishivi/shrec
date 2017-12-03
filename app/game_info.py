import requests
import csv
from app import app

def get_game_info(app_id):
    '''
    returns a tuple (game_name, game_id, game_description, game_image)
    Ideally we will also get game description and images.

    '''
    g_api = 'http://store.steampowered.com/api/appdetails/?appids=' + str(app_id) + '&format=json'
    output = []
    game_data = requests.get(g_api).json()
    if not game_data or 'data' not in game_data[str(app_id)]:
        # broken game, look it up on steam-tracker
        game_name = get_unlisted_name(app_id)
        game_image = "Sorry, no image found"
        # no help here :'(
        if game_name is None:
            return ("Broken Game", app_id, "This game doesn't exist!?", "No image :'(")
    else:
        game_name = game_data[str(app_id)]['data']['name']
        game_image = game_data[str(app_id)]['data']['header_image']
    game_description = get_game_description(game_name)
    # fall back on steam api
    if (len(game_description) == 0):
        game_description = game_data[str(app_id)]['data']['short_description']
    if (len(game_description) == 0):
        game_description = "Sorry, we couldn't find a description for this game :'("
    if len(game_description) > 200:
        try:
            num = game_description.index('. ', 190)
            game_description = game_description[:num] + '...'
        except Exception:
            print('Something went wrong with game description extraction')
    return (game_name, app_id, game_description, game_image)


def get_game_description(game_name):
    url = app.config['IGDB_API_URL']  + '/games/?fields=*&limit=1&search=' + game_name
    headers = {
            'Accept': 'application/json',
            'user-key': app.config['IGDB_API_KEY']
            }
    res = requests.get(url, headers=headers).json()[0]
    if 'summary' in res.keys():
        return res['summary']
    else:
        return ''

def get_unlisted_name(game_id):
    st_api = 'https://steam-tracker.com/api?action=GetAppList'
    res = requests.get(st_api).json()['removed_apps']
    for app in res:
        if app['appid'] == str(game_id):
            return app['name']
    return None
