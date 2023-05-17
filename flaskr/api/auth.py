import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify

)
from werkzeug.security import check_password_hash, generate_password_hash

from flaskr.models import Base, User, Result

db = Base.get_db()

bp = Blueprint('auth', __name__, url_prefix='')


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                User.get_by_username(username)
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                copy = request.json.copy()
                copy['password'] = generate_password_hash(password)
                User.add(copy)
                return jsonify(Result.success(msg='registered successful'))
        flash(error)

    return jsonify(Result.fail(msg='registered failed'))


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.json['username']
        password = request.json['password']
        error = None
        user = User.get_by_username(username)

        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user.password, password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user.id
            return jsonify(Result.success(msg='login successful'))

        flash(error)
    return jsonify(Result.fail(msg='login failed'))


@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = User.get_by_id(user_id)


@bp.route('/logout')
def logout():
    session.clear()
    return jsonify(Result.success(msg='logout successful'))


def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return jsonify(Result.fail(msg='login required'))

        return view(**kwargs)

    return wrapped_view
