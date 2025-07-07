from datetime import datetime
from enum import Enum
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy import Enum as SQLAlchemyEnum 

from .database import Base, engine

# Define your Python Enum first
class LearningResourceType(Enum):
    article = "article"
    video = 'video'
    course = 'course'
    book = 'book'

class LearningResource(Base):
    __tablename__ = "learning_resource" 

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(String, nullable=True)
    # Use SQLAlchemyEnum to map your Python Enum to a database ENUM type
    resource_type = Column(SQLAlchemyEnum(LearningResourceType), nullable=False)
    difficult = Column(Integer, default=1)
    created_at = Column(DateTime, nullable=False, default=datetime.now())


Base.metadata.create_all(engine)