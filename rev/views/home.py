import math
from flask import Blueprint, render_template, flash, redirect, url_for, abort, request
from rev.models import Checking, Breaks, Reports
from rev.helpers import current_date, current_datetime, calc_datetime
from rev.forms import FormCheckout, FormReport
from rev.users import secure, current_user
from peewee import PeeweeException

bp = Blueprint('home', __name__)


@bp.before_request
def secure_site():
    return secure()


def _get_404(model, **exp):
    try:
        return model.get(**exp)
    except PeeweeException:
        abort(404)


def _break_choices():
    return ['lunch', 'bio', 'coaching', 'short', 'meeting']


@bp.route('/')
def action_index():
    uid = current_user().id
    current_status = 'out'
    break_choices = _break_choices()
    checking = Checking.select().where(Checking.users == uid, Checking.status == 'in').order_by(Checking.id.desc())
    status_in = Checking.select().where(Checking.users == uid, Checking.status == 'in')

    if status_in.exists():
        current_status = 'in'

    ctx = {
        'checking': checking,
        'current_status': current_status,
        'status': status_in,
        'break_choices': break_choices,
    }
    return render_template('home/index.html', **ctx)
    

@bp.route('/check-in')
def action_check_in():
    uid = current_user().id
    check_record = Checking.select().where(Checking.users == uid).order_by(Checking.id.desc()).limit(1)
    
    checking = Checking(
        users=uid,
        checkin=current_datetime(),
        checkout=current_datetime(),
        status='in',
        total_hours=0,
    )

    if check_record.exists():
        check_record = check_record.get()

        if check_record.status == 'in':
            flash('Cannot <b>CHECK-IN</b>, you are currently in <b>CHECK-IN</b> status', 'danger')

        else:
            try:
                checking.save()
                flash('<b>CHECK-IN</b> successful!', 'success')
            
            except Exception as err:
                flash(f'Failed to add record, Please contact admin. {err}', 'danger')

    else:
        try:
            checking.save()
            flash('<b>Initial CHECK-IN</b> successful!', 'success')
        
        except Exception as err:
            flash(f'Failed to add record, Please contact admin. {err}', 'danger')
    
    # always return to home
    return redirect(url_for('home.action_index'))


@bp.route('/check-out/<int:id>', methods=['GET', 'POST'])
def action_check_out(id):
    uid = current_user().id
    checking = _get_404(Checking, id=id, users=uid)

    form = FormCheckout()

    # check if there are active breaks
    active_breaks = Breaks.select().where(Breaks.users == uid, Breaks.status=='start')
    if active_breaks.exists():
        flash('You have active break, please stop to continue checking out', 'danger')
        return redirect(url_for('home.action_index'))

    if form.validate_on_submit():
        
        if checking.status == 'out':
            flash('This timelog was already Checked-OUT', 'danger')

        else:
            # time difference
            checkout_time = current_datetime()
            total_hours = calc_datetime(checking.checkin, checkout_time)

            checking.checkout = current_datetime()
            checking.status = 'out'
            checking.eod = form.eod.data
            checking.total_hours = total_hours
            checking.updated = current_datetime()
            
            try:
                checking.save()
                flash('CHECK OUT successful!', 'success')
                return redirect(url_for('home.action_index'))
            except Exception as err:
                flash('Failed CHECK-OUT, Please contact admin. {}'.format(err), 'danger')

    return render_template('home/out.html', form=form, checking=checking)
    

@bp.route('/break-start/<string:mode>')
def action_break_start(mode):
    uid = current_user().id
    break_types = _break_choices()
    if mode not in break_types:
        abort(404)

    checkin = Checking.select().where(Checking.status == 'in', Checking.users == uid)\
            .order_by(Checking.id.desc()).limit(1)
    
    if checkin.exists():
        checkin = checkin.get()
        # check if there are active breaks
        break_start = Breaks.select().where(Breaks.status == 'start', Breaks.users == uid).limit(1)
        
        if break_start.exists():
            flash('You are currently on break', 'danger')

        else:
            try:
                new_break = Breaks(
                    users=uid,
                    checking=checkin.id,
                    start=current_datetime(),
                    end=current_datetime(),
                    status='start',
                    total_hours=0,
                    mode=mode,
                    )
                new_break.save()
                flash('Break started successfully', 'success')

            except Exception as err:
                flash(f'Error processing [{err}]', 'danger')
    
    else:
        flash('You are not Checked-IN', 'danger')

    return redirect(url_for('home.action_index'))


@bp.route('/break-stop/<int:id>')
def action_break_stop(id):
    uid = current_user().id
    breaks = _get_404(Breaks, id=id, users=uid)

    if breaks.status == 'stop':
        abort(404)

    try:
        end_time = current_datetime()
        calc_hours = calc_datetime(breaks.start, end_time)
        breaks.status = 'stop'
        breaks.end = end_time
        breaks.total_hours = calc_hours
        breaks.save()
        flash('Break has stopped', 'success')

    except PeeweeException as err:
        flash('Something went wrong', 'danger')

    return redirect(url_for('home.action_index'))


@bp.route('/checking-details/<int:id>')
def action_checking_details(id):
    uid = current_user().id
    checking = _get_404(Checking, id=id)

    total_log_hours = checking.total_hours
    total_break_hours = 0

    for item in checking.breaks:
        total_break_hours += item.total_hours

    working_hours = total_log_hours - total_break_hours
    from_url = request.args.get('from_url') or url_for('home.action_timelogs')

    return render_template(
        'home/checking-details.html', 
        checking=checking, 
        current_date=current_date(),
        working_hours=working_hours,
        total_break_hours=total_break_hours,
        from_url=from_url,
    )


@bp.route('/timelogs')
def action_timelogs():
    uid = current_user().id
    page = int( request.args.get('page') or 1)
    timelogs_count = Checking.select().where(Checking.users == uid).count()
    timelogs = Checking.select().where(Checking.users == uid).order_by(Checking.created.desc()).paginate(page,10)
    page_number = math.ceil( (timelogs_count or 1) / 10 ) + 1

    return render_template('home/timelogs.html', 
                           timelogs=timelogs, page=page, 
                           page_number=page_number, 
                           timelogs_count=timelogs_count,
                        )


@bp.route('/report', methods=['GET', 'POST'])
def action_report():
    form = FormReport()
    msg = None

    form.resolved.data = False

    if request.method == 'POST':
        try:
            Reports.create(
                title=form.title.data,
                severity=form.severity.data,
                details=form.details.data,
                resolved=form.resolved.data,
                users=current_user().id,
                )
            flash('Report was submitted', 'success')
            return redirect(url_for('home.action_report'))
        except Exception as err:
            flash(f'Something went wrong. error{err}', 'danger')
        
    return render_template('home/report.html', form=form)

