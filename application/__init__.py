from flask import Flask
import joblib
import dill
from flask_sqlalchemy import SQLAlchemy
import os

# Get the current script's directory
current_directory = os.path.dirname(os.path.abspath(__file__))

# Iniialise the flask app
app = Flask(__name__)


# Configure the config file
app.config.from_pyfile('config.cfg')
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{current_directory}/database.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialise sql alchemy
db = SQLAlchemy()

# Create the database here
with app.app_context():
    db.init_app(app)
    from .models import Prediction, User
    db.create_all()
    db.session.commit()
    print('Created Database!') 

# Import the login manager
from flask_login import LoginManager
manager = LoginManager()
manager.init_app(app)

# Import the load from joblib to use ml file
from joblib import load

joblib_file = "./application/static/finalized_model.pkl"
ai_model = load(joblib_file)

# Import the routes
from application import routes
