from flask import render_template
from app import app, oid

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
@oid.loginhandler
def login():
    return oid.try_login('http://steamcommunity.com/openid')


@oid.after_login
def after_login(resp):
    return str(resp)
