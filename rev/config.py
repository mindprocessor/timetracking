import tomllib
from flask import Flask
from flask_wtf.csrf import CSRFProtect
from peewee import MySQLDatabase


with open("config.toml", "rb") as f:
    config_data = tomllib.load(f)


app = Flask(__name__)
app.config['SECRET_KEY'] = config_data['flask']['secret_key']
app.config['TEMPLATE_RELOAD'] = config_data['flask']['template_reload']
app.config['SESSION_COOKIE_SECURE'] = config_data['flask']['session_cookie_secure']


csrf = CSRFProtect(app)
db = MySQLDatabase(
    database=config_data['database']['database'], 
    user=config_data['database']['user'],
    password=config_data['database']['password'], 
    host=config_data['database']['host'], 
    port=config_data['database']['port'],
    )
