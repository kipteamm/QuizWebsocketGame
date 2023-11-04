from flask import Flask, redirect, url_for, flash

from flask_login import LoginManager

from flask_migrate import Migrate

from .game.events import register_events as register_game_events

from .auth.models import User
from .auth.views import auth_blueprint

from .game.functions import *
from .game.views import game_blueprint

from .main.views import main_blueprint

from .extensions import db, socketio

def create_app():
    app = Flask(__name__)
    app.config["DEBUG"] = True
    app.config["SECRET_KEY"] = "secret"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\Admin\\OneDrive - Stedelijk Onderwijs Antwerpen\\Desktop\\development\\QuizWebsocketGame\\app\\data\\database.db'


    app.register_blueprint(auth_blueprint)
    app.register_blueprint(game_blueprint)
    app.register_blueprint(main_blueprint)

    login_manager = LoginManager(app)

    db.init_app(app)

    migrate = Migrate()
    migrate.init_app(app, db)

    @login_manager.user_loader
    def load_user(user_id):
        # Implement the logic to load the user object from the user ID
        return User.query.get(int(user_id))

    @login_manager.unauthorized_handler
    def unauthorized():
        flash('Please log in to access this page.', 'error')
        return redirect(url_for('auth.login'))

    socketio.init_app(app)
    register_game_events(socketio)

    return app