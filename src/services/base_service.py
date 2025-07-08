from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncSession

class SessionMixin: # designed to provide any class that inherits from it with a session attribute. Common pattern to inject  dependencies into a service class
    """Provide instance of database session"""
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

class BaseService(SessionMixin): #foundational class for all application service classes and will automatically have the session attribute available upon initialization
    """Base class for application service"""