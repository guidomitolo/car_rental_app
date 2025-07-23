import mysql.connector
from config import DB_CONFIG
from flask import g



def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = mysql.connector.connect(**DB_CONFIG)
    return db

def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_app_db(app):
    app.teardown_appcontext(close_connection)