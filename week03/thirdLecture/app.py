import enum
from datetime import datetime, timedelta

import jwt
from decouple import config
from flask import Flask, request
from flask_httpauth import HTTPTokenAuth
from flask_migrate import Migrate
from flask_restful import Api, Resource, abort
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, ValidationError, validates
from password_strength import PasswordPolicy
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.exceptions import Forbidden
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
api = Api(app)

db_user = config('DB_USER')
db_password = config('DB_PASSWORD')
db_host = config('DB_HOST')
db_port = config('DB_PORT')
db_name = config('DB_NAME')

app.config['SQLALCHEMY_DATABASE_URI'] = \
    f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

auth = HTTPTokenAuth(scheme="Bearer")


@auth.verify_token
def verify_token(token):
    try:
        return User.decode_token(token)
    except jwt.exceptions.InvalidTokenError as ex:
        abort(401)


class UserRolesEnum(enum.Enum):
    super_admin = "super admin"
    admin = "admin"
    user = "user"


def permissions_required(required_roles: list[UserRolesEnum]):
    def decorator(function):
        def decorated_function(*args, **kwargs):
            current_user = auth.current_user()
            if current_user.role not in required_roles:
                raise Forbidden()
            return function(*args, **kwargs)
        return decorated_function
    return decorator


class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(120), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_on: Mapped[datetime] = mapped_column(server_default=func.now())
    update_on: Mapped[datetime] = mapped_column(onupdate=func.now(), server_default=func.now())
    role: Mapped[UserRolesEnum] = mapped_column(
        db.Enum(UserRolesEnum),
        default=UserRolesEnum.user,
        nullable=False
    )

    def encode_token(self):
        key = config("SECRET_KEY")
        data = {
            "exp": datetime.utcnow() + timedelta(days=2),
            "sub": self.id
        }
        return jwt.encode(data, key, algorithm="HS256")

    @staticmethod
    def decode_token(token):
        key = config("SECRET_KEY")
        data = jwt.decode(token, key, algorithms=["HS256"])
        user_id = data["sub"]
        user = db.session.execute(db.select(User).filter_by(id=user_id)).scalar()
        if not user:
            raise jwt.exceptions.InvalidTokenError()
        return user


class ColorEnum(enum.Enum):
    pink = "pink"
    black = "black"
    white = "white"
    yellow = "yellow"


class SizeEnum(enum.Enum):
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"
    xl = "xl"
    xxl = "xxl"


class Clothes(db.Model):
    __tablename__ = "clothes"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    color: Mapped[ColorEnum] = mapped_column(
        db.Enum(ColorEnum),
        default=ColorEnum.white,
        nullable=False
    )
    size: Mapped[SizeEnum] = mapped_column(
        db.Enum(SizeEnum),
        default=SizeEnum.s,
        nullable=False
    )
    photo: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_on: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_on: Mapped[datetime] = mapped_column(onupdate=func.now(), server_default=func.now())


class BaseUserSchema(Schema):
    email = fields.Email(required=True)
    full_name = fields.String(required=True)

    @validates('full_name')
    def validate_full_name(self, value):
        try:
            first_name, last_name = value.split()
        except ValueError:
            raise ValidationError("You should provide first and last name.")

        if len(first_name) < 2 or len(last_name) < 2:
            raise ValidationError("Each name must contain at least two characters.")


class UserSignInSchema(BaseUserSchema):
    password = fields.String(required=True)

    policy = PasswordPolicy.from_names(
        uppercase=1,
        numbers=1,
        special=1,
        nonletters=1,
    )

    @validates('password')
    def validate_password(self, value):
        errors = self.policy.test(value)
        if errors:
            raise ValidationError("Password must have uppercase letters, numbers and special characters.")


class UserResponseSchema(BaseUserSchema):
    id = fields.Integer()


class ClothesResponseSchema(Schema):
    id = fields.Integer()
    name = fields.String(required=True)
    color = fields.Enum(enum=ColorEnum, required=True)
    size = fields.Enum(enum=SizeEnum, required=True)
    photo = fields.String(required=True)

    @validates('name')
    def validate_name(self, value):
        if len(value) < 2 or len(value) < 255:
            raise ValidationError("A piece of clothing's name must be at least 2 characters "
                                  "and not more than 255 characters long.")

    @validates('photo')
    def validate_name(self, value):
        if len(value) < 2 or len(value) < 255:
            raise ValidationError("A piece of clothing's photo must be at least 2 characters "
                                  "and not more than 255 characters long.")


class SignUpResource(Resource):
    def post(self):
        data = request.get_json()

        schema = UserSignInSchema()
        errors = schema.validate(data)
        if not errors:
            data["password"] = generate_password_hash(data['password'], method='pbkdf2:sha256')
            user = User(**data)
            db.session.add(user)
            try:
                db.session.commit()
                token = user.encode_token()
                return {"token": token}, 201
            except IntegrityError as ex:
                return {"message": "Email already exists, please sign in instead."}, 400
        return errors, 400


class UserLoginResource(Resource):
    def post(self):
        data = request.get_json()
        user = db.session.execute(db.select(User).filter_by(email=data["email"])).scalar()
        if not user:
            raise Exception("Invalid email or password.")

        result = check_password_hash(user.password, data['password'])
        if result:
            return {"token": user.encode_token()}
        raise Exception("Invalid email or password.")


class UserResource(Resource):

    @auth.login_required
    @permissions_required([UserRolesEnum.admin, UserRolesEnum.super_admin])
    def get(self, id):
        user = db.session.execute(db.select(User).filter_by(id=id)).scalar()
        if not user:
            return {"message": "Not found."}, 404
        return UserResponseSchema().dump(user)


class ClothesResource(Resource):
    @auth.login_required
    @permissions_required([UserRolesEnum.user, UserRolesEnum.admin])
    def get(self):
        clothes = db.session.execute(db.select(Clothes)).scalars()
        resp = ClothesResponseSchema().dump(clothes, many=True)
        return {"data": resp}, 200


api.add_resource(SignUpResource, '/register')
api.add_resource(UserLoginResource, '/login')
api.add_resource(UserResource, '/users/<int:id>')
api.add_resource(ClothesResource, '/clothes')
