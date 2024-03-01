from rev.models import Users
from rev.helpers import do_hash


username = 'admin'
password = do_hash('#admin999')

user = Users(
    username=username,
    password=password,
    level='admin',
    first_name='administrator',
    last_name='administrator',
    account='admin',
    email='admin@mail.com',
    superadmin=True,
)

try:
    user.save()
    print(f'user created with username:{username} and password:admin')
except Exception as err:
    print(f'error - {err}')
