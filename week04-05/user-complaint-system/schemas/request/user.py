from marshmallow import Schema, fields, validates_schema, ValidationError
from marshmallow.validate import OneOf


class UserSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True)


class RequestRegisterUserSchema(UserSchema):
    first_name = fields.String(min_length=2, max_length=20, required=True)
    last_name = fields.String(min_length=2, max_length=20, required=True)
    phone = fields.String(min_length=10, max_length=13, required=True)


class RequestLoginUserSchema(UserSchema):
    pass


class RequestRegisterStaffUserSchema(RequestRegisterUserSchema):
    role = fields.String(required=True, validate=OneOf(["admin", "approver"]))
    certificate = fields.URL()

    @validates_schema
    def validate_certificate(self, data, **kwargs):
        if data["role"] == "approver" and "certificate" not in data:
            raise ValidationError("Pass certificate of the approver", field_names=["certificate"], )


class PasswordChangeSchema(Schema):
    old_password = fields.String(required=True)
    new_password = fields.String(required=True)

    @validates_schema
    def validate_passwords(self, data, **kwargs):
        # Ensure that the old password is not the same as the new password
        if data["old_password"] == data["new_password"]:
            raise ValidationError("New password cannot be the same as the old password.",
                                  field_names=["new_password"], )
