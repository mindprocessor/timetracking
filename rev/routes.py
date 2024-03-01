from rev.config import app
from rev.views import home, auth
from rev.views.admin import bp as admin_bp
from rev.htmx.admin import bp as htmx_admin
from rev.htmx.user import bp as htmx_user


app.register_blueprint(home.bp, url_prefix='/')
app.register_blueprint(auth.bp, url_prefix='/auth')

# admin
app.register_blueprint(admin_bp, url_prefix='/admin')

# hmtx admin
app.register_blueprint(htmx_admin, url_prefix='/htmx/admin')

# hmtx user
app.register_blueprint(htmx_user, url_prefix='/htmx/user')
