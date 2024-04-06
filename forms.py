from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, EmailField, TextAreaField
from wtforms.validators import InputRequired, Email, Length

class RegistrationForm(FlaskForm):
    username = StringField("Username", 
                           validators=[InputRequired(), Length(max=20, message="Maximum 20 characters")])
    password = PasswordField("Password", 
                             validators=[InputRequired()])
    email = EmailField("Email", 
                       validators=[InputRequired(), Email(message='Not a valid email.')])
    first_name = StringField("First Name", 
                             validators=[InputRequired()])
    last_name = StringField("Last Name", 
                             validators=[InputRequired()])

class LoginForm(FlaskForm):
    username = StringField("Username", 
                           validators=[InputRequired()])
    password = PasswordField("Password", 
                             validators=[InputRequired()])
    
class FeedbackForm(FlaskForm):
    title = StringField("Title",
                        validators=[InputRequired(), Length(max=100)])
    content = TextAreaField("Content", 
                            validators=[InputRequired()])
    
    