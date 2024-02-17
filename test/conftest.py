import pytest
from werkzeug.security import generate_password_hash
from datetime import datetime
import os
import sys
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from application import db
from application import app as ai_app
from application.models import User
from flask_login import LoginManager, login_user
import uuid
from sqlalchemy.exc import ResourceClosedError


ai_app.config['WTF_CSRF_ENABLED'] = False

# Loading the manager
login_manager = LoginManager()
login_manager.init_app(ai_app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Yielding the app
@pytest.fixture
def app_context():
    with ai_app.app_context():
        # Start a nested transaction
        transaction = db.session.begin_nested()
        try:
            yield db.session
        except Exception as e:
            if transaction.is_active:
                transaction.rollback()
            raise e
        finally:
            if transaction.is_active:
                transaction.rollback()
            db.session.remove()
# Client
@pytest.fixture
def client(app_context):
    yield ai_app.test_client()

# Add baseline user for testing
@pytest.fixture
def add_base_users(app_context):
    unique_id1 = uuid.uuid4()
    unique_id2 = uuid.uuid4()
    users = [
        User(username=f'James2_{unique_id1}', email=f'test{unique_id1}@example.com', 
             password_hash=generate_password_hash('password'), 
             joined_at=datetime.utcnow()),
        User(username=f'James3_{unique_id2}', email=f'test{unique_id2}@example.com', 
             password_hash=generate_password_hash('password'), 
             joined_at=datetime.utcnow())
    ]

    db.session.add_all(users)
    yield users

# Set the logged in client
@pytest.fixture
def logged_in_client(client, add_base_users):
    user = add_base_users[0]

    with client.session_transaction() as sess:
        sess['user_id'] = user.id
        
    with ai_app.test_request_context():
        login_user(user)
