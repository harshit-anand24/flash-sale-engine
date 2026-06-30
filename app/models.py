from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime, timezone
from database import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(255), index=True)
    product_id = Column(String(255), index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
