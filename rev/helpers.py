import random
import string
from datetime import datetime as dt
from zoneinfo import ZoneInfo


def do_hash(word):
    from hashlib import sha256
    encrypt = sha256(word.encode('utf-8')).hexdigest()
    return encrypt


def html_alert(msg, category):
    html = """
        <div class="alert alert-{0} alert-dismissible fade show fixed-top m-4" role="alert">
            {1}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    """.format(category, msg)
    return html


def str_datetime_now():
    td = current_datetime()
    string_date = f'{td.year}-{td.month}-{td.day} {td.hour}:{td.minute}'
    return string_date


def str_date_now():
    td = current_datetime()
    string_date = f'{td.year}-{td.month}-{td.day}'
    return string_date


def calc_datetime(date_from, date_to):
    d_f = date_from
    d_t = date_to

    # convert to hours
    result = (d_t - d_f).total_seconds() / 3600
    return round(result, 2)


def compare_datetime(date_one, date_two):
    d_o = date_one
    d_t = date_two
    result = d_o < d_t
    return result


def obj_datetime(string_datetime):
    datetime_object = dt.datetime.strptime(string_datetime, '%Y-%m-%d %H:%M')
    return datetime_object


def current_datetime():
    timezone = ZoneInfo('Asia/Manila')
    return dt.now(tz=timezone).replace(microsecond=0, tzinfo=None)


def current_date():
    timezone = ZoneInfo('Asia/Manila')
    return dt.now(tz=timezone).date()


def current_month():
    # timezone should be global
    timezone = ZoneInfo('Asia/Manila')
    date = dt.now(tz=timezone)
    month = date.month
    year = date.year
    return f'{year}-{month:02d}'


def random_string():
    # initializing size of string
    n = 7

    # using random.choices()
    # generating random strings
    result = ''.join(random.choices(string.ascii_lowercase + string.digits, k=n))
    return result
