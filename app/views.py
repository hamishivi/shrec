import re
from flask import render_template, g, flash, redirect, session
from app import app, oid, user_info, game_info

_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')

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
    session['games'] = [287700, 285980, 219150, 480490, 418370, 367500]
    return redirect(oid.get_next_url())
