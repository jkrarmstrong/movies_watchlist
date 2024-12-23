# flask_wtf will add functionality for protection againts csrf attacks
from typing import Any
from flask_wtf import FlaskForm
from wtforms import StringField, IntegerField, SubmitField, TextAreaField, URLField, PasswordField
from wtforms.validators import InputRequired, NumberRange, Email, Length, EqualTo


# Class for creating new movie entries
# title, director and year forms require input
class MovieForm(FlaskForm):
    title = StringField("Title", validators=[InputRequired()])
    director = StringField("Director", validators=[InputRequired()])
    year = IntegerField("Year", validators=[InputRequired(), NumberRange(min=1878, message="Please enter enter a year in the format YYYY")])
    submit = SubmitField("Add Movie")




class StringListField(TextAreaField):
    def _value(self):
        if self.data:
            return "\n".join(self.data)
        else:
            return ""
    
    def process_formdata(self, valuelist):
        if valuelist and valuelist[0]:
            self.data = [line.strip() for line in valuelist[0].split("\n")]
        else:
            self.data = []



class ExtendedMovieForm(MovieForm):
    cast = StringListField("Cast")
    series = StringListField("Series")
    tags = StringListField("Tags")
    description  = TextAreaField("Description")
    video_link = URLField("Video link")

    submit = SubmitField("Submit")



class RegisterForm(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=8, message="Your password must be minimum 8 charachters.")])
    confirm_password = PasswordField("Confirm Password", validators=[InputRequired(), EqualTo("password", message="This password did not match the previous one.")])
    submit = SubmitField("Register")


class Loginform(FlaskForm):
    email = StringField("Email", validators=[InputRequired(), Email()])
    password = StringField("Password", validators=[InputRequired()])
    submit = SubmitField("Login")