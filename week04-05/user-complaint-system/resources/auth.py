from flask import request
from flask_restful import Resource

from managers.auth import auth, AuthManager
from managers.complainer import ComplainerManager
from schemas.request.user import RequestRegisterUserSchema, RequestLoginUserSchema, PasswordChangeSchema
from utils.decorators import validate_schema


class RegisterComplainer(Resource):
    @validate_schema(RequestRegisterUserSchema)
    def post(self):
        data = request.get_json()
        token = ComplainerManager.register(data)
        return {"token": token}, 201


class LoginComplainer(Resource):
    @validate_schema(RequestLoginUserSchema)
    def post(self):
        data = request.get_json()
        token = ComplainerManager.login(data)
        return {"token": token}


class Password(Resource):
    @auth.login_required
    @validate_schema(PasswordChangeSchema)
    def post(self):
        data = request.get_json()
        AuthManager.change_password(data)
        return 204
