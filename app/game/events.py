from flask_socketio import join_room, leave_room

from flask_login import current_user

from flask_socketio import emit

from app.extensions import db, socketio

from .models import Room, MultipleChoiceQuestion, Answer

import requests
import time


def ack():
    print('message was received!')


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

            emit('kick_all', room=room_id, namespace='/game', broadcast=True)

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

    db.session.commit()

    print('new question')

    emit('new_question', {'owner_id' : room.owner_id}, room=room.room_id, namespace='/game', broadcast=True, callback=ack)


@socketio.on('ask_question', namespace='/game')
def ask_question(data):
    print('ask_question received')

    room = Room.query.filter_by(room_id=data['room_id']).first()

    if MultipleChoiceQuestion.query.filter_by(room_id=room.room_id, index=room.question_index).first():
        print('here 1')

        return

    response = requests.get('https://opentdb.com/api.php?amount=1&difficulty=easy&type=multiple')

    if response.ok:
        question = response.json()['results'][0]

        question_object = MultipleChoiceQuestion(room.room_id, room.question_index, question['question'], question['correct_answer'], time.time())

        db.session.add(question_object)
        db.session.commit()

        print('question sent')

        emit('question', question, room=room.room_id, namespace='/game', broadcast=True)

        time.sleep(15)

        emit('question_end', room=room.room_id, namespace='/game', broadcast=True)
    
    else:
        print('here 2')

        emit('kick_all', room=room.room_id, namespace='/game', broadcast=True)


@socketio.on('answer', namespace='/game')
def answer(data):
    room = Room.query.filter_by(room_id=data['room_id']).first()

    question = MultipleChoiceQuestion.query.filter_by(room_id=room.room_id, index=room.question_index).first()

    if question:
        points = 30 - round(time.time() - question.creation_timestamp)

        if data['answer'] == question.answer:
            user_answers = Answer.query.filter_by(room_id=room.room_id, index=room.question_index).count()

            if user_answers == 0:
                points += 30

            elif user_answers == 1:
                points += 20

            elif user_answers == 2:
                points += 10

        else:
            points = 0

        user_answer = Answer(room.room_id, current_user.id, room.question_index) # type: ignore

        current_user.points += points # type: ignore

        db.session.add(user_answer)
        db.session.commit()


@socketio.on('end_question', namespace='/game')
def end_question(data):
    print('question ended')

    room = Room.query.filter_by(room_id=data['room_id']).first()

    for player in room.players:
        answer = Answer.query.filter_by(room_id=room.room_id, user_id=player.id, index=room.question_index).first()

        if not answer:
            player.points += 0

    emit('update_players', {'owner_id': room.owner_id, 'players': room.get_players()}, room=room.room_id, namespace='/game', broadcast=True)

    room.question_index += 1

    if room.question_index < 4:
        print('new question')

        emit('new_question', room=room.room_id, namespace='/game', broadcast=True)