from flask import Blueprint, abort
from rev.users import user_authenticated


bp = Blueprint('htmx_user', __name__)


# check auth
@bp.before_request
def action_check_auth():
    if user_authenticated():
        pass
    else:
        abort(404)


def action_sample():
    return 'sample'