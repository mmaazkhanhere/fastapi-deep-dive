from sqlalchemy.orm import Session

class SessionMixin:
    """Provide instance of database session"""
    def __init__(self, session: Session) -> None:
        self.session = session

class BaseService(SessionMixin):
    """Base class for application service"""