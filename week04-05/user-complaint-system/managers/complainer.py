from werkzeug.exceptions import BadRequest
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from managers.auth import AuthManager
from models.enums import RoleType
from models.user import UserModel


class ComplainerManager:
    @staticmethod
    def register(complainer_data):
        complainer_data["password"] = generate_password_hash(
            complainer_data["password"], method="pbkdf2:sha256"
        )
        complainer_data["role"] = RoleType.complainer.name
        user = UserModel(**complainer_data)
        try:
            db.session.add(user)
            db.session.flush()
            return AuthManager.encode_token(user)
        except Exception as ex:
            raise BadRequest(str(ex))

    @staticmethod
    def login(data):
        user = db.session.execute(db.select(UserModel).filter_by(email=data["email"])).scalar()
        if not user or not check_password_hash(user.password, data["password"]):
            raise BadRequest("Invalid username or password.")
        return AuthManager.encode_token(user)


