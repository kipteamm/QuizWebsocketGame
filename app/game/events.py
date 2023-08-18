from flask_socketio import join_room, leave_room

from flask_login import current_user

from flask_socketio import emit

from app.extensions import db, socketio

from .models import Room


@socketio.on('join_game', namespace='/game')
def join_game(data):
    room_id = data['room_id']

    join_room(room_id)

    room = Room.query.filter_by(room_id=room_id).first()
    
    players = []

    for player in room.players:
        players.append({
            'user_id' : player.id,
            'username' : player.username
        })

    emit('update_players', {'owner_id': room.owner_id, 'players': players}, room=room_id, namespace='/game', broadcast=True)


@socketio.on('leave_game', namespace='/game')
def leave_game(data):
    room_id = data['room_id']

    leave_room(room_id)

    room = Room.query.filter_by(room_id=room_id).first()
    
    players = []

    for player in room.players:
        players.append({
            'user_id' : player.id,
            'username' : player.username
        })

    emit('update_players', {'owner_id': room.owner_id, 'players': players}, room=room_id, namespace='/game', broadcast=True)