from flask_login import current_user

from flask_socketio import emit

from app.extensions import db, socketio

from .models import Room

@socketio.event
def create_room():
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


@socketio.event
def join_room(room_id):
    Room.delete_inactive_rooms()

    room = Room.query.filter_by(room_id=room_id).first()

    if room is None:
        emit('response', {
            'id': 'room_join_failed',
            'message': 'Room not found',
            'data': None
        })
        return

    if current_user not in room.players:
        room.players.append(current_user)
        db.session.commit()

    emit('response', {
        'id': 'room_joined',
        'message': 'Room joined',
        'data': room.room_id
    }, broadcast=True)