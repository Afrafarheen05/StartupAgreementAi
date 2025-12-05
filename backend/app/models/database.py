"""
Comprehensive Database Models for All Features
SQLAlchemy ORM with SQLite/PostgreSQL support
"""
from sqlalchemy import Column, Integer, String, Text, Float, DateTime, JSON, Boolean, ForeignKey, Enum, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import enum
import os

Base = declarative_base()


# ==================== ENUMS ====================
class RiskLevel(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class UserRole(enum.Enum):
    FOUNDER = "founder"
    CO_FOUNDER = "co_founder"
    LAWYER = "lawyer"
    ADVISOR = "advisor"
    INVESTOR = "investor"


class ComplianceStatus(enum.Enum):
    COMPLIANT = "compliant"
    VIOLATION = "violation"
    WARNING = "warning"
    NEEDS_REVIEW = "needs_review"


# ==================== USER & TEAM MODELS ====================
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="founder")
    company_name = Column(String(255))
    startup_type = Column(String(50), default="SaaS")
    profile_picture = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    workspaces = relationship("WorkspaceMember", back_populates="user")
    documents = relationship("Document", back_populates="owner", foreign_keys="Document.owner_id")
    comments = relationship("Comment", back_populates="author", foreign_keys="Comment.author_id")
    negotiations = relationship("NegotiationSession", back_populates="user")


class Workspace(Base):
    __tablename__ = "workspaces"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    settings = Column(JSON)
    
    members = relationship("WorkspaceMember", back_populates="workspace")
    documents = relationship("Document", back_populates="workspace")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    
    id = Column(Integer, primary_key=True, index=True)
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    role = Column(String(50), default="member")
    permissions = Column(JSON)
    joined_at = Column(DateTime, default=datetime.utcnow)
    
    workspace = relationship("Workspace", back_populates="members")
    user = relationship("User", back_populates="workspaces")


# ==================== DOCUMENT & VERSION MODELS ====================
class Document(Base):
    __tablename__ = "documents"
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255))
    file_path = Column(String(500), nullable=False)
    file_type = Column(String(10))
    file_size = Column(Integer)
    
    owner_id = Column(Integer, ForeignKey("users.id"))
    workspace_id = Column(Integer, ForeignKey("workspaces.id"))
    
    startup_type = Column(String(50), default="SaaS")
    overall_risk_score = Column(Float)
    risk_level = Column(String(20))
    total_clauses = Column(Integer, default=0)
    high_risk_clauses = Column(Integer, default=0)
    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime)
    last_modified = Column(DateTime)
    is_template = Column(Boolean, default=False)
    tags = Column(JSON)
    
    owner = relationship("User", back_populates="documents", foreign_keys=[owner_id])
    workspace = relationship("Workspace", back_populates="documents")
    clauses = relationship("Clause", back_populates="document", cascade="all, delete-orphan")
    versions = relationship("DocumentVersion", back_populates="document", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="document")
    comparisons = relationship("ComparisonDocument", back_populates="document")
    compliance_checks = relationship("ComplianceCheck", back_populates="document")


class DocumentVersion(Base):
    __tablename__ = "document_versions"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    version_number = Column(Integer, nullable=False)
    file_path = Column(String(500), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(Integer, ForeignKey("users.id"))
    change_summary = Column(Text)
    risk_score = Column(Float)
    risk_delta = Column(Float)
    
    changes = Column(JSON)
    clauses_added = Column(Integer, default=0)
    clauses_removed = Column(Integer, default=0)
    clauses_modified = Column(Integer, default=0)
    
    document = relationship("Document", back_populates="versions")


class Clause(Base):
    __tablename__ = "clauses"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    
    clause_type = Column(String(100), nullable=False)
    clause_text = Column(Text, nullable=False)
    page_number = Column(Integer)
    position = Column(Integer)
    
    risk_level = Column(String(20), nullable=False)
    risk_score = Column(Float, nullable=False)
    explanation = Column(Text)
    
    recommendation = Column(Text)
    suggested_replacement = Column(Text)
    negotiation_priority = Column(Integer, default=0)
    
    market_percentile = Column(Float)
    is_standard = Column(Boolean, default=False)
    
    extracted_at = Column(DateTime, default=datetime.utcnow)
    
    document = relationship("Document", back_populates="clauses")
    comments = relationship("Comment", back_populates="clause")


# ==================== COMPARISON ENGINE MODELS ====================
class Comparison(Base):
    __tablename__ = "comparisons"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    
    winner_document_id = Column(Integer, ForeignKey("documents.id"))
    comparison_summary = Column(JSON)
    total_score = Column(JSON)
    
    documents = relationship("ComparisonDocument", back_populates="comparison")


class ComparisonDocument(Base):
    __tablename__ = "comparison_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    comparison_id = Column(Integer, ForeignKey("comparisons.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    position = Column(Integer)
    
    comparison = relationship("Comparison", back_populates="documents")
    document = relationship("Document", back_populates="comparisons")


# ==================== NEGOTIATION SIMULATOR MODELS ====================
class NegotiationSession(Base):
    __tablename__ = "negotiation_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    document_id = Column(Integer, ForeignKey("documents.id"))
    clause_id = Column(Integer, ForeignKey("clauses.id"))
    
    session_name = Column(String(255))
    investor_profile = Column(String(50))
    funding_stage = Column(String(50))
    
    status = Column(String(50), default="in_progress")
    current_round = Column(Integer, default=1)
    max_rounds = Column(Integer, default=5)
    
    outcome = Column(String(50))
    success_probability = Column(Float)
    final_terms = Column(Text)
    lessons_learned = Column(JSON)
    
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    
    user = relationship("User", back_populates="negotiations")
    moves = relationship("NegotiationMove", back_populates="session")


class NegotiationMove(Base):
    __tablename__ = "negotiation_moves"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("negotiation_sessions.id"))
    round_number = Column(Integer, nullable=False)
    
    actor = Column(String(20))
    move_type = Column(String(50))
    proposal = Column(Text)
    reasoning = Column(Text)
    
    move_quality = Column(Float)
    predicted_response = Column(Text)
    alternative_moves = Column(JSON)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("NegotiationSession", back_populates="moves")


# ==================== COMPLIANCE CHECKER MODELS ====================
class ComplianceCheck(Base):
    __tablename__ = "compliance_checks"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    
    jurisdiction = Column(String(50), nullable=False)
    framework = Column(String(100))
    
    status = Column(String(50), nullable=False)
    compliance_score = Column(Float)
    violations = Column(JSON)
    warnings = Column(JSON)
    recommendations = Column(JSON)
    
    missing_clauses = Column(JSON)
    required_modifications = Column(JSON)
    
    checked_at = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime)
    
    document = relationship("Document", back_populates="compliance_checks")


class ComplianceRule(Base):
    __tablename__ = "compliance_rules"
    
    id = Column(Integer, primary_key=True, index=True)
    jurisdiction = Column(String(50), nullable=False)
    framework = Column(String(100))
    rule_code = Column(String(50), unique=True)
    
    rule_name = Column(String(255), nullable=False)
    description = Column(Text)
    severity = Column(String(20))
    
    keywords = Column(JSON)
    patterns = Column(JSON)
    required_clause = Column(Boolean, default=False)
    
    fix_template = Column(Text)
    explanation = Column(Text)
    
    effective_date = Column(DateTime)
    updated_at = Column(DateTime)
    is_active = Column(Boolean, default=True)


# ==================== BENCHMARK DATABASE MODELS ====================
class BenchmarkData(Base):
    __tablename__ = "benchmark_data"
    
    id = Column(Integer, primary_key=True, index=True)
    
    agreement_type = Column(String(100))
    industry = Column(String(100))
    funding_stage = Column(String(50))
    geography = Column(String(50))
    
    clause_type = Column(String(100), nullable=False)
    clause_value = Column(Text)
    
    percentile_25 = Column(Float)
    percentile_50 = Column(Float)
    percentile_75 = Column(Float)
    average = Column(Float)
    
    frequency = Column(Float)
    negotiation_success_rate = Column(Float)
    founder_friendly_score = Column(Float)
    
    sample_size = Column(Integer)
    year = Column(Integer)
    quarter = Column(Integer)
    data_source = Column(String(255))
    added_at = Column(DateTime, default=datetime.utcnow)


# ==================== COLLABORATION MODELS ====================
class Comment(Base):
    __tablename__ = "comments"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    clause_id = Column(Integer, ForeignKey("clauses.id"), nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"))
    parent_id = Column(Integer, ForeignKey("comments.id"), nullable=True)
    
    content = Column(Text, nullable=False)
    mentions = Column(JSON)
    
    is_resolved = Column(Boolean, default=False)
    resolved_by = Column(Integer, ForeignKey("users.id"), nullable=True)
    resolved_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime)
    
    document = relationship("Document", back_populates="comments")
    clause = relationship("Clause", back_populates="comments")
    author = relationship("User", back_populates="comments", foreign_keys=[author_id])


class Approval(Base):
    __tablename__ = "approvals"
    
    id = Column(Integer, primary_key=True, index=True)
    document_id = Column(Integer, ForeignKey("documents.id"))
    approver_id = Column(Integer, ForeignKey("users.id"))
    
    status = Column(String(50), default="pending")
    decision = Column(String(50))
    comments = Column(Text)
    conditions = Column(JSON)
    
    requested_at = Column(DateTime, default=datetime.utcnow)
    responded_at = Column(DateTime)


# ==================== TEMPLATE & GENERATION MODELS ====================
class Template(Base):
    __tablename__ = "templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    category = Column(String(100))
    
    template_content = Column(Text, nullable=False)
    variables = Column(JSON)
    default_clauses = Column(JSON)
    
    customizable_sections = Column(JSON)
    industry_specific = Column(String(100))
    jurisdiction = Column(String(50))
    
    founder_friendliness_score = Column(Float)
    usage_count = Column(Integer, default=0)
    success_rate = Column(Float)
    
    created_by = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)


class GeneratedDocument(Base):
    __tablename__ = "generated_documents"
    
    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("templates.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    
    parameters = Column(JSON)
    selected_clauses = Column(JSON)
    customizations = Column(JSON)
    
    generated_content = Column(Text)
    file_path = Column(String(500))
    
    generated_at = Column(DateTime, default=datetime.utcnow)
    was_used = Column(Boolean, default=False)


# ==================== ANALYTICS & NOTIFICATIONS ====================
class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    workspace_id = Column(Integer, ForeignKey("workspaces.id"), nullable=True)
    
    action = Column(String(100), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(Integer)
    details = Column(JSON)
    
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String(50))


class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    
    type = Column(String(50))
    title = Column(String(255))
    message = Column(Text)
    link = Column(String(500))
    
    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime)
    
    created_at = Column(DateTime, default=datetime.utcnow)


# ==================== LEGACY MODELS (For Backward Compatibility) ====================
class Analysis(Base):
    """Store document analysis results - Legacy model"""
    __tablename__ = 'analyses'
    
    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    startup_type = Column(String(50))
    upload_date = Column(DateTime, default=datetime.utcnow)
    
    overall_risk_score = Column(Float)
    overall_risk_level = Column(String(20))
    clause_count = Column(Integer)
    red_flag_count = Column(Integer)
    
    clauses = Column(JSON)
    risk_assessment = Column(JSON)
    predictions = Column(JSON)
    recommendations = Column(JSON)
    
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
    source = Column(String(100))


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
