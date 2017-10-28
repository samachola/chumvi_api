from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True)
    email = db.Column(db.String(50), unique=True)
    name = db.Column(db.String(100))
    admin = db.Column(db.Boolean)
    password = db.Column(db.String(80))

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    category_name = db.Column(db.String(50))

class Recipe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200))
    ingredients = db.Column(db.String)
    steps = db.Column(db.String)
    category_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer)

if __name__ == '__main__':
    app.run()