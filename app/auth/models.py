from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

from app.extensions import db

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    # Authentication
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    is_active = db.Column(db.Boolean, default=True)

    # Current game
    points = db.Column(db.Integer, default=0)
    
    # Statistics
    victories = db.Column(db.Integer, default=0)
    games_played = db.Column(db.Integer, default=0)

    def __init__(self, username, password):
        self.username = username
        self.set_password(password)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    @staticmethod
    def authenticate(username, password):
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            return user
        return None
