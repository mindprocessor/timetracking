from flask import Flask
from flask_wtf.csrf import CSRFProtect
from peewee import SqliteDatabase, MySQLDatabase


app = Flask(__name__)
app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['PRESERVE_CONTEXT_ON_EXCEPTION'] = False
app.config['TEMPLATE_RELOAD'] = True
app.config['SESSION_COOKIE_SECURE'] = False

csrf = CSRFProtect(app)
#db = SqliteDatabase('data.sqlite3')
db = MySQLDatabase(database="hms247", user="root", password="", host="127.0.0.1", port=3306)
