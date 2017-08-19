import re
from flask import render_template, g, flash, redirect
from app import app, oid
from app.userinfo import get_userinfo

_steam_id_re = re.compile('steamcommunity.com/openid/id/(.*?)$')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
@oid.loginhandler
def login():
    if 'user' in g and g.user is not None:
        return redirect(oid.get_next_url())
    return oid.try_login('http://steamcommunity.com/openid')


@oid.after_login
def after_login(resp):
    g.user = _steam_id_re.search(resp.identity_url).group(1)
    flash(f'User id is {g.user}')
    return redirect(oid.get_next_url())
