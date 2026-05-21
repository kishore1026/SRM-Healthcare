from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """Login form for doctor authentication."""

    username = StringField(
        'Username',
        validators=[
            DataRequired(message='Username is required.'),
            Length(min=3, max=50, message='Username must be between 3 and 50 characters.')
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Enter your username',
            'autofocus': True,
            'autocomplete': 'username'
        }
    )

    password = PasswordField(
        'Password',
        validators=[
            DataRequired(message='Password is required.'),
            Length(min=4, max=128, message='Password must be at least 4 characters.')
        ],
        render_kw={
            'class': 'form-control',
            'placeholder': 'Enter your password',
            'autocomplete': 'current-password'
        }
    )

    remember_me = BooleanField('Remember Me')

    submit = SubmitField(
        'Sign In',
        render_kw={'class': 'btn btn-primary btn-lg w-100'}
    )
