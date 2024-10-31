from werkzeug.security import generate_password_hash

from db import db
from models import UserModel


class UserManager:
    @staticmethod
    def create_staff_user(user_data):
        user_data['password'] = generate_password_hash(user_data['password'], method='pbkdf2:sha256')
        user = UserModel(**user_data)
        db.session.add(user)
        db.session.flush()
