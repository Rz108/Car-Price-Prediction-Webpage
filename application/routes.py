from application import app
from flask import render_template, request, flash, redirect, url_for,   jsonify, session
from application.forms import PredictionForm,Login ,RegistrationForm , ResetPasswordForm, ChangePasswordForm
from application import ai_model, manager
from application import db
from application.models import Prediction, User
from datetime import datetime
import pandas as pd
from flask_login import login_user , logout_user , login_required , current_user, LoginManager
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.exceptions import Forbidden
from sqlalchemy.exc import IntegrityError
import pytz
import json
import os
from sqlalchemy import desc, asc
# Set the current directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Set the login manager
login_manager = LoginManager()
login_manager.login_view = 'login'  
login_manager.init_app(app)

# Set the loader methods
@login_manager.user_loader
def loader(userid):
    return User.query.get(int(userid))

# set the home about us page here
@app.route('/')
def home():
    return render_template('home.html')


# Set the registration methods
@app.route('/register', methods=['GET', 'POST'])
def register():

    # Set up the form for registration
    form = RegistrationForm()
    # If it is a post method
    if request.method == 'POST':
        if form.validate_on_submit():

            # Check for existing user here

            existing_user = User.query.filter_by(email=form.email.data).first()
            existing_user_username = User.query.filter_by(username=form.username.data).first()
            # If there is no existing user
            if existing_user is None and existing_user_username is None:

                # It sets the password and 
                user = User(username=form.username.data, email=form.email.data)

                # Set the password after validation of password 
                user.set_password(form.password_1.data)

                # Commit to the database
                db.session.add(user)
                db.session.commit()

                # Redirect the user to login page here
                return redirect(url_for('login'))
            
            # IF the user already exist, warmog will be shown
            else:
                flash('A user with that email or username already exists.')
    
    # Return the render template here
    return render_template('register.html', form=form)


# Set the login route
@app.route('/login', methods=['GET','POST'] )
def login():

    # Set up the login form here
    form = Login()

    # If methods is equal to post
    if request.method == 'POST':

        # Validate on submit here
        if form.validate_on_submit():

            # Filter the uyser by their id
            user = User.query.filter_by(email = form.email.data ).first()
            # Debugging tools
            # print(user)

            # Check whether the password is correct
            if user:
                # Utilise password hash to hash the password so that the company is not able to see
                if check_password_hash(user.password_hash , form.password.data):
                    print('login')
                    login_user(user)

                    # Redirect to predict
                    return redirect('/predict')
                
                # If wrong password here
                else:
                    flash('Wrong password' , 'danger')
            # If user does not exist here
            else:
                flash('User does not exist' , 'danger')
        
        # Unexpected error
        else:
            flash('Error, Unable to login' , 'danger')
    
    # Return the rendered template here
    return render_template("login.html", form=form, title="Sign Up" , index = True )


# Custom methods to get stored brands in json database
def get_brands():
    # This is to open the file and loads
    with open(f'{current_directory}/brands.json', 'r') as file:
        brands = json.load(file)
    return brands


# Set the predict methods
@app.route("/predict", methods=['GET','POST'])
@login_required #login is required for this
def predict():

    # If user is not authenticated here
    if not current_user.is_authenticated:
        flash('You have not logged in yet.', 'warning')

        # Redirect them back to login
        return redirect(url_for('login'))
    
    # Set up the prediction form here
    form = PredictionForm()

    # Retrieve the brands and models here
    brands = get_brands()
    prediction = None  

    # If post request is requested
    if request.method == 'POST': 

        if form.validate_on_submit():
             
            # Setting of the data here
            brand = form.brand.data
            year = int(form.year.data)
            mileage = int(form.mileage.data)
            engine = form.engine.data
            engine_size = form.engine_size.data
            transmission = form.transmission.data
            fuel_type = form.fuel_type.data
            drivetrain = form.drivetrain.data
            min_mpg = form.min_mpg.data
            damaged = int(form.damaged.data)

            # Setting of the binary data here
            damaged2 = 'Yes' if damaged == 1 else 'No'
            turbo = int(form.turbo.data)
            turbo2 = 'Yes' if turbo == 1 else 'No'
            navigation_system =int( form.navigation_system.data)
            navigation_system2 = 'Yes' if navigation_system == 1 else 'No'
            backup_camera = int(form.backup_camera.data)
            backup_camera2 = 'Yes' if backup_camera == 1 else 'No'
            first_owner = int(form.first_owner.data)
            first_owner2 = 'Yes' if first_owner == 1 else 'No'

            # Setting of the featured engineered column here
            age = 2023 - year

            # Creating the dataframe for insertion
            df = pd.DataFrame([[brand, year, mileage, engine,engine_size,
                transmission, fuel_type, drivetrain, min_mpg,
                damaged, turbo, navigation_system, backup_camera,first_owner,age ]], columns = [
                    'brand', 'year', 'mileage', 'engine','engine_size',
                    'transmission', 'fuel_type', 'drivetrain', 'min_mpg',
                    'damaged', 'turbo', 'navigation_system', 'backup_camera','first_owner','Age'
                    ])         
            
            # Getting the current user
            userid = current_user.id  
            result = ai_model.predict(df) # Mossl prediction
            
            # Setting the time for Singapore user
            utc = datetime.utcnow()
            TimeSgt = pytz.timezone('Asia/Singapore')
            SGTTime = utc.replace(tzinfo=pytz.utc).astimezone(TimeSgt)
            
            # Setting the new entry here
            new_entry = Prediction(userid=userid,brand=brand,
                year=year,
                mileage=mileage,
                engine = engine,
                engine_size = engine_size,
                transmission = transmission,
                fuel_type = fuel_type,
                drivetrain = drivetrain,
                min_mpg = min_mpg,
                damaged = damaged2,
                turbo = turbo2,
                navigation_system = navigation_system2,
                backup_camera = backup_camera2,
                first_owner = first_owner2,
                age = age,
                prediction=int(result[0]),
                predicted_on= SGTTime)
            
            # Adding the new entry
            add_entry(new_entry)
            prediction = int(result[0])  # Set the prediction variable
        
        # If there is any error in the webpage
        else: 
            flash("Error, cannot proceed with prediction", "danger") 

    # Return the render template here
    return render_template("index.html", form=form, title='Enter Car Prediction Parameters', 
                           brands=brands, current_year=datetime.now().year, prediction=prediction)

# Setting the add entry methods here
def add_entry(new_entry):
    try:
        db.session.add(new_entry)
        db.session.commit()
        return new_entry.id
    except Exception as error:
        print(error)
        db.session.rollback()
        flash(error,"danger")

# Setting the remove entry methods here
def remove_entry(id):
    try:
        entry = Prediction.query.get_or_404(id)
        db.session.delete(entry)
        db.session.commit()
        flash("Entry removed successfully", "success")
    except Exception as error:
        db.session.rollback()
        flash(str(error), "danger")

# Setting the get entry here
def get_entry(id):
    try:
        result = db.get_or_404(Prediction, id)
        return result
    except Exception as error:
        db.session.rollback()
        flash(str(error), "danger")
        return 0

# Set the methods for getting the history of the user prediction
@app.route('/history', methods=['GET', 'POST'])
@login_required
def history():
    
    # Check whether user is login
    if not current_user.is_authenticated:
        flash('You have not logged in yet.', 'warning')
        return redirect(url_for('login'))
    
    # If the methods is post
    if request.method == 'POST':
        id_to_delete = request.form.get('id_to_delete')
        if id_to_delete:
            remove_entry(id_to_delete)
            return redirect(url_for('history'))

    # Set the sort by here
    page = request.args.get('page', 1, type=int)
    sortBy = request.args.get('sort', 'id', type=str)
    sortOrder = request.args.get('order', 'desc', type=str)

    # If it is decreasing here set the sql alchemy to it
    if sortOrder == 'desc':
        orderFunc = desc
    else:
        orderFunc = asc
    userid = current_user.id  
    # Get the predictions base on the condition here
    predictions = Prediction.query.filter(Prediction.userid == userid)\
                              .order_by(orderFunc(getattr(Prediction, sortBy)))\
                              .paginate(page=page, per_page=5, error_out=False)
    
    # set the next url and previous url here
    next_url = url_for('history', page=predictions.next_num, sort=sortBy, order=sortOrder) if predictions.has_next else None
    prev_url = url_for('history', page=predictions.prev_num, sort=sortBy, order=sortOrder) if predictions.has_prev else None

    # This is to debug
    # print(f"Next URL: {next_url}, Prev URL: {prev_url}")

    # Return the render tempalte here
    return render_template('history.html', predictions=predictions, next_url=next_url, prev_url=prev_url)


# Setting the logout options here
@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect('/login')


## Restful api

# Set the methods for reset password
@app.route('/reset_password', methods=['GET', 'POST'])
def reset_password():

    # Start the reset password form
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash('User not found!', 'danger')
            return redirect(url_for('login'))
        
        # Settubg the new password
        user.set_password(form.new_pw.data)
        db.session.commit()
        flash('Password has been reset!', 'success')
        return redirect(url_for('login'))

    # Return render template
    return render_template('reset_password.html', form=form)

# Set the methods to get the profile
@app.route('/profile')
def profile():
    userid = current_user.id  
    user = User.query.get_or_404(userid)
    return render_template('profile.html', user=user)

# Set the change password by username
@app.route('/change-password/<username>', methods=['GET', 'POST'])
def change_password(username):
    user = User.query.filter_by(username=username).first_or_404()
    form = ChangePasswordForm()
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.session.commit()
        flash('Your password has been updated!', 'success')
        return redirect(url_for('profile', username=username))
    
    # Return the rendered template
    return render_template('change_password.html', form=form, username=username)


## Restful api


# Set the methods for adding
@app.route("/api/add/<int:id>", methods=['POST']) 
@login_required
def api_add(id): 
    try:
        print(session.get('user_id'))
        if session.get("user_id") != id:
            raise Forbidden("Your user id does not match up with the request.")
        data = request.get_json() 
        brand = data['brand']
        year = data['year']
        age = data['Age']
        mileage = data['mileage']
        engine = data['engine']
        engine_size = data['engine_size']
        transmission = data['transmission']
        fuel_type = data['fuel_type']
        drivetrain = data['drivetrain']
        min_mpg = data['min_mpg']
        damaged = int(data['damaged'])
        turbo = int(data['turbo'])
        navigation_system =int( data['navigation_system'])
        backup_camera = int(data['backup_camera'])
        first_owner = int(data['first_owner'])
        real = data['prediction']
        userid = id
        new_entry = Prediction(userid=id,brand=brand,
                    year=year,
                    age = age,
                    mileage=mileage,
                    engine = engine,
                    engine_size = engine_size,
                    transmission = transmission,
                    fuel_type = fuel_type,
                    drivetrain = drivetrain,
                    min_mpg = min_mpg,
                    damaged = damaged,
                    turbo = turbo,
                    navigation_system = navigation_system,
                    backup_camera = backup_camera,
                    first_owner = first_owner,
                    prediction = real,
                    predicted_on=datetime.utcnow())
        result = add_entry(new_entry) 
        print(result)
        return jsonify({'id':result})
    except KeyError as e:
        return jsonify({'Error':f'There is missing data in {e}'})

# Set the methods of getting entry

def get_entry(id):
    try:
        # Version 2
        result = db.get_or_404(Prediction, id)
        return result
    except Exception as error:
        db.session.rollback()
        flash(str(error), "danger")
        return 0

@app.route("/api/get/<int:id>", methods=['GET']) 
@login_required
def api_get(id): #retrieve the entry using id from client 
    entry = get_entry(int(id))
    print(entry)  
    data = [
        dict(
            userid= i.id,
            brand= i.brand,
            year= i.year,
            Age = i.Age,
            mileage= i.mileage,
            engine = i.engine,
            engine_size = i.engine_size,
            transmission = i.transmission,
            fuel_type = i.fuel_type,
            drivetrain = i.drivetrain,
            min_mpg = i.min_mpg,
            damaged = i.damaged,
            turbo = i.turbo,
            navigation_system = i.navigation_system,
            backup_camera = i.backup_camera,
            first_owner = i.first_owner,
            prediction = i.prediction,
            predicted_on=datetime.utcnow()
        )
        for i in entry
    ]
    result = jsonify(data) 
    print(result)
    return result   


# Set the methods for registration
class CustomDatabaseError(Exception):
    def __init__(self, message="There was a database error"):
        self.message = message
        super().__init__(self.message)

class CustomApplicationError(Exception):
    def __init__(self, message="An unexpected error occurred in the application"):
        self.message = message
        super().__init__(self.message)

@app.route("/api/register", methods=['POST']) 
def api_register():
    try:
        data = request.get_json()
        username,email = data['username'], data['email']
        password, password1 = data['password'], data['password1']
        if password != password1:
            return jsonify({'Error':f'Password not the same'}),401
        joined_at = datetime.utcnow()
        user = User(username =username, email = email, password_hash = password)
        print('here')
        id = add_entry(user)
    except IntegrityError as e:
        raise CustomDatabaseError("This email/username is already in use.") from e
    except Exception as e:
        raise CustomApplicationError("An unexpected error occurred.") from e
    return jsonify(
        {
            "id": id,
            'username':username,
            "email": email,
            "password": password1,
            "joined_at": joined_at,
        }
    ) , 201


# Set the methods for predict
@app.route("/api/predict", methods=['POST'])
@login_required
def test_predict():
    print('here')
    brands = [
        "Honda", "Cadillac", "Toyota", "Mazda", "Chevrolet", "MINI", "Mercedes-Benz",
        "Jeep", "Maserati", "Lexus", "Audi", "Porsche", "Land", "Mitsubishi",
        "Kia", "Hyundai", "Volvo", "Volkswagen", "Ford", "FIAT", "Alfa",
        "BMW", "Nissan", "Jaguar", "Suzuki"
    ]
    try: 
        data = request.get_json()
        brand = data['brand']
        year = data['year']
        age = data['Age']
        mileage = data['mileage']
        engine = data['engine']
        engine_size = data['engine_size']
        transmission = data['transmission']
        fuel_type = data['fuel_type']
        drivetrain = data['drivetrain']
        min_mpg = data['min_mpg']
        damaged = int(data['damaged'])
        turbo = int(data['turbo'])
        navigation_system =int( data['navigation_system'])
        backup_camera = int(data['backup_camera'])
        first_owner = int(data['first_owner'])
        real = data['price']
        assert isinstance(brand, str), 'Brand should be a string'
        assert isinstance(year, int) and 1900 < year <= 2023, 'Year should be a valid integer (1900-2023)'
        assert isinstance(mileage, (int, float)) and mileage >= 0, 'Mileage should be a non-negative number'
        assert isinstance(engine, str), 'Engine should be a string'
        assert isinstance(engine_size, (int, float)) and engine_size > 0, 'Engine size should be a positive number'
        assert isinstance(transmission, str), 'Transmission should be a string'
        assert isinstance(fuel_type, str), 'Fuel type should be a string'
        assert isinstance(drivetrain, str), 'Drivetrain should be a string'
        assert isinstance(min_mpg, (int, float)) and min_mpg > 0, 'Minimum MPG should be a positive number'
        assert damaged in [0, 1], 'Damaged should be 0 or 1'
        assert turbo in [0, 1], 'Turbo should be 0 or 1'
        assert navigation_system in [0, 1], 'Navigation system should be 0 or 1'
        assert backup_camera in [0, 1], 'Backup camera should be 0 or 1'
        assert first_owner in [0, 1], 'First owner should be 0 or 1'
        if real is not None:
            assert isinstance(real, (int, float)) and real > 0, 'Prices should be more than 0'

    except Exception as e:
        print(e)
        return jsonify({'Error':'Prediction did not go through'})
    df = pd.DataFrame([[brand, year, mileage, engine,engine_size,
            transmission, fuel_type, drivetrain, min_mpg,
            damaged, turbo, navigation_system, backup_camera,age, first_owner ]], columns = [
                'brand', 'year', 'mileage', 'engine','engine_size',
                'transmission', 'fuel_type', 'drivetrain', 'min_mpg',
                'damaged', 'turbo', 'navigation_system', 'backup_camera','Age','first_owner'
                ])          
    result = ai_model.predict(df)

    if real is not None:
        dif = real - result[0]
    else: dif = None
    return jsonify({
        'prediction':result[0],
        'difference':dif
    })

# Set the methods for api login
@app.route('/api/login', methods=['POST'])
def api_login():
    try: 
        data = request.get_json()
        email, password = data['email'], data['password']
        user = User.query.filter_by(email=email).first()
        print(user)
        if user is None:
            return jsonify({"error": "User not found"}), 404
        if user.password_hash != password:
            return jsonify({'error':'Wrong Password'}), 403
        session["user_id"] = user.id
        return jsonify(
            {
                "id": user.id,
                "email": email,
                "password": password,
                "message": "Login successful."
            }
        ), 200
    except Exception as e:
        print(e)
        return jsonify({"error": "Database error occurred."}), 500
    except Exception as e:
        print(e)
        return jsonify({"error": "An unexpected error occurred."}), 500



