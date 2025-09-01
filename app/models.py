# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()

class SupportRequest(Base):
    __tablename__ = "support_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(100), nullable=False)
    email = Column(String(255), nullable=False)
    subject = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # AI-generated fields (optional initially)
    category = Column(String(50), nullable=True)  # Will be set by AI
    ai_summary = Column(Text, nullable=True)      # Will be set by AI
    
    # Status tracking
    processing_status = Column(String(20), default="pending")
    notification_sent = Column(String(10), default="false")
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

# Database connection
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://support_user:support_pass@localhost:5432/support_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def create_tables():
    """Create all tables"""
    Base.metadata.create_all(bind=engine)
