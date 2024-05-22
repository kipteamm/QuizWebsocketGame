from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user

from app.extensions import db

from sqlalchemy import func

from .models import User


auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if User.query.filter(func.lower(User.username) == func.lower(username)).first():
            flash('Username already taken. Please choose a different username.', 'error')
            return render_template('auth/register.html')

        if len(username) > 25:
            flash(f'Your username is {len(username) - 25} characters too long.', 'error')
            return render_template('auth/register.html')

        if len(username) < 1:
            flash(f'Your username is {1 - len(username)} characters too short.', 'error')
            return render_template('auth/register.html')
        
        if len(password) > 128:
            flash(f'Your password is {len(password) - 128} characters too long.', 'error')
            return render_template('auth/register.html')

        if len(password) < 8:
            flash(f'Your password is {8 - len(password)} characters too short.', 'error')
            return render_template('auth/register.html')

        user = User(username, password)

        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        
        flash('Registration successful. Welcome!', 'success')
        
        return redirect(url_for('game.home'))
    
    return render_template('auth/register.html')


@auth_blueprint.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.authenticate(username, password)
        
        if not user:
            flash('Invalid username or password', 'error')
            return render_template('auth/login.html')
        
        login_user(user)
            
        flash('Login successful. Welcome back!', 'success')
            
        return redirect(url_for('game.home'))

    return render_template('auth/login.html')
