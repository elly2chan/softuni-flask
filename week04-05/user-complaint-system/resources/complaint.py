from flask import request
from flask_restful import Resource

from managers.auth import auth
from managers.complainer import ComplainerManager
from models import RoleType
from schemas.request.complaint import RequestComplaintSchema
from schemas.response.complaint import ResponseComplaintSchema
from utils.decorators import permission_required, validate_schema


class ComplaintListCreate(Resource):
    @auth.login_required
    @validate_schema(RequestComplaintSchema)
    def get(self):
        user = auth.current_user()
        complaints = ComplainerManager.get_claims(user)
        return ResponseComplaintSchema().dump(complaints, many=True)

    @auth.login_required
    @permission_required(RoleType.complainer)
    @validate_schema(RequestComplaintSchema)
    def post(self):
        user = auth.current_user()
        data = request.get_json()
        complaint = ComplainerManager.create(user, data)
        return ResponseComplaintSchema().dump(complaint), 201


class ComplaintApprove(Resource):
    @auth.login_required
    @permission_required(RoleType.approver)
    def put(self, complaint_id):
        ComplainerManager.approve(complaint_id)
        return 204


class ComplaintReject(Resource):
    @auth.login_required
    @permission_required(RoleType.approver)
    def put(self, complaint_id):
        ComplainerManager.reject(complaint_id)
        return 204
