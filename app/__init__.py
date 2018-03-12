from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flasgger import Swagger
from flask_cors import CORS

app = Flask(__name__, instance_relative_config=True)
CORS(app)
#load the config file
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

#load the routes
#from app import api

swagger = Swagger(app, 
        template={
            "consumes":[
                "application/json"
            ],
            "produces":[
                "application/json"
            ],
            "Accept":[
                "application/json"
            ]
        }
)

from .categories import mod
from .auth import mod
from .recipes import mod

app.register_blueprint(categories.mod, url_prefix='/api-v0')
app.register_blueprint(auth.mod, url_prefix='/api-v0')
app.register_blueprint(recipes.mod, url_prefix='/api-v0')
