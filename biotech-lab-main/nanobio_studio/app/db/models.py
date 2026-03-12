"""
Database Models for ML Module

ORM models for persisting formulations, assays, models, and artifacts.
"""

from datetime import datetime
from sqlalchemy import Column, String, Float, Integer, DateTime, Boolean, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()


class Formulation(Base):
    """Formulation records"""
    
    __tablename__ = "formulations"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(String(1000))
    payload_type = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # JSON storage for flexible schema
    components = Column(JSON, nullable=False)
    properties = Column(JSON)
    metadata_json = Column(JSON)
    
    # Relationships
    assays = relationship("Assay", back_populates="formulation")


class Assay(Base):
    """Assay results linked to formulations"""
    
    __tablename__ = "assays"
    
    id = Column(String(36), primary_key=True)
    formulation_id = Column(String(36), ForeignKey("formulations.id"), nullable=False)
    assay_type = Column(String(100), nullable=False)
    target = Column(String(100))
    value = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # JSON for flexible assay data
    conditions = Column(JSON)
    metadata_json = Column(JSON)
    
    # Relationships
    formulation = relationship("Formulation", back_populates="assays")


class TrainedModel(Base):
    """Trained ML models"""
    
    __tablename__ = "trained_models"
    
    id = Column(String(36), primary_key=True)
    task_name = Column(String(255), nullable=False)  # Removed unique=True to allow multiple trainings per task
    model_type = Column(String(100), nullable=False)
    task_type = Column(String(50), nullable=False)
    target_variable = Column(String(100), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Model performance
    n_training_samples = Column(Integer)
    n_features = Column(Integer)
    train_score = Column(Float)
    validation_score = Column(Float)
    
    # Storage info
    model_path = Column(String(500), nullable=False)
    preprocessing_path = Column(String(500))
    
    # JSON for model config and metadata
    task_config = Column(JSON)
    evaluation_summary = Column(JSON)
    metadata_json = Column(JSON)
    
    # Relationships
    predictions = relationship("ModelPrediction", back_populates="model")


class ModelPrediction(Base):
    """Model predictions on formulations"""
    
    __tablename__ = "model_predictions"
    
    id = Column(String(36), primary_key=True)
    model_id = Column(String(36), ForeignKey("trained_models.id"), nullable=False)
    formulation_id = Column(String(36), ForeignKey("formulations.id"))
    prediction = Column(Float, nullable=False)
    confidence = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # JSON for additional prediction data
    metadata_json = Column(JSON)
    
    # Relationships
    model = relationship("TrainedModel", back_populates="predictions")


class RankingResult(Base):
    """Ranking results for candidate formulations"""
    
    __tablename__ = "ranking_results"
    
    id = Column(String(36), primary_key=True)
    ranking_session_id = Column(String(36), nullable=False)
    formulation_id = Column(String(36), ForeignKey("formulations.id"))
    rank = Column(Integer, nullable=False)
    score = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Ranking criteria and method
    ranking_criteria = Column(JSON)
    method = Column(String(100))
    
    # Relationships
    formulation = relationship("Formulation")


class Artifact(Base):
    """ML artifacts (models, preprocessors, etc.)"""
    
    __tablename__ = "artifacts"
    
    id = Column(String(36), primary_key=True)
    name = Column(String(255), nullable=False, unique=True)
    artifact_type = Column(String(100), nullable=False)  # 'model', 'preprocessor', 'dataset'
    task_name = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Storage info
    path = Column(String(500), nullable=False)
    size_bytes = Column(Integer)
    
    # Metadata
    description = Column(String(1000))
    version = Column(String(50))
    metadata_json = Column(JSON)
    
    # UI info
    is_favorite = Column(Boolean, default=False)
    tags = Column(JSON)
