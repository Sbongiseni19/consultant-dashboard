from sqlalchemy import Column, Integer, String, Boolean, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class Booking(Base):
    __tablename__ = "bookings"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String, index=True)
    customer_email = Column(String, index=True)
    reason = Column(String)
    status = Column(String, default="pending")  # pending, accepted, completed
    created_at = Column(DateTime, default=datetime.utcnow)
