from flask_login import login_required, current_user

from flask import Blueprint, render_template, redirect, request, flash

from app.extensions import db

from .functions import user_object

from .models import Room, MultipleChoiceQuestion, Answer


game_blueprint = Blueprint('game', __name__)

@game_blueprint.route('/home', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == "POST":
        if 'create_room' in request.form:
            room = Room.query.filter_by(owner_id=current_user.id).first() # type: ignore

            if room:
                db.session.delete(room)

            Room.delete_inactive_rooms()

            room = Room(current_user.id) # type: ignore

            room.players.append(current_user)

            db.session.add(room)
            db.session.commit()

            return redirect(f'game?id={room.room_id}')
    
        if 'join_room' in request.form:
            room = Room.query.filter_by(room_id=request.form.get('join_room')).first()

            if room:
                if len(room.players) == 3:
                    flash('This room is full.', 'error')

                    return render_template('game/home.html')

                return redirect(f'game?id={room.room_id}')
            
            flash('No room found with this ID.', 'error')

            return render_template('game/home.html')


    return render_template('game/home.html')


@game_blueprint.route('/game', methods=['GET', 'POST'])
@login_required
def game():
    room_id = request.args.get('id')

    room = Room.query.filter_by(room_id=room_id).first()

    if room is None:
        return redirect('home')
    
    current_user.points = 0
    
    if current_user not in room.players:
        if len(room.players) == 3:
            flash('This room is full.', 'error')

            return render_template('game/home.html')
        
        room.players.append(current_user)
        db.session.commit()

    return render_template('game/game.html', user=user_object(current_user), room=room.to_dict()) # type: ignore


@game_blueprint.route('/test', methods=['GET'])
@login_required
def test():
    Room.query.delete()
    MultipleChoiceQuestion.query.delete()
    Answer.query.delete()
    
    db.session.commit()

    return '<h1>success</h1>'