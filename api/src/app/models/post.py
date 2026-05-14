from sqlalchemy import Column, String, Text, DateTime, UUID

from app.utils import generate_uuid4
from datetime import datetime
from app.services.db_services import Base
from app.models.mixins import CRUDMixin




class Post(Base, CRUDMixin):

    __tablename__ = "posts"
    id = Column(UUID(as_uuid=True), primary_key=True, default=generate_uuid4)
    slug = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False) # Stores MDX/Markdown
    data_path = Column(String, nullable=True) # Path for DuckDB/Parquet
    published_at = Column(DateTime, default=datetime.utcnow)