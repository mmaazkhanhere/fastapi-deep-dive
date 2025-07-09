# src/db/models.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from .database import Base


class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    role = Column(String, default="learner")
    # CORRECTED: Use "Skills" (plural, matching class name)
    skills = relationship("Skills", back_populates="user")
    learning_resources = relationship("LearningResource", back_populates="user")


class LearningResource(Base):
    __tablename__ = "learning_resource"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    url = Column(String, nullable=True)
    resource_type = Column(String, nullable=False)
    difficulty = Column(Integer, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    user_id = Column(Integer, ForeignKey("user.id"))
    skill_id = Column(Integer, ForeignKey("skills.id"))

    user = relationship("User", back_populates="learning_resources")
    # This relationship also refers to "Skills" (plural)
    skill = relationship("Skills")


class Skills(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    user_id = Column(Integer, ForeignKey("user.id"))

    user = relationship("User", back_populates="skills")