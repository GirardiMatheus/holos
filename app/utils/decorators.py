from functools import wraps
from flask import redirect, url_for, session

def login_required(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        if 'username' not in session:
            return redirect(url_for('auth.login'))
        return route(*args, **kwargs)
    return wrapper