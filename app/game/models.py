from datetime import datetime, timedelta

from app.extensions import db

from sqlalchemy import func

import random

class Room(db.Model):
    __tablename__ = 'room'

    room_id = db.Column(db.Integer, unique=True, primary_key=True)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

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

        inactive_rooms = cls.query.filter(
            func.json_array_length(cls.players) == 1, 
            cls.last_active < one_hour_ago 
        ).all()

        for room in inactive_rooms:
            db.session.delete(room)

        db.session.commit()

class RoomPlayers(db.Model):
    __tablename__ = 'room_players'

    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)