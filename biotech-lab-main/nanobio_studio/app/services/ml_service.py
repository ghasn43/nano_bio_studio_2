"""
ML Service Layer

High-level orchestration for ML operations including dataset building,
training, evaluation, and ranking.
"""

import logging
from typing import Dict, List, Optional
import uuid
from datetime import datetime
import pandas as pd
import os

# Add file handler to capture all training logs
_logger = logging.getLogger(__name__)
_log_file = "training_debug.log"
_file_handler = logging.FileHandler(_log_file, mode='a')
_file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
_logger.addHandler(_file_handler)
_logger.setLevel(logging.DEBUG)
from ..ml.dataset_builder import DatasetBuilder
from ..ml.feature_builder import FeatureBuilder
from ..ml.preprocess import PreprocessingPipeline
from ..ml.train import ModelTrainer
from ..ml.predict import ModelPredictor
from ..ml.ranker import CandidateRanker
from ..ml.persistence import ModelPersistence
from ..ml.schemas import (
    MLTaskConfig,
    DatasetBuildRequest,
    TrainRequest,
    TrainResponse,
    RankingRequest,
)
from ..db.database import get_db
from ..db.models import TrainedModel
from ..db.database import ModelRepository


logger = logging.getLogger(__name__)


class MLService:
    """
    High-level ML service coordinating all ML operations.
    """

    def __init__(self, models_dir: str = "models_store"):
        self.dataset_builder = DatasetBuilder()
        self.feature_builder = FeatureBuilder()
        self.trainer = ModelTrainer()
        self.persistence = ModelPersistence(models_dir=models_dir)

    def build_dataset(
        self,
        records: pd.DataFrame,
        request: DatasetBuildRequest,
    ) -> Dict:
        """
        Build a training dataset from records.
        
        Args:
            records: Raw formulation/assay records
            request: DatasetBuildRequest configuration
            
        Returns:
            Complete dataset dict
        """
        
        config = request.task_config
        
        dataset = self.dataset_builder.build_dataset(
            records=records,
            task_name=config.task_name,
            target_variable=config.target_variable,
            test_split=config.test_split,
            random_state=config.random_state,
            include_metadata=request.include_metadata,
            handle_missing=request.handle_missing,
            filter_assay_type=config.filter_assay_type,
            filter_payload_type=config.filter_payload_type,
            filter_target=config.filter_target,
            exclude_features=config.exclude_features,
        )
        
        logger.info(f"Built dataset for task '{config.task_name}'")
        return dataset

    def train_models(
        self,
        records: pd.DataFrame,
        request: TrainRequest,
    ) -> TrainResponse:
        """
        Full training pipeline: build dataset, preprocess, train, evaluate.
        
        Args:
            records: Raw formulation/assay records
            request: TrainRequest with configuration
            
        Returns:
            TrainResponse with best model and metrics
        """
        
        logger.info("="*80)
        logger.info("🚀 TRAIN_MODELS: STARTING FULL TRAINING PIPELINE")
        logger.info("="*80)
        
        config = request.dataset_build_request.task_config
        logger.info(f"📋 TRAIN_MODELS: Task config loaded: task={config.task_name}")
        
        # Build dataset
        logger.info(f"🔨 TRAIN_MODELS: Building dataset for task '{config.task_name}'...")
        dataset = self.build_dataset(records, request.dataset_build_request)
        logger.info(f"✅ TRAIN_MODELS: Dataset built - {dataset['n_samples']} samples, {dataset['n_features']} features")
        
        # Preprocessing
        logger.info("🔧 TRAIN_MODELS: Starting preprocessing...")
        preprocessing_pipeline = PreprocessingPipeline(
            numeric_features=dataset['numeric_features'],
            categorical_features=dataset['categorical_features'],
            scale_numeric=True,
            scaler_type="standard",
        )
        logger.info("🔧 TRAIN_MODELS: Preprocessing pipeline created, fitting on training data...")
        
        X_train_transformed = preprocessing_pipeline.fit_transform(dataset['X_train'])
        logger.info(f"✅ TRAIN_MODELS: Training data preprocessed (shape: {X_train_transformed.shape})")
        
        X_valid_transformed = preprocessing_pipeline.transform(dataset['X_valid'])
        logger.info(f"✅ TRAIN_MODELS: Validation data preprocessed (shape: {X_valid_transformed.shape})")
        
        y_train = dataset['y_train'].values
        y_valid = dataset['y_valid'].values
        logger.info(f"✅ TRAIN_MODELS: Target variables extracted")
        
        # Train models - determine task type from task_type value
        logger.info(f"🤖 TRAIN_MODELS: Determining task type from '{config.task_type.value}'...")
        is_regression = "predict_" in config.task_type.value
        is_classification = "classify_" in config.task_type.value
        logger.info(f"🤖 TRAIN_MODELS: is_regression={is_regression}, is_classification={is_classification}")
        
        if is_regression:
            logger.info(f"🤖 TRAIN_MODELS: Starting regression training with models: {config.model_types}")
            results = self.trainer.train_regression_models(
                X_train_transformed, y_train,
                X_valid_transformed, y_valid,
                config.model_types,
            )
            logger.info(f"✅ TRAIN_MODELS: Regression training completed with {len(results)} models")
        elif is_classification:
            logger.info(f"🤖 TRAIN_MODELS: Starting classification training with models: {config.model_types}")
            results = self.trainer.train_classification_models(
                X_train_transformed, y_train,
                X_valid_transformed, y_valid,
                config.model_types,
            )
            logger.info(f"✅ TRAIN_MODELS: Classification training completed with {len(results)} models")
        else:
            logger.error(f"❌ TRAIN_MODELS: Unknown task type: {config.task_type}")
            raise ValueError(f"Unknown task type: {config.task_type}")
        
        # Select best model
        logger.info("🏆 TRAIN_MODELS: Selecting best model from results...")
        best_model_type, best_model = self.trainer.select_best_model(
            results,
            config.task_type,
        )
        logger.info(f"🏆 TRAIN_MODELS: Best model selected: {best_model_type}")
        
        # Save if requested
        artifact_path = None
        if request.save_artifacts:
            logger.info("💾 TRAIN_MODELS: Building evaluation summary for artifact save...")
            artifact_name = request.artifact_name or config.task_name
            
            evaluation_summary = {
                model_type: {
                    'train': train_metrics,
                    'validation': valid_metrics,
                }
                for model_type, (_, train_metrics, valid_metrics) in results.items()
            }
            logger.info(f"💾 TRAIN_MODELS: Saving model bundle to disk (artifact_name={artifact_name})...")
            
            artifact_path = self.persistence.save_model_bundle(
                model=best_model,
                preprocessing_pipeline=preprocessing_pipeline,
                task_config=config.dict(),
                evaluation_summary=evaluation_summary,
                feature_builder=self.feature_builder,
                metadata={'artifact_name': artifact_name},
            )
            logger.info(f"✅ TRAIN_MODELS: Model artifacts saved to: {artifact_path}")
        
        # Build response
        logger.info("📦 TRAIN_MODELS: Building response object...")
        evaluation_summaries = [
            self._create_evaluation_summary(model_type, train_metrics, valid_metrics, best_model_type)
            for model_type, (_, train_metrics, valid_metrics) in results.items()
        ]
        logger.info(f"📦 TRAIN_MODELS: Created evaluation summaries for {len(evaluation_summaries)} models")
        
        logger.info("📦 TRAIN_MODELS: Creating final TrainResponse...")
        response = TrainResponse(
            task_name=config.task_name,
            best_model_type=best_model_type,
            n_samples=dataset['n_samples'],
            n_features=dataset['n_features'],
            evaluation_summaries=evaluation_summaries,
            artifact_path=artifact_path,
        )
        logger.info("✅ TRAIN_MODELS: TrainResponse created successfully")
        # Save training record to database for persistence
        logger.info("="*80)
        logger.info("💾 TRAINING SAVE: ABOUT TO SAVE TRAINING RECORD TO DATABASE...")
        logger.info("="*80)
        
        try:
            logger.info("💾 TRAINING SAVE: Getting database instance...")
            db = get_db()
            session = db.get_session()
            model_repo = ModelRepository(session)
            
            # Check if a model with this task_name already exists
            logger.info(f"💾 Checking for existing model with task_name='{config.task_name}'...")
            existing_model = model_repo.get_by_task(config.task_name)
            
            if existing_model:
                # Instead of updating, create a new record with a versioned name
                logger.info(f"⚠️ Model with task_name '{config.task_name}' already exists. Creating new version...")
                
                # Find the next available version number
                version = 1
                base_name = config.task_name
                
                # Remove any existing version suffix if present
                if '_v' in base_name and base_name.split('_v')[-1].isdigit():
                    base_name = '_v'.join(base_name.split('_v')[:-1])
                
                # Find the next available version number
                while True:
                    versioned_name = f"{base_name}_v{version}"
                    if not model_repo.get_by_task(versioned_name):
                        break
                    version += 1
                
                # Use versioned name for the new model
                task_name_to_use = versioned_name
                logger.info(f"📝 Using versioned task name: {task_name_to_use}")
            else:
                # First version - use original name
                task_name_to_use = config.task_name
                version = 1
                logger.info(f"📝 Using original task name: {task_name_to_use}")
            
            # Get best model metrics
            logger.info("💾 Extracting best model metrics from evaluation summaries...")
            best_train_metrics = None
            best_valid_metrics = None
            for summary in evaluation_summaries:
                if summary.best_model:
                    best_train_metrics = summary.train_metrics.model_dump()
                    best_valid_metrics = summary.validation_metrics.model_dump()
                    logger.info(f"✅ Best model metrics found: train_r2={best_train_metrics.get('r2')}, valid_r2={best_valid_metrics.get('r2')}")
                    break
            
            if best_train_metrics is None:
                logger.warning(f"⚠️ No best_model summary found")
            
            # Create new TrainedModel record (always create new, never update)
            model_id = str(uuid.uuid4())
            trained_model = TrainedModel(
                id=model_id,
                task_name=task_name_to_use,  # Use versioned name if needed
                model_type=str(best_model_type),
                task_type=str(config.task_type),
                target_variable=config.target_variable,
                created_at=datetime.utcnow(),
                n_training_samples=dataset['n_samples'],
                n_features=dataset['n_features'],
                train_score=best_train_metrics.get('r2') if best_train_metrics else None,
                validation_score=best_valid_metrics.get('r2') if best_valid_metrics else None,
                model_path=artifact_path or '',
                preprocessing_path=None,
                task_config=config.model_dump() if hasattr(config, 'model_dump') else config.dict(),
                evaluation_summary={
                    'train': best_train_metrics,
                    'validation': best_valid_metrics,
                    'version': version,
                    'original_task': config.task_name if version > 1 else None,
                },
                metadata_json={
                    'artifact_name': request.artifact_name,
                    'version': version,
                    'training_timestamp': datetime.utcnow().isoformat(),
                    'model_types_trained': config.model_types,
                },
            )
            
            logger.info(f"✅ Created TrainedModel object with task_name: {task_name_to_use} (version {version})")
            
            # Save to database
            saved_model = model_repo.create(trained_model)
            logger.info(f"✅ Model saved successfully with ID: {model_id}")
            
            # Verify the save
            verify_session = db.get_session()
            try:
                from sqlalchemy import text
                result = verify_session.execute(text(f"SELECT COUNT(*) FROM trained_models WHERE id = '{model_id}'"))
                count = result.scalar()
                logger.info(f"✅ Verification - record {'EXISTS' if count > 0 else 'NOT FOUND'} in database")
            except Exception as verify_err:
                logger.warning(f"⚠️ Could not verify saved record: {verify_err}")
            finally:
                verify_session.close()
            
            session.close()
            logger.info(f"✅ Training record successfully saved: {task_name_to_use} (ID: {model_id})")
            logger.info("="*80)
            
        except Exception as e:
            logger.error("="*80)
            logger.error(f"❌ Exception during database save: {str(e)}", exc_info=True)
            logger.error("="*80)
            # Write exception to file for debugging
            with open("training_exception.log", "a") as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Exception at: {datetime.utcnow()}\n")
                f.write(f"Task: {config.task_name}\n")
                f.write(f"Error: {str(e)}\n")
                import traceback
                f.write(traceback.format_exc())
                f.write(f"\n{'='*80}\n")
            if 'session' in locals():
                session.rollback()
                session.close()
            logger.warning("⚠️ Training completed but database save failed. Check logs for details.")
        
        logger.info("="*80)
        logger.info(f"✅ 🎉 TRAINING COMPLETE for '{config.task_name}'!")
        
        # Write completion marker to file for debugging
        with open("training_completion.log", "a") as f:
            f.write(f"{datetime.utcnow().isoformat()} - Training completed: {config.task_name}\n")
        logger.info(f"✅ Response object created with {len(evaluation_summaries)} model evaluation summaries")
        logger.info("="*80)
        
        return response

    def _create_evaluation_summary(self, model_type, train_metrics, valid_metrics, best_model_type):
        """Helper to create evaluation summary"""
        from ..ml.schemas import EvaluationSummary, MetricDict
        
        return EvaluationSummary(
            model_type=model_type,
            train_metrics=MetricDict(**train_metrics),
            validation_metrics=MetricDict(**valid_metrics),
            best_model=model_type == best_model_type,
        )


class RankingService:
    """
    Service for ranking candidate formulations.
    """

    def __init__(self, models_dir: str = "models_store"):
        self.persistence = ModelPersistence(models_dir=models_dir)

    def rank_candidates(
        self,
        candidates: List[Dict],
        request: RankingRequest,
    ) -> List[Dict]:
        """
        Rank candidate formulations.
        
        Args:
            candidates: List of candidate formulation dicts
            request: RankingRequest with criteria
            
        Returns:
            List of ranking results
        """
        
        ranker = CandidateRanker()
        
        results = ranker.rank_formulations(candidates, request)
        
        return [result.dict() for result in results]

    def get_available_tasks(self) -> List[Dict]:
        """Get available trained models/tasks"""
        models = self.persistence.list_available_models()
        return models
