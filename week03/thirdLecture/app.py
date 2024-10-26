import enum
from datetime import datetime
from typing import Optional

from decouple import config
from flask import Flask, request
from flask_migrate import Migrate
from flask_restful import Api, Resource
from flask_sqlalchemy import SQLAlchemy
from marshmallow import Schema, fields, validate, ValidationError, validates
from password_strength import PasswordPolicy
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Mapped, mapped_column
from werkzeug.security import generate_password_hash

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


class User(db.Model):
    __tablename__ = 'user'

    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(120), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    created_on: Mapped[datetime] = mapped_column(server_default=func.now())
    update_on: Mapped[datetime] = mapped_column(onupdate=func.now(), server_default=func.now())


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


class SignUp(Resource):
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
                response_schema = UserResponseSchema()
                response_data = response_schema.dump(user)
                return response_data, 201
            except IntegrityError as ex:
                return {"message": "Email already exists, please sign in instead."}, 400
        return errors, 400


class UserResource(Resource):

    def get(self, id):
        user = db.session.execute(db.select(User).filter_by(id=id)).scalar_one()
        if not user:
            return {"message": "Not found."}, 404
        return UserResponseSchema().dump(user)


api.add_resource(SignUp, '/register')
api.add_resource(UserResource, '/users/<int:id>/')
