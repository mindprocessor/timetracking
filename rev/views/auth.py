from flask import render_template as render
from flask import url_for, flash, redirect, Blueprint, session
from rev.forms import FormLogin
from rev.helpers import do_hash
from rev.models import Users


bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['POST', 'GET'])
def action_login():
    form = FormLogin()
    if form.validate_on_submit():
        username = form.username.data
        password = do_hash(form.password.data)
        user = Users.select().where(Users.username == username, Users.password == password)
        
        if user.exists():
            user = user.get()
            if user.status:
                session['user'] = user.id
                return redirect(url_for('home.action_index'))
            else:
                flash('Your account is deactivated', 'danger')
                return redirect(url_for('auth.action_login'))
        
        else:
            flash('Username / Password is wrong!', 'danger')
            return redirect(url_for('auth.action_login'))
            
    return render('auth/login.html', form=form)


@bp.route('/logout')
def action_logout():
    session.pop('user', None)
    return redirect(url_for('auth.action_login'))