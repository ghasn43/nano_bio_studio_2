"""
ML Training Page

Interactive page for building datasets and training ML models.
"""

import streamlit as st
import pandas as pd
import logging
from nanobio_studio.app.services.ml_service import MLService
from nanobio_studio.app.ml.schemas import (
    MLTaskConfig,
    TaskType,
    DatasetBuildRequest,
    TrainRequest,
)
from nanobio_studio.app.auth import Permission
from nanobio_studio.app.ui.streamlit_auth import (
    require_login,
    require_permission,
    show_user_info,
    StreamlitAuth,
)


logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="ML Training",
    page_icon="🤖",
    layout="wide",
)


def main():
    """Main page content"""

    st.title("🤖 ML Model Training")

    # Check authentication
    if not require_login("ML Training"):
        return

    # Check permission
    if not require_permission(Permission.MODEL_TRAIN, "Model training"):
        return

    # Show user info
    show_user_info()

    st.divider()

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Dataset Builder", "Train Models", "Training History"])

    # Tab 1: Dataset Builder
    with tab1:
        st.header("📊 Dataset Builder")

        uploaded_file = st.file_uploader(
            "Upload formulation data (CSV)",
            type=["csv"],
            key="dataset_upload",
        )

        if uploaded_file:
            # Load and preview data
            df = pd.read_csv(uploaded_file)

            st.subheader("Data Preview")
            st.dataframe(df.head(10), use_container_width=True)

            st.info(f"Rows: {len(df)} | Columns: {len(df.columns)}")

            # Dataset configuration
            st.subheader("Dataset Configuration")

            col1, col2 = st.columns(2)

            with col1:
                task_name = st.text_input(
                    "Task Name",
                    value="toxicity_prediction",
                    help="Unique identifier for this task",
                )

            with col2:
                task_type = st.selectbox(
                    "Task Type",
                    options=["regression", "classification"],
                    help="Type of ML task",
                )

            col1, col2 = st.columns(2)

            with col1:
                target_variable = st.selectbox(
                    "Target Variable",
                    options=df.columns,
                    help="Column to predict",
                )

            with col2:
                test_split = st.slider(
                    "Test Split Ratio",
                    min_value=0.1,
                    max_value=0.5,
                    value=0.2,
                    step=0.05,
                )

            # Feature selection
            st.subheader("Feature Selection")

            exclude_columns = st.multiselect(
                "Columns to Exclude",
                options=df.columns,
                help="Columns to exclude from training",
            )

            # Build button
            if st.button("Build Dataset", key="build_dataset_btn"):
                try:
                    with st.spinner("Building dataset..."):
                        ml_service = MLService()

                        config = MLTaskConfig(
                            task_name=task_name,
                            task_type=TaskType(task_type),
                            target_variable=target_variable,
                            test_split=test_split,
                            exclude_features=exclude_columns,
                        )

                        request = DatasetBuildRequest(task_config=config)

                        dataset = ml_service.build_dataset(df, request)

                        st.success("✅ Dataset built successfully!")

                        col1, col2, col3 = st.columns(3)

                        with col1:
                            st.metric("Total Samples", dataset["n_samples"])

                        with col2:
                            st.metric("Features", dataset["n_features"])

                        with col3:
                            st.metric("Train/Validation", f"{len(dataset['X_train'])}/{len(dataset['X_valid'])}")

                        # Store in session state
                        st.session_state.dataset = dataset
                        st.session_state.dataset_config = config

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Dataset build error: {e}")

    # Tab 2: Train Models
    with tab2:
        st.header("🤖 Train Models")

        if "dataset" not in st.session_state:
            st.info("👈 Please build a dataset first in the Dataset Builder tab")
            return

        uploaded_file = st.file_uploader(
            "Upload data for training (CSV)",
            type=["csv"],
            key="train_upload",
        )

        if uploaded_file:
            df = pd.read_csv(uploaded_file)

            st.subheader("Training Configuration")

            col1, col2 = st.columns(2)

            with col1:
                model_types = st.multiselect(
                    "Select Model Types",
                    options=["linear_regression", "random_forest", "gradient_boosting", "svm"],
                    default=["linear_regression", "random_forest"],
                    help="Models to train",
                )

            with col2:
                test_split = st.slider(
                    "Test Split",
                    min_value=0.1,
                    max_value=0.5,
                    value=0.2,
                    step=0.05,
                )

            col1, col2 = st.columns(2)

            with col1:
                save_artifacts = st.checkbox(
                    "Save Model Artifacts",
                    value=True,
                    help="Save trained models to disk",
                )

            with col2:
                artifact_name = st.text_input(
                    "Artifact Name",
                    value=st.session_state.dataset_config.task_name,
                    help="Name for saved artifacts",
                )

            if st.button("Start Training", key="start_training_btn"):
                try:
                    with st.spinner("🔄 Training models... This may take a few minutes"):
                        ml_service = MLService()

                        config = st.session_state.dataset_config
                        config.model_types = model_types

                        request = TrainRequest(
                            dataset_build_request=DatasetBuildRequest(task_config=config),
                            save_artifacts=save_artifacts,
                            artifact_name=artifact_name,
                        )

                        response = ml_service.train_models(df, request)

                        st.success("✅ Training complete!")

                        # Display results
                        col1, col2 = st.columns(2)

                        with col1:
                            st.metric("Best Model", response.best_model_type)

                        with col2:
                            st.metric("Total Samples", response.n_samples)

                        # Evaluation metrics
                        st.subheader("📈 Model Evaluation")

                        for summary in response.evaluation_summaries:
                            with st.expander(
                                f"{summary.model_type} {'⭐ BEST' if summary.best_model else ''}",
                                expanded=summary.best_model,
                            ):
                                col1, col2 = st.columns(2)

                                with col1:
                                    st.write("**Training Metrics**")
                                    for metric, value in summary.train_metrics.dict().items():
                                        st.write(f"  {metric}: {value:.4f}")

                                with col2:
                                    st.write("**Validation Metrics**")
                                    for metric, value in summary.validation_metrics.dict().items():
                                        st.write(f"  {metric}: {value:.4f}")

                        if response.artifact_path:
                            st.success(f"📦 Model saved to: {response.artifact_path}")

                        # Store in session
                        st.session_state.last_training = response

                except Exception as e:
                    st.error(f"Training Error: {str(e)}")
                    logger.error(f"Training error: {e}")

    # Tab 3: Training History
    with tab3:
        st.header("📚 Training History")

        if "last_training" in st.session_state:
            response = st.session_state.last_training

            st.subheader("Latest Training")

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Task", response.task_name)

            with col2:
                st.metric("Best Model", response.best_model_type)

            with col3:
                st.metric("Features", response.n_features)

            st.write("Use the ML Model Management page to view all trained models")

        else:
            st.info("No training history yet. Train a model to get started!")


if __name__ == "__main__":
    main()
