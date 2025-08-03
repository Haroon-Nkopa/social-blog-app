from flask_wtf import FlaskForm
from typing import Optional
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Email, EqualTo, ValidationError, Length
import sqlalchemy as sa
from app.models import User
from app import db


class LoginForm(FlaskForm):
    username = StringField('username',validators=[DataRequired()])
    password = PasswordField('password', validators=[DataRequired()])
    remember_me = BooleanField('remember me')
    submit = SubmitField('signin')

def validate_email(self, email):
    query = sa.Select(User).where(User.email == email.data)
    user = db.session.scalar(query)
    if user is not None:
        raise ValidationError('you a different email')
    
def validate_username(self, username):
    query = sa.select(User).where(User.username == username.data)
    user = db.session.scalar(query)
    if user is not None :
        raise ValidationError('Use a different username')



class registrationForm(FlaskForm):
    username = StringField('username', validators=[DataRequired(), validate_username])
    email = StringField('email', validators=[DataRequired(), Email(), validate_email])
    password = PasswordField('password', validators=[DataRequired()])
    password2 = PasswordField('repeat password', validators=[DataRequired(),EqualTo('password') ])    
    submit = SubmitField('register')


class EditProfileForm(FlaskForm):
    username = StringField('username', validators=[DataRequired()])
    about_me = TextAreaField('About me', validators=[Length(min=0, max=140)])
    submit = SubmitField('submit')

    def __init__(self, original_username, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if self.original_username != username.data:
            #make request to the db 
            query = sa.select(User).where(User.username == username.data)
            user = db.session.scalar(query)
            if user:
                raise ValidationError('Use a different name champ!')    

class EmptyForm(FlaskForm):
    submit = SubmitField()

class PostForm(FlaskForm):
    postText = TextAreaField('Say something', validators=[DataRequired(), Length(min=1, max=140)])
    submit = SubmitField('post')  

class password_reset_request(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()]) 
    submit = SubmitField('send email')
    
class Reset_Password(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    password02 = PasswordField('repeate password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('change password')    