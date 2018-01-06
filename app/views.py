import re
import os
import random
from contextlib import suppress
from flask import render_template, g, flash, redirect, session, jsonify
from app import app, oid, user_info, game_info, rec

STEAM_ID_RE = re.compile('steamcommunity.com/openid/id/(.*?)$')


@app.before_request
def before_request():
   g.shrek = get_random_shrek()


@app.route('/')
def index():
    if 'user' in session:
        steam_id = session['user']
        return render_template('loading.html')
    else:
        return render_template('index.html')


@app.route('/reccomendations/<int:steam_id>')
def reccomendations(steam_id):
    user_info.save_owned_games(steam_id)
    for person in user_info.fetch_friend_network(steam_id):
        with suppress(user_info.PrivateAccount):
            user_info.save_owned_games(person)
    recs = rec.get_rec(steam_id, *rec.load('./training_data'))
    unplayed = user_info.filter_unplayed(user_info.fetch_owned_games(steam_id))
    return render_template('reccomendations.html', rec=[
            (game, expln) for game, expln in recs if game in unplayed
    ][:9])

@app.route('/api/game-info/<int:game_id>')
def game_data(game_id):
    return jsonify(game_info.fetch_game_info(game_id)._asdict())

@app.route('/api/game-names/<games>')
def game_names(games):
    return ', '.join([game_info.fetch_game_name(app_id) for app_id in eval(games)])

@app.route('/login')
@oid.loginhandler
def login():
    if 'user' in g:
        return redirect(oid.get_next_url())
    else:
        return oid.try_login(app.config['STEAM_API_URL'])


@oid.after_login
def after_login(resp):
    session['user'] = STEAM_ID_RE.search(resp.identity_url).group(1)
    g.user = session['user']
    return redirect('/')


@app.route('/logout')
def logout():
    session.pop('openid', None)
    session.pop('games', None)
    session.pop('user', None)
    session.pop('naive', None)
    return redirect(oid.get_next_url())


SHREKS = [entry.path for entry in os.scandir('./app/shreks') if entry.name.endswith('.txt')]

def get_random_shrek():
    with open(random.choice(SHREKS)) as shrek:
        return shrek.read()
