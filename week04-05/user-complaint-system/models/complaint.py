from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db import db
from models.enums import State
from models.user import UserModel


class ComplaintModel(db.Model):
    __tablename__ = "COMPLAINTS"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(db.String(100), nullable=False)
    description: Mapped[str] = mapped_column(db.Text, nullable=False)
    photo_url: Mapped[str] = mapped_column(db.String(255), nullable=False)
    amount: Mapped[float] = mapped_column(db.Float, nullable=False)
    created_on: Mapped[datetime] = mapped_column(db.DateTime, server_default=func.now())
    status: Mapped[State] = mapped_column(
        db.Enum(State), default=State.pending, nullable=False
    )
    complainer_id: Mapped[int] = mapped_column(db.Integer, db.ForeignKey("USERS.id"))
    complainer: Mapped["UserModel"] = relationship("UserModel")
