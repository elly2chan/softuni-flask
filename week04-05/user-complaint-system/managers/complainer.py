from werkzeug.exceptions import BadRequest, NotFound
from werkzeug.security import generate_password_hash, check_password_hash

from db import db
from managers.auth import AuthManager
from models import ComplaintModel
from models.enums import RoleType, State
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

    @staticmethod
    def get_claims(user):
        query = db.select(ComplaintModel)
        if user.role.complainer:
            query = query.filter_by(complainer_id=user.id)
        return db.session.execute(query).scalars().all()

    @staticmethod
    def create(user, data):
        data["complainer_id"] = user.id
        complaint = ComplaintModel(**data)
        db.session.add(complaint)
        db.session.flush()

    @staticmethod
    def approve(complaint_id):
        complaint = db.session.execute(db.select(ComplaintModel).filter_by(id=complaint_id)).scalar()
        if not complaint:
            raise NotFound
        complaint.status = State.approved
        db.session.add(complaint)
        db.session.flush()

    @staticmethod
    def reject(complaint_id):
        complaint = db.session.execute(db.select(ComplaintModel).filter_by(id=complaint_id)).scalar()
        if not complaint:
            raise NotFound
        complaint.status = State.rejected
        db.session.add(complaint)
        db.session.flush()

    # db.session.execute(db.update(ComplaintModel).
    #   where(ComplaintModel.id == complaint_id).values(status=State.rejected))
