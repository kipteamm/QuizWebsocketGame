from flask_socketio import join_room, leave_room

from flask_login import current_user

from flask_socketio import emit

from app.extensions import db, socketio

from .models import Room

import requests
import time


@socketio.on('join_game', namespace='/game')
def join_game(data):
    room_id = data['room_id']

    join_room(room_id)

    room = Room.query.filter_by(room_id=room_id).first()

    if room:
        players = []

        for player in room.players:
            players.append({
                'user_id' : player.id,
                'username' : player.username
            })

        emit('update_players', {'owner_id': room.owner_id, 'players': players}, room=room_id, namespace='/game', broadcast=True)
    else:
        emit('kick_all', room=room_id, namespace='/game', broadcast=True)


@socketio.on('leave_game', namespace='/game')
def leave_game(data):
    room_id = data['room_id']

    leave_room(room_id)

    room = Room.query.filter_by(room_id=room_id).first()

    if room:
        room.players.remove(current_user)

        if current_user.id == room.owner_id: # type: ignore
            db.session.delete(room)

        db.session.commit()

        players = []

        for player in room.players:
            players.append({
                'user_id' : player.id,
                'username' : player.username
            })

        emit('update_players', {'owner_id': room.owner_id, 'players': players}, room=room_id, namespace='/game', broadcast=True)
    else:
        emit('kick_all', room=room_id, namespace='/game', broadcast=True)


@socketio.on('start_game', namespace='/game')
def start_game(data):
    room_id = data['room_id']

    emit('starting', room=room_id, namespace='/game', broadcast=True)

    time.sleep(5)

    room = Room.query.filter_by(room_id=room_id).first()

    room.started = True

    response = requests.get('https://opentdb.com/api.php?amount=1&difficulty=medium&type=multiple')

    print()

    if response.ok:
        emit('question', response.json()['results'][0], room=room_id, namespace='/game', broadcast=True)