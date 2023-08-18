from flask_login import current_user

from flask_socketio import emit

from app.extensions import db, socketio

from .models import Room


@socketio.on('player_joined', namespace='/game')
def player_joined(data):
    print("aa")

    room_id = data['room_id']

    room = Room.query.filter_by(room_id=room_id).first()
    players = room.players

    print("ee")

    emit('update_players', {'owner_id': room.owner_id, 'players': players, 'player_count': len(players)}, room=room_id, namespace='/game', broadcast=True)


@socketio.event
def leave_room(user_id):
    Room.delete_inactive_rooms()

    room = Room(current_user.id) # type: ignore

    room.players.append(current_user)

    db.session.add(room)
    db.session.commit()

    emit('response', {
        'id' : 'room_created', 
        'message' : "room created", 
        'data': room
    }, broadcast=True)