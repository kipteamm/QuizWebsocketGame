from flask import Blueprint, render_template

from flask_login import login_required

game_blueprint = Blueprint('game', __name__)

@game_blueprint.route('/home')
@login_required
def home():
    return render_template('game/home.html')