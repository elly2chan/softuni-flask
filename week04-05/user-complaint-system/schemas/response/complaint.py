from marshmallow import fields
from marshmallow_enum import EnumField

from models.enums import State
from schemas.base import BaseComplaintSchema


class ResponseComplaintSchema(BaseComplaintSchema):
    id = fields.Integer(required=True)
    status = EnumField(State, by_value=True)
    created_on = fields.DateTime(required=True)