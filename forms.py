from flask_wtf import Form
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField
from wtforms.validators import DataRequired, Email, Length
import pymysql

class SignupForm(Form):
    first_name = StringField('First name', validators=[DataRequired("Please enter your firstname")])
    last_name = StringField('Last name', validators=[DataRequired("Please enter your lastname")])
    email = StringField('Email', validators=[DataRequired("Please enter your email"), Email("Enter your email")])
    password = PasswordField('Password', validators=[DataRequired("Please enter your password"), Length(min=6, message="Password must be at least 6 characters")])
    submit = SubmitField('Submit')


class LoginForm(Form):
    email = StringField('Email', validators=[DataRequired("Please enter your valid email address."), Email("Please enter the email")])
    password = PasswordField("Password", validators=[DataRequired("Please enter your Password")])
    submit = SubmitField('Submit')

class CityForm(Form):
    connection = pymysql.connect(host='localhost',user='root',password='h3llo2u', db='hotels')
    cursor = connection.cursor()
    cities  = []
    with connection:
        sql = "SELECT DISTINCT `city` FROM `hotel_ratings` ORDER BY `city` ASC"
        cursor.execute(sql)
        result = cursor.fetchall()
        for r in result:
            cities.append(r[0])
    cursor.close()
    city = SelectField('Select City', choices=[tuple([city, city]) for city in cities if city is not None])
    submit = SubmitField('Submit')
