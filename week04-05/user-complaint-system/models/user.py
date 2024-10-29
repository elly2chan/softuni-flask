from sqlalchemy.orm import Mapped, mapped_column

from db import db
from models.enums import RoleType


class UserModel(db.Model):
    __tablename__ = "USERS"
    id: Mapped[int] = mapped_column(primary_key=True)
    email: Mapped[str] = mapped_column(db.String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(db.String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    last_name: Mapped[str] = mapped_column(db.String(255), nullable=False)
    phone: Mapped[str] = mapped_column(db.String(20), nullable=True)
    role: Mapped[RoleType] = mapped_column(
        db.Enum(RoleType),
        default=RoleType.complainer.name,
        nullable=False
    )
    certificate: Mapped[str] = mapped_column(db.String(255), nullable=True)
