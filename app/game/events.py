from flask_socketio import SocketIO, join_room, leave_room

from flask_login import current_user

from flask_socketio import emit

from app.extensions import db

from .functions import game_log, clear_game_log

from .models import Room, MultipleChoiceQuestion, Answer

import requests
import time


def register_events(socketio: SocketIO):

    @socketio.on('join_game', namespace='/game')
    def join_game(data):
        room_id = data['room_id']

        join_room(room_id)

        room = Room.query.filter_by(room_id=room_id).first()

        if not room:
            emit('kick_all', room=room_id, namespace='/game', broadcast=True) # type: ignore

        players = []

        for player in room.players:
            players.append({
                'user_id' : player.id,
                'username' : player.username,
                'points' : player.points
            })

        emit('update_players', {'owner_id': room.owner_id, 'players': players}, room=room_id, namespace='/game', broadcast=True) # type: ignore
            

    @socketio.on('leave_game', namespace='/game')
    def leave_game(data):
        room_id = data['room_id']

        leave_room(room_id)

        room = Room.query.filter_by(room_id=room_id).first()

        if not room:
            emit('kick_all', room=room_id, namespace='/game', broadcast=True) # type: ignore

        room.players.remove(current_user)

        if current_user.id == room.owner_id: # type: ignore
            for question in MultipleChoiceQuestion.query.filter_by(room_id=room.room_id):  
                db.session.delete(question)

            for answer in Answer.query.filter_by(room_id=room.room_id):
                db.session.delete(answer)

            db.session.delete(room)

            emit('kick_all', room=room_id, namespace='/game', broadcast=True) # type: ignore

        db.session.commit()

        players = []

        for player in room.players:
            players.append({
                'user_id' : player.id,
                'username' : player.username,
                'points' : player.points
            })

        emit('update_players', {'owner_id': room.owner_id, 'players': players}, room=room_id, namespace='/game', broadcast=True) # type: ignore


    @socketio.on('start_game', namespace='/game')
    def start_game(data):
        room_id = data['room_id']

        #clear_game_log()

        emit('starting', room=room_id, namespace='/game', broadcast=True) # type: ignore

        time.sleep(5)

        room = Room.query.filter_by(room_id=room_id).first()

        room.started = True

        for player in room.players:
            player.games_played += 1

        db.session.commit()

        emit('new_question', {'owner_id' : room.owner_id}, room=room_id, namespace='/game', broadcast=True) # type: ignore


    @socketio.on('ask_question', namespace='/game')
    def ask_question(data):
        room_id = data['room_id']

        room = Room.query.filter_by(room_id=room_id).first()

        if MultipleChoiceQuestion.query.filter_by(room_id=room.room_id, index=room.question_index).first():
            return

        response = requests.get('https://the-trivia-api.com/v2/questions?limit=1')

        if not response.ok:
            emit('kick_all', room=room_id, namespace='/game', broadcast=True) # type: ignore

        question = response.json()[0]

        question_text = question['question']['text']
        correct_answer = question['correctAnswer']
        incorrect_answers = question['incorrectAnswers']

        question_object = MultipleChoiceQuestion(room.room_id, room.question_index, question_text, correct_answer, time.time())

        db.session.add(question_object)
        db.session.commit()

        incorrect_answers.append(correct_answer)

        emit('question', {'question' : question_text, 'answers' : incorrect_answers}, room=room_id, namespace='/game', broadcast=True) # type: ignore

        #game_log('info', "question sent", "ask_question")
            
        time.sleep(15)

        emit('question_end', {'owner_id': room.owner_id, 'question_id' : question_object.question_id, 'answer' : question_object.answer}, room=room_id, namespace='/game', broadcast=True) # type: ignore

        #game_log('info', "question end", "ask_question")


    @socketio.on('answer', namespace='/game')
    def answer(data):
        room_id = data['room_id']

        room = Room.query.filter_by(room_id=room_id).first()

        question = MultipleChoiceQuestion.query.filter_by(room_id=room.room_id, index=room.question_index).first()

        if not question:
            return

        points = 30 - round(time.time() - question.creation_timestamp)

        user_answers = Answer.query.filter_by(room_id=room.room_id, index=room.question_index).count()

        if data['answer'] == question.answer:
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

        if user_answers == len(room.players) - 1:
            emit('question_end', {'owner_id': room.owner_id, 'question_id' : question.question_id, 'answer' : question.answer}, room=room_id, namespace='/game', broadcast=True) # type: ignore


    @socketio.on('end_question', namespace='/game')
    def end_question(data):
        room_id = data['room_id']
        question_id = data['question_id']

        room = Room.query.filter_by(room_id=room_id).first()
        question = MultipleChoiceQuestion.query.filter_by(question_id=question_id).first()

        if question.answered:
            return
        
        question.answered = True

        room.question_index = room.question_index + 1

        for player in room.players:
            answer = Answer.query.filter_by(room_id=room.room_id, user_id=player.id, index=room.question_index).first()

            if not answer:
                player.points += 0

        emit('update_players', {'owner_id': room.owner_id, 'players': room.get_players()}, room=room_id, namespace='/game', broadcast=True) # type: ignore

        db.session.commit()

        if room.question_index < 11:
            emit('new_question', {'owner_id': room.owner_id}, room=room_id, namespace='/game', broadcast=True) # type: ignore

            return


        most_points, winner = 0, None

        for player in room.players:
            if player.points > most_points:
                most_points = player.points

                winner = player

            player.points = 0

        winner_data = {}

        if winner:
            winner.victories += 1 

            winner_data = {'id' : winner.id, 'username' : winner.username}

        db.session.commit()

        emit('game_end', winner_data, room=room_id, namespace='/game', broadcast=True) # type: ignore