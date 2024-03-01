from rev.models import Users
from flask import session, abort, redirect, url_for
from rev.config import app


def user_authenticated():
    # user = key value is id
    if 'user' not in session:
        return False
    
    user = Users.select(Users.id == session['user'])
    if user.exists():
        return True
    else:
        return False


def user_get():
    if 'user' in session:
        user = session['user']
        return Users.get(id=user)
    else:
        return None


def secure():
    if not user_authenticated():
        return redirect(url_for('auth.action_login'))
    else:
        pass
    

def secure_admin():
    if not user_authenticated():
        return redirect(url_for('auth.login'))
    else:
        if current_user().level != 'admin':
            abort(500)
    

def current_user():
    return user_get()
    

@app.context_processor
def utility_processor():
    return dict(
        user_authenticated=user_authenticated(), 
        current_user=current_user())
