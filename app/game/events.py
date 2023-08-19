from flask_socketio import join_room, leave_room

from flask_login import current_user

from flask_socketio import emit

from app.extensions import db, socketio

from .models import Room, MultipleChoiceQuestion, RoomPlayers

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
                'username' : player.username,
                'points' : player.points
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
            for question in MultipleChoiceQuestion.query.filter_by(room_id=room_id):
                db.session.delete(question)

            db.session.delete(room)

        db.session.commit()

        players = []

        for player in room.players:
            players.append({
                'user_id' : player.id,
                'username' : player.username,
                'points' : player.points
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

    response = requests.get('https://opentdb.com/api.php?amount=1&difficulty=easy&type=multiple')

    if response.ok:
        question = response.json()['results'][0]

        question_object = MultipleChoiceQuestion(room.room_id, room.question_index, question['question'], question['correct_answer'], time.time())

        db.session.add(question_object)
        db.session.commit()

        emit('question', question, room=room_id, namespace='/game', broadcast=True)

        time.sleep(30)

        emit('time_is_up', room=room_id, namespace='/game', broadcast=True)


@socketio.on('answer', namespace='/game')
def answer(data):
    room = Room.query.filter_by(room_id=data['room_id']).first()

    question = MultipleChoiceQuestion.query.filter_by(room_id=room.room_id, index=room.question_index).first()

    if question:
        points = 30 - round(time.time() - question.creation_timestamp)

        if data['answer'] == question.answer:
            if len(question.answers) == 0:
                points += 30

            elif len(question.answers) == 1:
                points += 20

            elif len(question.answers) == 2:
                points += 10

            question.answers.append(current_user)
        else:
            points = 0

        current_user.points += points # type: ignore

        db.session.commit()


@socketio.on('time_is_up', namespace='/game')
def time_is_up(data):
    room = Room.query.filter_by(room_id=data['room_id']).first()

    question = MultipleChoiceQuestion.query.filter_by(room_id=room.room_id, index=room.question_index).first()

    for player in room.players:
        if not player in question.players:
            player.points += 0

    room.question_index += 1