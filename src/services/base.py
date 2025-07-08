from sqlalchemy.ext.asyncio import AsyncSession

class SessionMixin:
    def __init__(self, session: AsyncSession)-> None:
        self.session = session

class BaseService(SessionMixin):
    pass