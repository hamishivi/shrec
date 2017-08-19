import requests
import csv
import pprint
from urllib.parse import urljoin
from app import app

def _steam_endpoint(endpoint, apikey=app.config['STEAM_API_KEY'], **params):
    '''
    Return a formatted endpoint URL from the Steam API
    '''
    url = [urljoin("http://api.steampowered.com/", endpoint)]

    if apikey:
        params["key"] = apikey
    paramstring = "&".join([f"{k}={params[k]}" for k in params])
    if paramstring:
        url.append("?" + paramstring)

    return urljoin(*url)

def get_user_data(steam_id):
    '''
    Create a csv file called training_data with the format: (steamid,gameid,play_time)
    '''
    url = _steam_endpoint('IPlayerService/GetOwnedGames/v0001', steamid=steam_id, format="json")
    game_data = requests.get(url).json()
    print(len(filter_unplayed(game_data)))
    with open('training_data','a') as f:
        writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for i in game_data['response']['games']:
            writer.writerow([steam_id, i['appid'], i['playtime_forever']])

def filter_unplayed(game_data):
    '''
    Filter out unplayed games from the data set
    '''
    unplayed_games = []
    for i in game_data['response']['games']:
        if i['playtime_forever'] == 0:
            unplayed_games.append(i['appid'])
    return unplayed_games

def traverse_friend_graph(steam_id,visited=set(),depth=0):
	if depth > 1:
		print('Recursion depth reached')
		return visited
	visited.add(steam_id)
	pp = pprint.PrettyPrinter(indent=4)
	f_api = _steam_endpoint('ISteamUser/GetFriendList/v0001', steamid=steam_id, relationship='friend')
	friends = requests.get(f_api).json()
	for i in friends['friendslist']['friends']:
		if i['steamid'] in visited:
			continue
		try:
			visited |= traverse_friend_graph(i['steamid'],visited,depth=depth+1)
		except KeyError:
			print("no friend scrub",steam_id)
			print(i)
	print(visited)
	return visited
