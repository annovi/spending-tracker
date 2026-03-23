from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .enums import AccountType


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    type: Mapped[AccountType] = mapped_column(Enum(AccountType), nullable=False)

    transactions = relationship("Transaction", back_populates="account")
