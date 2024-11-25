from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId
from app import mongo, login_manager

class User(UserMixin):
    def __init__(self, user_data):
        self.user_data = user_data

    def get_id(self):
        return str(self.user_data.get('_id'))

    @property
    def is_admin(self):
        return self.user_data.get('is_admin', False)

    @property
    def username(self):
        return self.user_data.get('username')

    @staticmethod
    def create_user(username, email, password, is_admin=False):
        user_data = {
            'username': username,
            'email': email,
            'password_hash': generate_password_hash(password),
            'is_admin': is_admin
        }
        result = mongo.db.users.insert_one(user_data)
        user_data['_id'] = result.inserted_id
        return User(user_data)

    @staticmethod
    def get_by_username(username):
        user_data = mongo.db.users.find_one({'username': username})
        return User(user_data) if user_data else None

    def check_password(self, password):
        return check_password_hash(self.user_data['password_hash'], password)

    @property
    def is_active(self):
        return True

    @property
    def is_authenticated(self):
        return True

    @property
    def is_anonymous(self):
        return False

@login_manager.user_loader
def load_user(user_id):
    try:
        if not ObjectId.is_valid(user_id):
            return None
        user_data = mongo.db.users.find_one({'_id': ObjectId(user_id)})
        return User(user_data) if user_data else None
    except:
        return None