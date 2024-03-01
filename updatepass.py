from rev.models import Users
from rev.helpers import do_hash


users = Users.select()

for user in users:
    username = user.username
    password = do_hash(username)

    if user.username == 'admin':
        password = do_hash('#admin999')
    
    update = Users.update(password=password).where(Users.id==user.id)
    try:
        update.execute()
        print(f"{user.username} password was updated")
    except:
        print('error')