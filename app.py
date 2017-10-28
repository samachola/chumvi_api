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



if __name__ == '__main__':
    app.run()