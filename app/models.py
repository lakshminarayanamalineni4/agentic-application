from datetime import datetime

from sqlalchemy import String, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""

class User(Base):
    __tablename__ = "users1"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    name: Mapped[str] = mapped_column(String(100),nullable=False)
    mobile: Mapped[str] = mapped_column(String(15), nullable=False, unique=True, index=True)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True, index=True)
    password: Mapped[str] = mapped_column(String(250), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)