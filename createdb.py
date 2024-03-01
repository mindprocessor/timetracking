from rev import db 
from rev.models import Users, Checking, Breaks, Reports


try:
    db.create_tables([
        # Users, Checking, Breaks
        Reports
        ])
    print('database created')

except Exception as err:
    print(f'error - {err}')