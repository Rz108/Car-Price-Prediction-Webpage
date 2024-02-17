from application import db
from flask_login import UserMixin
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.orm import validates

# Creating the prediction database to store the data
class Prediction(db.Model):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    userid = db.Column(db.Integer, db.ForeignKey('User.id') , nullable = False)
    brand = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer,nullable=False)
    age = db.Column(db.Integer,nullable=False)
    mileage = db.Column(db.Float,nullable=False)
    engine = db.Column(db.String,nullable=False)
    engine_size = db.Column(db.Integer,nullable=False)
    transmission = db.Column(db.String,nullable=False)
    fuel_type = db.Column(db.String,nullable=False)
    drivetrain = db.Column(db.String,nullable=False)
    min_mpg = db.Column(db.Float,nullable=False)
    damaged = db.Column(db.String,nullable=False)
    turbo = db.Column(db.String,nullable=False)
    navigation_system = db.Column(db.String,nullable=False)
    backup_camera = db.Column(db.String,nullable=False)
    first_owner = db.Column(db.String,nullable=False)
    predicted_on = db.Column(db.DateTime, nullable=False) 
    
    prediction = db.Column(db.Float,nullable=False)
    @validates("year")
    def validate_year(self, key, year):
        assert type(year) is int, "year should be an integer"
        assert year > 0, "A room should accomodate at least one"
        return year
# Creating the user database to store info of user
class User(UserMixin, db.Model):
    __tablename__ = "User"
    id = db.Column(db.Integer, primary_key=True,autoincrement=True)
    username = db.Column(db.String(50), index=True, unique=True)
    email = db.Column(db.String(150), unique = True, index = True)
    password_hash = db.Column(db.String(150))
    joined_at = db.Column(db.DateTime(), default = datetime.utcnow, index = True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self,password):
        return check_password_hash(self.password_hash,password)

