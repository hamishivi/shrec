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
    #print(game_data)
    game_name = game_data[str(app_id)]['data']['name']
    game_description = game_data[str(app_id)]['data']['short_description']
    game_image = game_data[str(app_id)]['data']['header_image']
    return (game_name, app_id, game_description, game_image)
