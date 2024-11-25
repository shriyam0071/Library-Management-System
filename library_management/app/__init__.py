from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo
from config import Config

mongo = PyMongo()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    mongo.init_app(app)
    login_manager.init_app(app)

    from app.routes import main
    app.register_blueprint(main)

    return app