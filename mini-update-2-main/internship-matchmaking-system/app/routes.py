from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from .models import User, Opportunity
from datetime import datetime

# Define a Blueprint for routes
main = Blueprint('main', __name__)

# Home page route
@main.route('/')
def index():
    return render_template('index.html')


# Registration Route
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        skills = request.form['skills']  # New skills input field

        # Hash the password for security
        hashed_password = generate_password_hash(password, method='sha256')

        # Add the new user to the database
        new_user = User(username=username, email=email, password=hashed_password, skills=skills)
        db.session.add(new_user)
        db.session.commit()

        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')


# Login Route
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists in the database
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Store the user_id in the session after successful login
            session['user_id'] = user.id

            flash('Login successful!', 'success')
            return redirect(url_for('main.dashboard_user'))
        else:
            flash('Login failed. Invalid email or password.', 'danger')

    return render_template('login.html')


# Admin Login Route
@main.route('/admin', methods=['GET', 'POST'])
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # Check if the user exists in the database
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):
            # Store the user_id in the session after successful login
            session['user_id'] = user.id

            flash('Admin login successful!', 'success')
            return redirect(url_for('main.dashboard_admin'))
        else:
            flash('Admin login failed. Invalid email or password.', 'danger')

    return render_template('admin.html')



# User Dashboard Route
@main.route('/dashboard_user')
def dashboard_user():
    if 'user_id' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('main.login'))

    user = User.query.get(session['user_id'])
    user_skills = set(user.skills.split(',')) if user.skills else set()

    opportunities = Opportunity.query.all()
    matching_opportunities = [
        opp for opp in opportunities 
        if user_skills & set(opp.skills_required.split(','))
    ]

    return render_template('dashboard.html', opportunities=matching_opportunities)


# Admin Dashboard Route
@main.route('/dashboard_admin')
def dashboard_admin():
    if 'user_id' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('main.login_admin'))

    user = User.query.get(session['user_id'])
    opportunities = Opportunity.query.all()
    return render_template('dashboard2.html', opportunities=opportunities)

# Create Opportunity Route
@main.route('/create_opportunity', methods=['GET', 'POST'])
def create_opportunity():
    if 'user_id' not in session:
        flash('You need to log in first.', 'warning')
        return redirect(url_for('main.login_admin'))

    user = User.query.get(session['user_id'])
    if 'user_id' not in session:
        flash('Unauthorized access.', 'danger')
        return redirect(url_for('main.dashboard_user'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        skills_required = request.form['skills_required']
        posted_date = datetime.now()

        new_opportunity = Opportunity(
            title=title, 
            description=description, 
            skills_required=skills_required, 
            posted_date=posted_date
        )
        
        db.session.add(new_opportunity)
        db.session.commit()

        flash('Opportunity created successfully!', 'success')
        return redirect(url_for('main.dashboard_admin'))

    return render_template('create_opportunity.html')


# Logout Route
@main.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('You have been logged out.', 'success')
    return redirect(url_for('main.login'))
