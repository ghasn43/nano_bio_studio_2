"""
Predefined ML Task Profiles

Contains quick-start configurations for common ML tasks on LNP data.
These profiles auto-populate recommended settings for toxicity prediction,
particle size prediction, and other tasks.
"""

from typing import Dict, List, Optional
from dataclasses import dataclass
from .schemas import MLTaskConfig, TaskType, ModelType


@dataclass
class TaskProfile:
    """Predefined configuration for an ML task"""
    task_name: str
    task_type: TaskType
    description: str
    default_target_variable: str
    recommended_target_variables: List[str]
    model_types: List[ModelType]
    test_split: float = 0.2
    random_state: int = 42
    exclude_features: List[str] = None
    filter_assay_type: Optional[str] = None
    filter_payload_type: Optional[str] = None
    filter_target: Optional[str] = None

    def __post_init__(self):
        if self.exclude_features is None:
            self.exclude_features = []

    def to_config(self, target_variable: Optional[str] = None) -> MLTaskConfig:
        """Convert profile to MLTaskConfig"""
        return MLTaskConfig(
            task_name=self.task_name,
            task_type=self.task_type,
            target_variable=target_variable or self.default_target_variable,
            model_types=self.model_types,
            test_split=self.test_split,
            random_state=self.random_state,
            exclude_features=self.exclude_features,
            filter_assay_type=self.filter_assay_type,
            filter_payload_type=self.filter_payload_type,
            filter_target=self.filter_target,
        )


# ============================================================================
# PREDEFINED TASK PROFILES
# ============================================================================

TOXICITY_PREDICTION = TaskProfile(
    task_name="toxicity_prediction",
    task_type=TaskType.PREDICT_TOXICITY,
    description="Predict toxicity percentage for LNP formulations (0-100%)",
    default_target_variable="Toxicity_%",
    recommended_target_variables=["Toxicity_%", "Toxicity_Score"],
    model_types=[
        ModelType.RANDOM_FOREST_REGRESSION,
        ModelType.GRADIENT_BOOSTING_REGRESSION,
        ModelType.LINEAR_REGRESSION,
    ],
    test_split=0.2,
    random_state=42,
    exclude_features=["Batch_ID", "Sterility_Pass"],
)

PARTICLE_SIZE_PREDICTION = TaskProfile(
    task_name="particle_size_prediction",
    task_type=TaskType.PREDICT_PARTICLE_SIZE,
    description="Predict particle size in nanometers for LNP formulations",
    default_target_variable="Size_nm",
    recommended_target_variables=["Size_nm", "Hydrodynamic_Size_nm"],
    model_types=[
        ModelType.RANDOM_FOREST_REGRESSION,
        ModelType.GRADIENT_BOOSTING_REGRESSION,
        ModelType.LINEAR_REGRESSION,
    ],
    test_split=0.2,
    random_state=42,
    exclude_features=["Batch_ID", "Sterility_Pass", "Hydrodynamic_Size_nm"],
)

PDI_PREDICTION = TaskProfile(
    task_name="pdi_prediction",
    task_type=TaskType.PREDICT_PDI,
    description="Predict Polydispersity Index (PDI) for LNP formulations",
    default_target_variable="PDI",
    recommended_target_variables=["PDI"],
    model_types=[
        ModelType.RANDOM_FOREST_REGRESSION,
        ModelType.GRADIENT_BOOSTING_REGRESSION,
        ModelType.LINEAR_REGRESSION,
    ],
    test_split=0.2,
    random_state=42,
    exclude_features=["Batch_ID", "Sterility_Pass"],
)

UPTAKE_PREDICTION = TaskProfile(
    task_name="uptake_prediction",
    task_type=TaskType.PREDICT_UPTAKE,
    description="Predict cellular uptake efficiency for LNP formulations",
    default_target_variable="Delivery_Efficiency_%",
    recommended_target_variables=["Delivery_Efficiency_%", "Uptake_Score"],
    model_types=[
        ModelType.RANDOM_FOREST_REGRESSION,
        ModelType.GRADIENT_BOOSTING_REGRESSION,
        ModelType.LINEAR_REGRESSION,
    ],
    test_split=0.2,
    random_state=42,
    exclude_features=["Batch_ID", "Sterility_Pass"],
)

TOXICITY_CLASSIFICATION = TaskProfile(
    task_name="toxicity_classification",
    task_type=TaskType.CLASSIFY_TOXICITY_BAND,
    description="Classify toxicity into bands (Low/Medium/High)",
    default_target_variable="Toxicity_Band",
    recommended_target_variables=["Toxicity_Band", "Toxicity_Category"],
    model_types=[
        ModelType.RANDOM_FOREST_CLASSIFICATION,
        ModelType.GRADIENT_BOOSTING_CLASSIFICATION,
        ModelType.LOGISTIC_REGRESSION,
    ],
    test_split=0.2,
    random_state=42,
    exclude_features=["Batch_ID", "Sterility_Pass", "Toxicity_%"],
)

QC_PASS_PREDICTION = TaskProfile(
    task_name="qc_pass_prediction",
    task_type=TaskType.CLASSIFY_QC_PASS,
    description="Predict QC pass/fail based on formulation parameters",
    default_target_variable="Sterility_Pass",
    recommended_target_variables=["Sterility_Pass", "QC_Status"],
    model_types=[
        ModelType.RANDOM_FOREST_CLASSIFICATION,
        ModelType.GRADIENT_BOOSTING_CLASSIFICATION,
        ModelType.LOGISTIC_REGRESSION,
    ],
    test_split=0.2,
    random_state=42,
    exclude_features=["Batch_ID"],
)


# Registry of all available profiles
TASK_PROFILES: Dict[str, TaskProfile] = {
    "toxicity_prediction": TOXICITY_PREDICTION,
    "particle_size_prediction": PARTICLE_SIZE_PREDICTION,
    "pdi_prediction": PDI_PREDICTION,
    "uptake_prediction": UPTAKE_PREDICTION,
    "toxicity_classification": TOXICITY_CLASSIFICATION,
    "qc_pass_prediction": QC_PASS_PREDICTION,
}


def get_profile(profile_name: str) -> Optional[TaskProfile]:
    """Get a task profile by name"""
    return TASK_PROFILES.get(profile_name.lower())


def get_profile_choices() -> List[str]:
    """Get list of all available profile names for UI selection"""
    return list(TASK_PROFILES.keys())


def get_profile_descriptions() -> Dict[str, str]:
    """Get descriptions for all profiles for UI display"""
    return {name: profile.description for name, profile in TASK_PROFILES.items()}


def apply_profile(
    profile_name: str,
    df: "pd.DataFrame",
    custom_target: Optional[str] = None,
) -> tuple:
    """
    Apply a profile to a dataset and return recommended settings.

    Args:
        profile_name: Name of the profile to apply
        df: Input dataframe
        custom_target: Override the default target variable

    Returns:
        Tuple of (config, recommended_excludes, recommended_target)
    """
    profile = get_profile(profile_name)
    if not profile:
        raise ValueError(f"Unknown profile: {profile_name}")

    # Ensure df.columns is a list for reliable membership testing
    available_columns = list(df.columns)

    # Determine target variable
    target_var = custom_target or profile.default_target_variable
    if target_var not in available_columns:
        # Try recommended alternatives
        for alt_target in profile.recommended_target_variables:
            if alt_target in available_columns:
                target_var = alt_target
                break
        else:
            raise ValueError(
                f"Target variable '{profile.default_target_variable}' not found. "
                f"Available columns: {available_columns}"
            )

    # Filter excludes to only existing columns (using list to avoid boolean series issues)
    valid_excludes = [col for col in profile.exclude_features if col in available_columns]

    # Create config with fresh exclude features list
    config = profile.to_config(target_variable=target_var)
    config.exclude_features = valid_excludes

    return config, valid_excludes, target_var
