import re
from flask import render_template, g, flash, redirect, session
from app import app, oid, user_info, game_info, rec
from random import random
import os
import shutil

_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')

@app.before_first_request
def startup():
    # load from the file.
    global data, game_matrix
    # try to load
    try:
        print('loading training data')
        data, game_matrix = rec.load('./training_data')
    # if something goes wrong, trace a random user and then try again!
    except Exception:
        print('no data found, loading random user data')
        u_info = user_info.get_user_data(76561198045011271)
        friend_set = user_info.traverse_friend_graph(76561198045011271)
        for i in friend_set:
             user_info.get_user_data(i)
        data, game_matrix = rec.load('./training_data')
        print('loaded')


@app.before_request
def before_request():
   g.shrek = get_random_shrek()

@app.route('/')
def index():
    if 'user' in session and session['user'] is not None:
        unplayed_games = user_info.get_unplayed_games(session['user'])
        data, game_matrix = rec.load('./training_data')
        naive =  False
        # we have already trawled this user, just give them their recs!
        if session['user'] in data['user'].cat.categories:
            recs = rec.get_rec(int(session['user']), data, game_matrix)
            games = [r[0] for r in recs if r[0] in unplayed_games]
            expln = [r[1] for r in recs if r[0] in unplayed_games]
        # give naive recommendations when there is nothing
        elif 'naive' not in session or session['naive'] is None:
            session['naive'] = True
            naive = True
            games = user_info.get_naive_recs(int(session['user']))
            expln = None
        # if they have seen naive recomendations, then do the graph search
        # and get their recommendation
        elif 'naive' in session:
           session.pop('naive', None)
           naive = False
           # friend search
           u_info = user_info.get_user_data(session['user'])
           friend_set = user_info.traverse_friend_graph(session['user'])
           for i in friend_set:
                user_info.get_user_data(i)
           # reload data (as the above search writes straight to the csv)
           data, game_matrix = rec.load('./training_data')
           # and then get our recs
           recs = rec.get_rec(int(session['user']), data, game_matrix)
           games = [r[0] for r in recs if r[0] in unplayed_games]
           expln = [r[1] for r in recs if r[0] in unplayed_games]

        games = games[:9]
        game_infos = [game_info.get_game_info(id) for id in games]
        if expln is not None:
            expln = expln[:9]
            expln_names = [[game_info.get_game_info(id) for id in r] for r in expln]
            expln_names = [[n[0] for n in r] for r in expln_names]
            print(expln_names)
        else:
            expln_names = None
        return render_template('index.html', games=game_infos, naive=naive, expln=expln_names)
    else:
        session.pop('naive', None)
        return render_template('index.html')


@app.route('/login')
@oid.loginhandler
def login():
    if 'user' in g and g.user is not None:
        return redirect(oid.get_next_url())
    return oid.try_login(app.config['STEAM_API_URL'])


@oid.after_login
def after_login(resp):
    print(resp.identity_url)
    session['user'] = _steam_id_re.search(resp.identity_url).group(1)
    print(session['user'])
    g.user = session['user']
    flash("Here's some basic reccomendations while we load better ones!")
    return redirect('/')

@app.route('/naive_landing')
def naive_landing():
   return redirect

@app.route('/logout')
def logout():
    session.pop('openid', None)
    session.pop('games', None)
    session.pop('user', None)
    session.pop('naive', None)
    return redirect(oid.get_next_url())

def get_random_shrek():
    shreks = list(filter(lambda f: f.endswith('.txt'), os.listdir('./app/shreks')))
    num = int(random()*len(shreks))
    filename =shreks[num]
    file = open('./app/shreks/' + filename)
    return file.read()
