from flask import Flask
from flask_openid import OpenID

app = Flask(__name__)
app.config.from_object('config')

oid = OpenID(app)

from app import views
