"""Organization model — tenant for multi-tenancy."""
from sqlalchemy import Column, String, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum

from app.models.base import Base, UUIDMixin, TimestampMixin


class OrgType(str, enum.Enum):
    HR = "hr"
    UNIVERSITY = "university"
    SCHOOL = "school"


class Organization(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    org_type = Column(SAEnum(OrgType), nullable=False)
    domain = Column(String(255), nullable=True)  # For email domain verification
    contact_email = Column(String(255), nullable=False)
    is_active = Column(String, default=True)

    # Relationships
    users = relationship("User", back_populates="organization")
    test_sessions = relationship("TestSession", back_populates="organization")
