from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, TextAreaField, HiddenField, BooleanField
from wtforms.validators import DataRequired, Email, ValidationError
from rev.users import current_user
from rev.helpers import do_hash


class FormLogin(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])


class FormUser(FlaskForm):
    user_type_choices = [('user', 'user'), ('admin', 'admin')]
    employee_id = StringField('Employee ID', validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired()])
    first_name = StringField('First Name', validators=[DataRequired()])
    last_name = StringField('Last Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    account = StringField('Account', validators=[DataRequired()])
    level = SelectField('Level', choices=user_type_choices, validators=[DataRequired()])

            
class FormCheckout(FlaskForm):
    eod = TextAreaField('End of Day Report', validators=[DataRequired()])
    

class FormChangePassword(FlaskForm):
    new_password = PasswordField('New password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired()])

    def validate_confirm_password(self, confirm_password):
        if confirm_password.data != self.new_password.data:
            raise ValidationError('Confirm password do not match')


class FormDeleteUser(FlaskForm):
    password = PasswordField('Password', validators=[DataRequired()])
    confirmation_code = StringField('Confirmation Code', validators=[DataRequired()])
    confirmation_code_hidden = HiddenField('Confirmation Hidden', validators=[DataRequired()])

    def validate_confirmation_code(self, confirmation_code):
        if confirmation_code.data != self.confirmation_code_hidden.data:
            raise ValidationError('Confirmation Code did not match')

    def validate_password(seld, password):
        curr_password = current_user().password
        password_data = do_hash(password.data)
        if curr_password != password_data:
            raise ValidationError('Password is not valid')
        

class FormReport(FlaskForm):
    title = StringField('Title', validators=[DataRequired()])
    severity = SelectField('Severity', validators=[DataRequired()], choices=['low', 'medium', 'high'])
    details = TextAreaField('Details', validators=[DataRequired()])
    remarks = TextAreaField('Remarks')
    resolved = BooleanField('Resolved')
