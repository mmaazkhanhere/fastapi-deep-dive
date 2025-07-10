# src/db/models.py

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Table
from sqlalchemy.orm import relationship, Mapped, mapped_column

from .database import Base

# Association table for many-to-many between LearningResource and Skills
learning_resource_skill_association = Table(
    "learning_resource_skill_association",
    Base.metadata,
    Column("learning_resource_id", ForeignKey("learning_resource.id"), primary_key=True),
    Column("skill_id", ForeignKey("skills.id"), primary_key=True),
)

class User(Base):
    __tablename__ = "user"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    role = Column(String, default="learner")
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

    user = relationship("User", back_populates="learning_resources")
    # Many-to-many relationship with Skills through the association table
    skills = relationship(
        "Skills", secondary=learning_resource_skill_association, back_populates="learning_resources"
    )


class Skills(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, index=True, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())
    user_id = Column(Integer, ForeignKey("user.id")) # Skill can be created by a user

    user = relationship("User", back_populates="skills")
    # Many-to-many relationship with LearningResource through the association table
    learning_resources = relationship(
        "LearningResource", secondary=learning_resource_skill_association, back_populates="skills"
    )