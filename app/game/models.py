from datetime import datetime, timedelta

from app.extensions import db

from sqlalchemy import func, or_, and_

import random
import time


class Room(db.Model):
    __tablename__ = 'room'

    room_id = db.Column(db.Integer, unique=True, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    question_index = db.Column(db.Integer, default=1)

    players = db.relationship('User', secondary='room_players', backref=db.backref('rooms', lazy='dynamic'))

    started = db.Column(db.Boolean, default=False)
    last_active = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, owner):
        self.owner_id = owner

        while True:
            room_id = str(random.randint(10000, 99999))

            # Check if the room ID already exists in the database
            if not Room.query.filter_by(room_id=room_id).first():
                self.room_id = room_id
                
                break

    def get_players(self):
        players = []

        for player in self.players: # type: ignore
            players.append({
                'user_id' : player.id,
                'username' : player.username,
                'points' : player.points
            })

        return players

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'owner_id': self.owner_id,
            'players': [{'id': user.id, 'username': user.username} for user in self.players], # type: ignore
            'started': self.started,
            'last_active': self.last_active.isoformat()  # Convert datetime to ISO format
        }

    @classmethod
    def delete_inactive_rooms(cls):
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)

        inactive_rooms_query = cls.query.filter(
            or_ (
                and_(
                    func.json_array_length(cls.players) == 1,
                    cls.last_active < one_hour_ago
                ),
                func.json_array_length(cls.players) == 0
            )
        )

        inactive_rooms = inactive_rooms_query.all()

        for room in inactive_rooms:
            MultipleChoiceQuestion.query.filter_by(room_id=room.room_id).delete()
            Answer.query.filter_by(room_id=room.room_id).delete()
    
            db.session.delete(room)

        db.session.commit()


class RoomPlayers(db.Model):
    __tablename__ = 'room_players'

    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)


class MultipleChoiceQuestion(db.Model):
    __tablename__ = 'multiple_choice_question'

    question_id = db.Column(db.Integer, unique=True, primary_key=True)
    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'))
    index = db.Column(db.Integer)

    question = db.Column(db.Text)
    answer = db.Column(db.Text)

    creation_timestamp = db.Column(db.Float)

    def __init__(self, room_id: int, question_index: int, question: str, answer: str, creation_timestamp: float):
        self.question_id = int(str(time.time()).replace('.', ''))
        self.room_id = room_id
        self.index = question_index
        self.question = question
        self.answer = answer
        self.creation_timestamp = creation_timestamp

    def to_dict(self):
        return {
            'room_id': self.room_id,
            'index': self.index,
            'question': self.question,
            'answer': self.answer
        }


class Answer(db.Model):
    __tablename__ = "answer"

    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)

    index = db.Column(db.Integer)

    def __init__(self, room_id: int, user_id: int, index: int):
        self.room_id = room_id
        self.user_id = user_id
        self.index = index