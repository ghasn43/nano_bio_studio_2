"""
ML Service Layer

High-level orchestration for ML operations including dataset building,
training, evaluation, and ranking.
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
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
        
        config = request.dataset_build_request.task_config
        
        # Build dataset
        dataset = self.build_dataset(records, request.dataset_build_request)
        
        logger.info(f"Training models for task '{config.task_name}'...")
        
        # Preprocessing
        preprocessing_pipeline = PreprocessingPipeline(
            numeric_features=dataset['numeric_features'],
            categorical_features=dataset['categorical_features'],
            scale_numeric=True,
            scaler_type="standard",
        )
        
        X_train_transformed = preprocessing_pipeline.fit_transform(dataset['X_train'])
        X_valid_transformed = preprocessing_pipeline.transform(dataset['X_valid'])
        
        y_train = dataset['y_train'].values
        y_valid = dataset['y_valid'].values
        
        # Train models - determine task type from task_type value
        is_regression = "predict_" in config.task_type.value
        is_classification = "classify_" in config.task_type.value
        
        if is_regression:
            results = self.trainer.train_regression_models(
                X_train_transformed, y_train,
                X_valid_transformed, y_valid,
                config.model_types,
            )
        elif is_classification:
            results = self.trainer.train_classification_models(
                X_train_transformed, y_train,
                X_valid_transformed, y_valid,
                config.model_types,
            )
        else:
            raise ValueError(f"Unknown task type: {config.task_type}")
        
        # Select best model
        best_model_type, best_model = self.trainer.select_best_model(
            results,
            config.task_type,
        )
        
        # Save if requested
        artifact_path = None
        if request.save_artifacts:
            artifact_name = request.artifact_name or config.task_name
            
            evaluation_summary = {
                model_type: {
                    'train': train_metrics,
                    'validation': valid_metrics,
                }
                for model_type, (_, train_metrics, valid_metrics) in results.items()
            }
            
            artifact_path = self.persistence.save_model_bundle(
                model=best_model,
                preprocessing_pipeline=preprocessing_pipeline,
                task_config=config.dict(),
                evaluation_summary=evaluation_summary,
                feature_builder=self.feature_builder,
                metadata={'artifact_name': artifact_name},
            )
        
        # Build response
        evaluation_summaries = [
            self._create_evaluation_summary(model_type, train_metrics, valid_metrics, best_model_type)
            for model_type, (_, train_metrics, valid_metrics) in results.items()
        ]
        
        response = TrainResponse(
            task_name=config.task_name,
            best_model_type=best_model_type,
            n_samples=dataset['n_samples'],
            n_features=dataset['n_features'],
            evaluation_summaries=evaluation_summaries,
            artifact_path=artifact_path,
        )
        
        logger.info(f"Training complete for '{config.task_name}'")
        return response

    def _create_evaluation_summary(self, model_type, train_metrics, valid_metrics, best_model_type):
        """Helper to create evaluation summary"""
        from .schemas import EvaluationSummary, MetricDict
        
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
