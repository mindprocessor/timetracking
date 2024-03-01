from flask import Blueprint, abort, request, flash
from flask import render_template as render
from rev.users import current_user, user_authenticated
from rev.models import Users, Checking, Breaks, Reports
from rev.forms import FormChangePassword, FormReport
from rev.helpers import html_alert, do_hash, current_date, current_month
from peewee import fn


bp = Blueprint('htmx_admin', __name__)


# check auth
@bp.before_request
def check_auth():
    if user_authenticated():
        user_level = current_user().level
        if user_level != 'admin' and user_level != 'superadmin':
            abort(404)
    else:
        abort(404)


#private---
def _get_404(model, **exp):
    try:
        return model.get(**exp)
    except:
        return abort(404)


# ATTENDANCE
# ATTENDANCE

@bp.route('/attendance/<int:uid>', methods=['GET', 'POST'])
def action_attendance(uid):
    context = {}
    month = None
    user = _get_404(Users, id=uid)

    if request.method == 'POST':
        month = request.form.get('month') or current_month()
        attendance = Checking.select().where(Checking.users==uid)\
                    .where(Checking.created.contains(month))\
                    .order_by(Checking.id.desc())
        print(month)

    if request.method == 'GET':
        attendance = Checking.select().where(Checking.users==uid)\
                    .order_by(Checking.id.desc()).limit(5)
    context = {
        'attendance': attendance,
        'user': user,
        'month': month,
        }
    return render('htmx/admin/attendance.html', **context)


@bp.route('/edit-password/<int:id>', methods=['GET', 'POST'])
def action_edit_password(id):
    user = Users.get(id=id)
    form = FormChangePassword()
    msg = None
    change_pass = False

    if form.validate_on_submit():
        if user.id == current_user().id:
            change_pass = True
        elif user.level == 'admin':
            msg = html_alert('User account is an admin. Cannot process your requests', 'danger')
            change_pass = False
        else:
            change_pass = True
        
        if change_pass:
            new_password = form.new_password.data
            hash_new_password = do_hash(new_password)

            try:
                user.password = hash_new_password
                user.save()
                msg = html_alert('Changes was save', 'success')
            except Exception as err:
                msg = html_alert('f{err}', 'danger')
        
    else:
        msg = html_alert('Validation error', 'danger')
        
    return render('htmx/admin/user-password.html', form=form, user=user, msg=msg)


@bp.route('/timelog/<int:id>',)
def action_timelog(id):
    timelog = _get_404(Checking, id=id)

    break_hours_sum = Breaks.select(fn.SUM(Breaks.total_hours)).where(Breaks.checking==id).scalar()
    working_hours = (timelog.total_hours or 0) - (break_hours_sum or 0)

    return render('htmx/admin/timelog.html', 
                  timelog=timelog, 
                  working_hours=working_hours,
                  break_hours_sum=break_hours_sum)


@bp.route('/report/<int:id>', methods=['GET', 'POST'])
def action_report(id):
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
        except Exception as err:
            msg = html_alert(f'Something went wrong. error[{err}]', 'danger')
            

    if request.method == 'GET':
        form.title.data = report.title
        form.severity.data = report.severity
        form.details.data = report.details
        form.remarks.data = report.remarks
        form.resolved.data = report.resolved

    return render('/htmx/admin/report.html', form=form, report=report, msg=msg)

