import re
from flask import render_template, g, flash, redirect, session
from app import app, oid, user_info, game_info, rec
from random import random
import os

_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')


@app.before_first_request
def startup():
    data = rec.load_file('./training_data')
    rec.train(data)
    print('done')


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
    # just some test games for now
    recs = rec.get_rec(g.user, 10)
    print(recs)
    session['games'] = [287700, 285980, 219150, 480490, 418370, 367500]
    return render_template('loading.html')

@app.route('/logout')
def logout():
    session.pop('openid', None)
    session.pop('games', None)
    return redirect(oid.get_next_url())

def get_random_shrek():
    num = int(random()*len(os.listdir('./app/shreks')))
    filename = os.listdir('./app/shreks')[num]
    file = open('./app/shreks/' + filename)
    return file.read()
