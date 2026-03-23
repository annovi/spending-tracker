from sqlalchemy import Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .enums import CategoryType


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    type: Mapped[CategoryType] = mapped_column(Enum(CategoryType), nullable=False)
    color: Mapped[str] = mapped_column(String(7), default="#64748b")
    icon: Mapped[str | None] = mapped_column(String(50), nullable=True)

    transactions = relationship("Transaction", back_populates="category")
