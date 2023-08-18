from flask_login import login_required, current_user

from flask import Blueprint, render_template, redirect, request

from app.extensions import db, socketio

from .models import Room


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
                socketio.emit('player_joined', {'player_id': current_user.id}, room=room.room_id, namespace='/game') # type: ignore

                print("emitted")

                return redirect(f'game?id={room.room_id}')


    return render_template('game/home.html')


@game_blueprint.route('/game', methods=['GET', 'POST'])
@login_required
def game():
    room_id = request.args.get('id')

    room = Room.query.filter_by(room_id=room_id).first()

    if room is None:
        return redirect('home')
    
    if current_user not in room.players:
        room.players.append(current_user)
        db.session.commit()

        socketio.emit('player_joined', {'room_id': room.room_id, 'player_id': current_user.id}, room=room.room_id, namespace='/game') # type: ignore

    return render_template('game/game.html', room=room.to_dict())