import re
from flask import render_template, g, flash, redirect, session
from app import app, oid, user_info, game_info, rec
from random import random
import os
import shutil

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
    print(session)
    print('user' in g)
    if 'user' in session and session['user'] is not None:
        unplayed_games = user_info.get_unplayed_games(session['user'])
        recs = rec.get_rec(int(session['user']), 10000)
        print(recs)
        naive = False
        if recs is None and 'naive' not in session:
            session['naive'] = True
            recs = user_info.get_naive_recs(int(session['user']))
            games = recs
            naive = True
        elif 'naive' in session and recs is None:
           session.pop('naive', None)
           u_info = user_info.get_user_data(session['user'])
           friend_set = user_info.traverse_friend_graph(session['user'])
           for i in friend_set:
                user_info.get_user_data(i)
           print('training data')
           data = rec.load_file('./training_data')
           rec.train(data)
           print('done!')
           recs = rec.get_rec(int(g.user), 10000)
           games = [r.product for r in recs if r.product in unplayed_games]
        else:
           games = [r.product for r in recs if r.product in unplayed_games]
        # need to filter for games in library
        #unplayed_games =  user_info.get_unplayed_games(session['user'])
        #games = [r.product for r in recs if r.product in unplayed_games]
        games = games[:12]
        game_infos = [game_info.get_game_info(id) for id in games]
        return render_template('index.html', games=game_infos, naive=naive)
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
    return redirect(oid.get_next_url())

def get_random_shrek():
    shreks = list(filter(lambda f: f.endswith('.txt'), os.listdir('./app/shreks')))
    num = int(random()*len(shreks))
    filename =shreks[num]
    file = open('./app/shreks/' + filename)
    return file.read()
