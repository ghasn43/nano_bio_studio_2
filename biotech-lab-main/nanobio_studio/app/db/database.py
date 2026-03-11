"""
Database Utilities

Session management, CRUD operations, and database initialization.
"""

import logging
from typing import List, Optional, Type, TypeVar
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool, NullPool
import os

from .models import Base, Formulation, Assay, TrainedModel, ModelPrediction, RankingResult, Artifact


logger = logging.getLogger(__name__)

T = TypeVar('T')


class Database:
    """Database connection and session management"""
    
    def __init__(self, db_url: Optional[str] = None):
        """
        Initialize database.
        
        Args:
            db_url: Database URL (defaults to file-based SQLite)
        """
        if db_url is None:
            # File-based SQLite for persistence
            db_url = "sqlite:///ml_module.db"
        
        # Configure engine based on database type
        is_sqlite = "sqlite" in db_url
        is_memory = "memory" in db_url
        
        engine_kwargs = {
            "connect_args": {"check_same_thread": False} if is_sqlite else {},
        }
        
        # Only use StaticPool for in-memory databases
        if is_sqlite and is_memory:
            engine_kwargs["poolclass"] = StaticPool
        elif is_sqlite:
            # For file-based SQLite, use NullPool to avoid connection pooling issues
            engine_kwargs["poolclass"] = NullPool
        
        self.engine = create_engine(db_url, **engine_kwargs)
        
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine,
        )
        
        logger.info(f"Database initialized with URL: {db_url}")
    
    def init_db(self):
        """Initialize database schema"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database schema initialized")
    
    def get_session(self) -> Session:
        """Get database session"""
        return self.SessionLocal()
    
    def close(self):
        """Close database connections"""
        self.engine.dispose()


class FormulationRepository:
    """CRUD operations for formulations"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, formulation: Formulation) -> Formulation:
        """Create new formulation"""
        self.session.add(formulation)
        self.session.commit()
        self.session.refresh(formulation)
        return formulation
    
    def get_by_id(self, formulation_id: str) -> Optional[Formulation]:
        """Get formulation by ID"""
        return self.session.query(Formulation).filter(
            Formulation.id == formulation_id
        ).first()
    
    def get_all(self) -> List[Formulation]:
        """Get all formulations"""
        return self.session.query(Formulation).all()
    
    def update(self, formulation_id: str, updates: dict) -> Optional[Formulation]:
        """Update formulation"""
        formulation = self.get_by_id(formulation_id)
        if formulation:
            for key, value in updates.items():
                if hasattr(formulation, key):
                    setattr(formulation, key, value)
            self.session.commit()
            self.session.refresh(formulation)
        return formulation
    
    def delete(self, formulation_id: str) -> bool:
        """Delete formulation"""
        formulation = self.get_by_id(formulation_id)
        if formulation:
            self.session.delete(formulation)
            self.session.commit()
            return True
        return False


class AssayRepository:
    """CRUD operations for assays"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, assay: Assay) -> Assay:
        """Create new assay"""
        self.session.add(assay)
        self.session.commit()
        self.session.refresh(assay)
        return assay
    
    def get_by_formulation(self, formulation_id: str) -> List[Assay]:
        """Get assays for formulation"""
        return self.session.query(Assay).filter(
            Assay.formulation_id == formulation_id
        ).all()
    
    def get_by_type(self, assay_type: str) -> List[Assay]:
        """Get assays by type"""
        return self.session.query(Assay).filter(
            Assay.assay_type == assay_type
        ).all()


class ModelRepository:
    """CRUD operations for trained models"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, model: TrainedModel) -> TrainedModel:
        """Create new model record"""
        self.session.add(model)
        self.session.commit()
        self.session.refresh(model)
        return model
    
    def get_by_task(self, task_name: str) -> Optional[TrainedModel]:
        """Get model by task name"""
        return self.session.query(TrainedModel).filter(
            TrainedModel.task_name == task_name
        ).first()
    
    def get_all(self) -> List[TrainedModel]:
        """Get all models"""
        models = self.session.query(TrainedModel).all()
        
        # Eagerly load all attributes to prevent lazy loading issues after session closes
        for model in models:
            # Access all attributes to force loading
            _ = (
                model.id,
                model.task_name,
                model.model_type,
                model.task_type,
                model.created_at,
                model.n_training_samples,
                model.n_features,
                model.train_score,
                model.validation_score,
                model.evaluation_summary,
            )
        
        return models
    
    def delete_by_task(self, task_name: str) -> bool:
        """Delete model by task name"""
        model = self.get_by_task(task_name)
        if model:
            self.session.delete(model)
            self.session.commit()
            return True
        return False


class RankingRepository:
    """CRUD operations for ranking results"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, result: RankingResult) -> RankingResult:
        """Create ranking result"""
        self.session.add(result)
        self.session.commit()
        self.session.refresh(result)
        return result
    
    def get_ranking_session(self, session_id: str) -> List[RankingResult]:
        """Get all results for ranking session"""
        return self.session.query(RankingResult).filter(
            RankingResult.ranking_session_id == session_id
        ).order_by(RankingResult.rank).all()


class ArtifactRepository:
    """CRUD operations for artifacts"""
    
    def __init__(self, session: Session):
        self.session = session
    
    def create(self, artifact: Artifact) -> Artifact:
        """Create artifact"""
        self.session.add(artifact)
        self.session.commit()
        self.session.refresh(artifact)
        return artifact
    
    def get_by_name(self, name: str) -> Optional[Artifact]:
        """Get artifact by name"""
        return self.session.query(Artifact).filter(
            Artifact.name == name
        ).first()
    
    def get_all_by_type(self, artifact_type: str) -> List[Artifact]:
        """Get artifacts by type"""
        return self.session.query(Artifact).filter(
            Artifact.artifact_type == artifact_type
        ).all()
    
    def mark_favorite(self, artifact_id: str, is_favorite: bool) -> Optional[Artifact]:
        """Mark artifact as favorite/unfavorite"""
        artifact = self.session.query(Artifact).filter(
            Artifact.id == artifact_id
        ).first()
        if artifact:
            artifact.is_favorite = is_favorite
            self.session.commit()
        return artifact


# Global database instance
_db: Optional[Database] = None


def get_db() -> Database:
    """Get or create global database instance"""
    global _db
    if _db is None:
        # Get database URL from environment or use absolute path default
        db_url = os.getenv("DATABASE_URL")
        
        if not db_url:
            # Create absolute path for SQLite database file
            # Navigate from nanobio_studio/app/db/database.py to biotech-lab-main
            db_file = os.path.abspath(__file__)  # Full path to database.py
            app_dir = os.path.dirname(db_file)  # nanobio_studio/app/db
            app_dir = os.path.dirname(app_dir)  # nanobio_studio/app
            nanobio_dir = os.path.dirname(app_dir)  # nanobio_studio
            root_dir = os.path.dirname(nanobio_dir)  # biotech-lab-main
            
            db_path = os.path.join(root_dir, "ml_module.db")
            
            # Convert Windows path to SQLite format (forward slashes)
            db_url = f"sqlite:///{db_path.replace(chr(92), '/')}"
            logger.info(f"Using database at: {db_path}")
        
        logger.info(f"Database URL: {db_url}")
        _db = Database(db_url)
        _db.init_db()
    return _db


def get_db_session() -> Session:
    """Get database session for dependency injection"""
    db = get_db()
    session = db.get_session()
    try:
        yield session
    finally:
        session.close()
