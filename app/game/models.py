from datetime import datetime, timedelta

from app.extensions import db

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

    @classmethod
    def delete_inactive_rooms(cls):
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        inactive_rooms = cls.query.filter(
            cls.players == [1],  # Check if players list has only 1 player
            cls.last_active < one_hour_ago  # Check if last_active is older than 1 hour
        ).all()

        for room in inactive_rooms:
            db.session.delete(room)

        db.session.commit()

class RoomPlayers(db.Model):
    __tablename__ = 'room_players'

    room_id = db.Column(db.Integer, db.ForeignKey('room.room_id'), primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)