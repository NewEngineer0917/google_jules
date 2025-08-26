from flask import render_template, redirect, url_for, flash, abort, Blueprint
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, logout_user, login_required, current_user
from .models import User, Todo
from .forms import LoginForm, RegistrationForm, TodoForm
from . import db

main = Blueprint('main', __name__)

@main.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return redirect(url_for('main.index'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@main.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='pbkdf2:sha256')
        user = User(username=form.username.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('main.login'))
    else:
        for fieldName, errorMessages in form.errors.items():
            for err in errorMessages:
                flash(f"Error in {fieldName}: {err}", 'danger')
    return render_template('signup.html', title='Sign Up', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/', methods=['GET', 'POST'])
@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    form = TodoForm()
    if form.validate_on_submit():
        todo = Todo(content=form.content.data, author=current_user)
        db.session.add(todo)
        db.session.commit()
        flash('Your todo has been added!', 'success')
        return redirect(url_for('main.index'))
    todos = Todo.query.filter_by(author=current_user).all()
    return render_template('index.html', title='Home', form=form, todos=todos)

@main.route('/todo/complete/<int:todo_id>')
@login_required
def complete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.author != current_user:
        abort(403)
    todo.completed = not todo.completed
    db.session.commit()
    return redirect(url_for('main.index'))

@main.route('/todo/delete/<int:todo_id>')
@login_required
def delete_todo(todo_id):
    todo = Todo.query.get_or_404(todo_id)
    if todo.author != current_user:
        abort(403)
    db.session.delete(todo)
    db.session.commit()
    flash('Your todo has been deleted!', 'success')
    return redirect(url_for('main.index'))
