import peewee
from flask import Blueprint, url_for, request, render_template, abort, flash, redirect
from rev.models import Checking, Users, Reports
from rev.forms import FormReport, FormUser, FormChangePassword, FormDeleteUser
from rev.users import secure_admin, current_user
from rev.helpers import current_month, do_hash, html_alert, random_string


bp = Blueprint('admin', __name__)


# check if the user is admin/superadmin ---
@bp.before_request
def check_level():
    return secure_admin()


# private function ---
def _get_404(model, **exp):
    if peewee.DoesNotExist():
        return model.get(**exp)
    else:
        abort(404)


# route functions ---
@bp.route('/', methods=['GET'])
def action_view():
    checkin_users = Checking.select(Checking, Users).join(Users, on=(Checking.users == Users.id))\
            .where(Checking.status == 'in')
    
    return render_template('admin/admin_view.html', checkin_users=checkin_users)


# USERS =========
# USERS =========

@bp.route('/users', methods=['GET', 'POST'])
def action_users():
    users = Users.select()
    return render_template('admin/users.html', users=users)


@bp.route('/user/<int:uid>', methods=['GET', 'POST'])
def action_user(uid):
    user = _get_404(Users, id=uid)
    return render_template('admin/user.html', user=user, uid=uid)


@bp.route('/user/add', methods=['POST', 'GET'])
def action_user_add():
    form = FormUser()

    if form.validate_on_submit():
        username = form.username.data
        email = form.email.data

        # find username and email
        find_username = Users.select().where(Users.username == username)
        find_email = Users.select().where(Users.email == email)

        if find_username.exists() or find_email.exists():
            flash('Username / Email is not available. Please choose another one.', 'danger')
        
        else:
            try:
                Users.create(
                    username=username,
                    first_name=form.first_name.data,
                    last_name=form.last_name.data,
                    email=form.email.data,
                    level=form.level.data,
                    account=form.account.data,
                    password=do_hash(form.password.data)
                )
                flash('New user was added!', 'success')
                return redirect(url_for('admin.action_users'))
            
            except Exception as err:
                flash(f'Error adding user! {err}', 'danger')
    
    return render_template('admin/user_add.html', form=form)


@bp.route('/user/edit/<int:uid>', methods=['GET', 'POST'])
def action_user_edit(uid):
    user = _get_404(Users, id=uid)
    form = FormUser()
    msg = None
    
    # password is required, this does not change the password
    form.password.data = "password"

    if current_user().superadmin:
        update_details = True
    elif current_user().id == user.id:
        update_details = True
    elif user.level == 'admin':
        update_details = False
    else:
        update_details = False

    if form.validate_on_submit():
        # employee id should be unique
        employee_id = form.employee_id.data
        is_employee_existing = Users.select().where(Users.eid==employee_id).where(Users.id!=uid).exists()
        if is_employee_existing:
            update_details = False
            msg = f"Employee ID ({employee_id}) is taken."

        if update_details:
            user.eid = form.employee_id.data
            user.first_name = form.first_name.data
            user.last_name = form.last_name.data
            user.email = form.email.data
            user.level = form.level.data
            user.account = form.account.data
            
            try:
                user.save()
                flash('Changes was saved!', 'success')
                return redirect(url_for('admin.action_user_edit', uid=uid))
            
            except Exception as err:
                flash(f'Error saving changes! {err}', 'danger')
        else:
            flash(f'Cannot proceed with your request. {msg}', 'danger')

    if request.method == 'GET':
        form.employee_id.data = user.eid
        form.username.data = user.username
        form.first_name.data = user.first_name
        form.last_name.data = user.last_name
        form.email.data = user.email
        form.level.data = user.level
        form.account.data = user.account

    return render_template('admin/user-edit.html', user=user, uid=uid, form=form)


@bp.route('/user/activate/<int:id>', methods=['GET'])
def action_user_activate(id):
    # only admin can activate user and admin
    user = _get_404(Users, id=id)
    user.status = True
    user.save()
    return redirect(url_for('admin.action_user', uid=id))


@bp.route('/user/delete/<int:id>', methods=['GET', 'POST'])
def action_user_delete(id):
    user = _get_404(Users, id=id)
    curr_user = current_user()
    code = random_string()
    form = FormDeleteUser()

    if request.method == 'POST':
        if form.validate():
            if user.superadmin:
                proceed_delete = False
                flash('Super admin user cannot be deleted', 'danger')
            else:
                if user.level == 'admin' and curr_user.level == 'admin':
                    proceed_delete = False
                    flash('Admin cannot delete other admin. Only superadmin can delete admin account', 'danger')
                elif user.level == 'user' and curr_user.level == 'admin':
                    proceed_delete = True
                else:
                    proceed_delete = True
            if proceed_delete:
                try:
                    user.delete_instance(recursive=True)
                    flash(f'<b>{user.username}</b> was deleted', 'success')  
                    return redirect(url_for('admin.action_users'))
                except peewee.PeeweeException:
                    flash('Error processing your request', 'danger')
        else:
            form.confirmation_code_hidden.data = code        
        
    if request.method == 'GET':
        form.confirmation_code_hidden.data = code

    return render_template(
        'admin/user-delete.html',
        user=user,
        code=code,
        form=form,
        )


@bp.route('/user/change-password/<int:uid>', methods=['GET', 'POST'])
def action_user_change_password(uid):
    user = _get_404(Users, id=uid)
    form_password = FormChangePassword()
    return render_template('admin/user-change-password.html', form_password=form_password, user=user)


@bp.route('/user/deactivate/<int:id>', methods=['GET'])
def action_user_deactivate(id):
    # only superadmin can deactivate admin users
    # admin users cannot deactivate superadmin user
    # admin can only deactivate users
    curr_user = current_user()
    proceed = True
    user = _get_404(Users, id=id)

    if user.level == 'admin':
        if curr_user.superadmin:
            proceed = True
        else:
            proceed = False

    if user.superadmin:
        proceed = False

    if proceed:
        user.status = False
        user.save()
    
    return redirect(url_for('admin.action_user', uid=id))


@bp.route('/user/timelogs/<int:id>')
def action_user_timelogs(id):
    user = _get_404(Users, id=id)
    month = request.args.get('month') or current_month()
    attendance = Checking.select().where(Checking.users==user.id)\
                    .where(Checking.created.contains(month))\
                    .order_by(Checking.id.desc())
    return render_template('admin/user-timelogs.html', month=month, user=user, attendance=attendance)


@bp.route('/user/timelog/detail/<int:id>')
def action_user_timelog_detail(id):
    timelog = _get_404(Checking, id=id)
    user = timelog.users
    breaks = timelog.breaks

    total_breaks = 0
    for item in breaks:
        total_breaks += item.total_hours

    working_hours = timelog.total_hours - total_breaks

    return render_template('admin/user-timelog-detail.html', 
                           user=user, 
                           breaks=breaks, 
                           timelog=timelog, 
                           total_breaks=total_breaks,
                           working_hours=working_hours)


# TIMELOGS ==========
# TIMELOGS ==========


@bp.route('/timelogs')
def action_timelogs():
    # get 15 last records
    timelogs = Checking.select(Checking, Users).join(Users).order_by(Checking.id.desc()).limit(15)
    return render_template('admin/timelogs.html', timelogs=timelogs)


@bp.route('/timelog/detail/<int:id>')
def action_timelog_detail(id):
    timelog = _get_404(Checking, id=id)
    return render_template('admin/timelog-detail.html', timelog=timelog)


# ATTENDANCE =============
# ATTENDANCE =============

@bp.route('/ax/attendance', methods=['GET', 'POST'])
def ax_attendance():
    action = request.args.get('action')
    ctx = {'action': action}

    if action == 'details':
        if request.args.get('id') is not None:
            uid = request.args.get('id')
            user = Users.select().where(Users.id == uid)
            
            if user.exists:
                attendance = Checking.select().where(Checking.users == uid).order_by(Checking.checkin.desc()).limit(20)
                ctx['attendance'] = attendance
                ctx['user'] = user
            
            else:
                return 'Cannot find user!'
        
        else:
            return 'ERROR!'

    else:
        users = Users.select()
        ctx['users'] = users

    return render_template('admin/attendance.html', **ctx)


# REPORTS ====
# REPORTS ====

@bp.route('/reports')
def action_reports():
    resolved = False
    resolved_status = request.args.get('resolved')

    if resolved_status == 'yes':
        resolved = True
    
    reports = Reports.select(Reports, Users).join(Users).where(Reports.resolved==resolved)
    return render_template('admin/reports.html', reports=reports)


@bp.route('/reports/edit/<int:id>', methods=['GET', 'POST'])
def action_reports_edit(id):
    report = _get_404(Reports, id=id)
    form = FormReport()
    msg = None

    if form.validate_on_submit():
        try:
            report.severity = form.severity.data
            report.remarks = form.remarks.data
            report.resolved = form.resolved.data
            report.save()
            msg = html_alert('Changes was saved', 'success')
        except peewee.PeeweeException as err:
            msg = html_alert(f'Something went wrong. error[{err}]', 'danger')
            

    if request.method == 'GET':
        form.title.data = report.title
        form.severity.data = report.severity
        form.details.data = report.details
        form.remarks.data = report.remarks
        form.resolved.data = report.resolved

    return render_template('admin/reports-edit.html', report=report, form=form, msg=msg)
