import re
from flask import render_template, g, flash, redirect, session
from app import app, oid, user_info, game_info, rec
from random import random
import os

_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')

'''
@app.before_first_request
def startup():
    data = rec.load_file('./training_data')
    rec.train(data)
    print('done')
'''

@app.before_request
def before_request():
   g.shrek = get_random_shrek()

@app.route('/')
def index():
    game_infos = []
    print(session)
    if 'games' in session and session['games'] is not None:
        for id in session['games']:
            game_infos.append(game_info.get_game_info(id))
    if len(game_infos) == 0:
        return render_template('index.html')
    else:
        print(game_infos)
        return render_template('index.html', games=game_infos)

@app.route('/login')
@oid.loginhandler
def login():
    if 'user' in g and g.user is not None:
        return redirect(oid.get_next_url())
    return oid.try_login(app.config['STEAM_API_URL'])


@oid.after_login
def after_login(resp):
    g.user = _steam_id_re.search(resp.identity_url).group(1)
    flash(f'User id is {g.user}')
    u_info = user_info.get_user_data(g.user)
    friend_set = user_info.traverse_friend_graph(g.user)
    for i in friend_set:
        user_info.get_user_data(i)
    print('training data')
    data = rec.load_file('./training_data')
    rec.train(data)
    print('done!')
# just some test games for now
    recs = rec.get_rec(int(g.user), 100)
    # need to filter for games in library
    unplayed_games =  user_info.get_unplayed_games(g.user)
    games = [r.product for r in recs if r.product in unplayed_games]
    session['games'] = games[:12]
    return render_template('loading.html')

@app.route('/logout')
def logout():
    session.pop('openid', None)
    session.pop('games', None)
    return redirect(oid.get_next_url())

def get_random_shrek():
    shreks = list(filter(lambda f: f.endswith('.txt'), os.listdir('./app/shreks')))
    num = int(random()*len(shreks))
    filename =shreks[num]
    file = open('./app/shreks/' + filename)
    return file.read()
