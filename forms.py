from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length


class RegisterForm(FlaskForm):
    # This form should accept a username, password, email, first_name, and last_name
    
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Length(max=50)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30)])

class LoginForm(FlaskForm):
    # This form should accept a username, password
    
    username = StringField("Username", validators=[InputRequired(), Length(max=20)])
    password = PasswordField("Password", validators=[InputRequired()])

class SearchForm(FlaskForm):
    # This form should accept a search string
    
    search = StringField("Search", validators=[InputRequired(), Length(max=40)], render_kw={"placeholder": "Search..."})
