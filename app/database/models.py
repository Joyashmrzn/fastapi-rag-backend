
from sqlalchemy import Column, Integer, String, DateTime, Date, Time
from sqlalchemy.sql import func

from app.database.connection import Base


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    file_type = Column(String(10), nullable=False)
    page_count = Column(Integer, nullable=True)
    character_count = Column(Integer, nullable=False)
    chunking_strategy = Column(String(50), nullable=False)
    chunk_count = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class InterviewBooking(Base):
    __tablename__ = "interview_bookings"

    id = Column(Integer, primary_key=True, index=True)
    candidate_name = Column(String(150), nullable=False)
    email = Column(String(255), nullable=False)
    interview_date = Column(Date, nullable=False)
    interview_time = Column(Time, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
