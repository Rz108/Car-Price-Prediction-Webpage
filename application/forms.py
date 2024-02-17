from flask_wtf import FlaskForm
from wtforms import FloatField, SubmitField, SelectField, PasswordField, BooleanField, StringField
from wtforms.fields import DateField, EmailField, TelField
from wtforms.validators import Length, InputRequired, ValidationError, NumberRange,Length, Optional, URL, Email, Regexp, EqualTo,  ValidationError
import pandas as pd
import os


# Create the registration form for user to register
class RegistrationForm(FlaskForm):
    username = StringField('Username', validators = [InputRequired()])
    email = EmailField('Email Address', validators =[InputRequired(), Email()])
    password_1 = PasswordField('Password', validators = [InputRequired()])
    password = PasswordField('Confirm Password', validators = [InputRequired(),EqualTo('password_1') ])
    submit = SubmitField('Register')

# Create the login form for the user to login
class Login(FlaskForm):
    email = EmailField('Email Address', validators =[InputRequired(), Email()])
    password = PasswordField('Password', validators =[ InputRequired()])
    save = BooleanField('Remeber Me', validators = [Optional()], default=False)
    submit = SubmitField('Login')


# Set the current directory to get the brands
current_directory = os.path.dirname(os.path.abspath(__file__))
data = pd.read_csv(f'{current_directory}/train.csv')
brand_names = ['Honda', 'Cadillac', 'Toyota', 'Mazda', 'Chevrolet', 'MINI', 'Mercedes-Benz', 'Jeep', 'Maserati', 'Lexus', 'Audi', 'Porsche', 'Land', 'Mitsubishi', 'Kia', 'Hyundai', 'Volvo', 'Volkswagen', 'Ford', 'FIAT', 'Alfa', 'BMW', 'Nissan', 'Jaguar', 'Suzuki']
engines = data['engine'].dropna().unique()
transmissions = data['transmission'].dropna().unique()
fuel_types = data['fuel_type'].dropna().unique()
drivetrains = data['drivetrain'].dropna().unique()

# Creating the prediction form
class PredictionForm(FlaskForm):
    brand_choices = [(brand, brand) for brand in brand_names]
    engine_choices = [(engine, engine) for engine in engines ]
    fuel_choices = [(fuel, fuel) for fuel in fuel_types ]
    transmission_choices = [(transmission, transmission) for transmission in transmissions ]
    drivetrain_choices = [(drivetrain, drivetrain) for drivetrain in drivetrains  ]
    brand = SelectField("Brand", choices=brand_choices, validators=[InputRequired()])
    year = FloatField("Year", validators=[InputRequired(), NumberRange(1968,2023)])
    mileage = FloatField("Mileage", validators=[InputRequired(), NumberRange(min = 0)])
    engine = SelectField("Engine", choices=engine_choices, validators=[InputRequired()])
    engine_size = FloatField("Engine Size", validators=[InputRequired(), NumberRange(min = 0)])
    transmission = SelectField("Transmissions", choices=transmission_choices, validators=[InputRequired()])
    fuel_type = SelectField("Fuel Type", choices=fuel_choices, validators=[InputRequired()])
    drivetrain = SelectField("Drive Train", choices=drivetrain_choices, validators=[InputRequired()])
    min_mpg = FloatField("Minimum MPG", validators=[InputRequired(), NumberRange(min = 0)])
    damaged = SelectField('Damaged', choices=[('','') , (1, 'Yes'),(0, 'No')]  , validators = [InputRequired()])
    turbo = SelectField('Turbo', choices=[('','') , (1, 'Yes'),(0, 'No')]  , validators = [InputRequired()])
    navigation_system = SelectField('Navigation System', choices=[('','') , (1, 'Yes'),(0, 'No')]  , validators = [InputRequired()])
    backup_camera = SelectField('Back Up Camera', choices=[('','') , (1, 'Yes'),(0, 'No')]  , validators = [InputRequired()])
    first_owner = SelectField('New', choices=[('','') , (1, 'Yes'),(0, 'No')]  , validators = [InputRequired()])
    submit = SubmitField("Predict")



# Creating the reset password form 
class ResetPasswordForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email()])
    new_pw = PasswordField('New Password', validators=[InputRequired()])
    submit = SubmitField('Reset Password')


# Set the change password here
class ChangePasswordForm(FlaskForm):
    new_password = PasswordField('New Password', validators=[InputRequired()])
    confirm_new_password = PasswordField('Confirm New Password',
                                         validators=[InputRequired(),
                                                     EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Change Password')