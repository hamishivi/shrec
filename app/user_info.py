from app import cache
import csv
import pprint
from urllib.parse import urljoin
from app import app
import sqlite3 as sql

def _steam_endpoint(endpoint, apikey=app.config['STEAM_API_KEY'], **params):
    '''
    Return a formatted endpoint URL from the Steam API

    Warning: Will fail if no parameters are included in the endpoint
    '''
    url = [urljoin("http://api.steampowered.com/", endpoint)]

    if apikey:
        params["key"] = apikey
    paramstring = "&".join([f"{k}={params[k]}" for k in params])
    if paramstring:
        url.append("?" + paramstring)
    return cache.get(urljoin(*url))

def get_naive_recs(steam_id, maxrec=5):
    '''
    Get recomendations using a naive non-machine-learning approach
    '''
    def get_game_data(appid):
        BASE_URL = "http://store.steampowered.com/api/"
        return cache.get(urljoin(BASE_URL, f"appdetails?appids={appid}"))

    def get_genres(game):
        return get_game_data(game['appid']).json()[str(game['appid'])]['data']['genres']

    user_data = get_user_data_raw(steam_id)['response']
    games = user_data['games']
    games.sort(key=lambda x: x['playtime_forever'], reverse=True)

    games_played = [i for i in games if i['playtime_forever'] > 0]
    games_unplayed = [i for i in games if i['playtime_forever'] == 0]
    games_top = [games[i] for i in range(min(maxrec, len(games_played)))]

    from pprint import pprint
    try:
        genres_top = set()
        for game in games_top:
            genres_top |= set(genre["id"] for genre in get_genres(game))

        recs = []
        for game in games_unplayed:
            genres = set(genre['id'] for genre in get_genres(game))
            if len(recs) > 5:
                break

            if genres_top & genres:
                recs.append(game['appid'])
        return recs
    except Exception:
        return games_top[:12]

def get_user_data_raw(steam_id):
    '''
    returns json of user games
    '''
    req = _steam_endpoint('IPlayerService/GetOwnedGames/v0001', steamid=steam_id, format="json")
    return req.json()



# def get_user_data(steam_id):
#     '''
#     Create a csv file called training_data with the format: (steamid,gameid,play_time)
#     '''
#     game_data = get_user_data_raw(steam_id)
#     played = filter_unplayed(game_data)
#     if played is None:
#         return
#     print(len(played))
#     with open('training_data','a') as f:
#         writer = csv.writer(f, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
#         for i in game_data['response']['games']:
#             if i['playtime_forever'] > 0:
#                 writer.writerow([steam_id, i['appid'], i['playtime_forever']])


def get_user_data(steam_id):

    '''

    Insert all games playtime data of steam_id user into database 'data.db' with relation:
        Play_time(steamid, gameid, play_time)
    Create db if doensn't exist

    '''

    conn = sql.connect('../data.db')
    c = conn.cursor()

    #Potential bug: Storing steamid as INTEGER (max: 2^64)
    c.execute(''' CREATE TABLE IF NOT EXISTS Play_time
                (steamid INTEGER, gameid INTEGER, play_time INTEGER)''')

    game_data = get_user_data_raw(steam_id)
    games = game_data['response']['games']
    played = filter_unplayed(game_data)
    if played is None:
        return
    print(len(played))


    rows = [(steam_id, i['appid'], i['playtime_forever']) for i in games if i['playtime_forever'] > 0]
    c.executemany('INSERT INTO Play_time VALUES (?, ?, ?)', rows)

    conn.commit()
    conn.close()




def get_unplayed_games(steam_id):
    '''
    gets all unplayed games from a certain user.
    '''
    return filter_unplayed(get_user_data_raw(steam_id))

def filter_unplayed(game_data):
    '''
    Filter out unplayed games from the data set
    '''
    unplayed_games = []
    try:
        for i in game_data['response']['games']:
            if i['playtime_forever'] == 0:
                unplayed_games.append(i['appid'])
        return unplayed_games
    except KeyError:
        pass

def traverse_friend_graph(steam_id, cap=50, maxdepth=4, visited=set(), depth=0):
    """Get a recursive list of connections up to a certain depth and number"""

    def get_friends(steam_id):
        """Get a list of friends for a steam user"""
        req = _steam_endpoint('ISteamUser/GetFriendList/v0001',
                              steamid=steam_id, relationship='friend')
        friends = req.json()
        try:
            return friends['friendslist']['friends']
        except KeyError:
            return []

    if len(visited) >= cap or depth >= maxdepth:
        return visited

    visited.add(steam_id)
    for i in get_friends(steam_id):
        if i['steamid'] in visited:
            continue
        visited |= traverse_friend_graph(i['steamid'], cap=cap, maxdepth=maxdepth,
                                         visited=visited, depth=depth+1)
    return visited
