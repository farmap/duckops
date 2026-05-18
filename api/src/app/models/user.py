from sqlalchemy import Column, String, UUID
from app.utils import generate_uuid4
from app.services.db_services import Base
from app.models.mixins import CRUDMixin

class User(Base, CRUDMixin):
    __tablename__ = "users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid4)

    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    theme = Column(String, default="dark", nullable=False)
