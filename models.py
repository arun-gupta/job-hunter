from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    location = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    requirements = Column(Text)
    salary_range = Column(String(100))
    job_url = Column(String(500), nullable=False)
    posted_date = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    resumes = relationship("OptimizedResume", back_populates="job")
    referrals = relationship("Referral", back_populates="job")

class OptimizedResume(Base):
    __tablename__ = "optimized_resumes"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    original_resume_path = Column(String(500), nullable=False)
    optimized_resume_path = Column(String(500), nullable=False)
    optimization_notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    job = relationship("Job", back_populates="resumes")

class Referral(Base):
    __tablename__ = "referrals"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    name = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    company = Column(String(255), nullable=False)
    connection_level = Column(Integer, nullable=False)  # 1 for 1st, 2 for 2nd
    profile_url = Column(String(500))
    introduction_needed = Column(Boolean, default=False)
    notes = Column(Text)
    created_at = Column(DateTime, server_default=func.now())
    job = relationship("Job", back_populates="referrals") 