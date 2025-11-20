"""
Database models
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os

Base = declarative_base()


class Analysis(Base):
    """Store document analysis results"""
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    startup_type = Column(String(50))
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    # Overall metrics
    overall_risk_score = Column(Float)
    overall_risk_level = Column(String(20))
    clause_count = Column(Integer)
    red_flag_count = Column(Integer)
    
    # Detailed results stored as JSON
    clauses = Column(JSON)  # List of extracted clauses with risk assessments
    risk_assessment = Column(JSON)  # Overall risk assessment
    predictions = Column(JSON)  # Future risk predictions
    recommendations = Column(JSON)  # Actionable recommendations
    
    # Document info
    page_count = Column(Integer)
    word_count = Column(Integer)
    file_path = Column(String(500))


class TrainingData(Base):
    """Store training data for model improvement"""
    __tablename__ = 'training_data'
    
    id = Column(Integer, primary_key=True, index=True)
    clause_text = Column(Text, nullable=False)
    clause_type = Column(String(100), nullable=False)
    risk_level = Column(String(20), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    source = Column(String(100))  # e.g., "user_feedback", "initial_dataset"


class UserFeedback(Base):
    """Store user feedback on predictions"""
    __tablename__ = 'user_feedback'
    
    id = Column(Integer, primary_key=True, index=True)
    analysis_id = Column(Integer, index=True)
    clause_type = Column(String(100))
    predicted_risk = Column(String(20))
    actual_risk = Column(String(20))
    feedback_text = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


# Database initialization
def init_db(database_url: str):
    """Initialize database and create tables"""
    engine = create_engine(database_url)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return engine, SessionLocal


def get_db_session(database_url: str):
    """Get database session"""
    _, SessionLocal = init_db(database_url)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
