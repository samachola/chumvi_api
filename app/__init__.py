from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__, instance_relative_config=True)
#load the config file
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#load the routes
from app import api

