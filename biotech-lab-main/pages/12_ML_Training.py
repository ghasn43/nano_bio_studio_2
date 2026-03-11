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
from nanobio_studio.app.ml.task_profiles import (
    get_profile_choices,
    get_profile_descriptions,
    apply_profile,
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

            # Quick Start with Profiles
            st.subheader("⚡ Quick Start with Predefined Profiles")
            
            profile_names = get_profile_choices()
            profile_descriptions = get_profile_descriptions()
            
            # Create selectbox with descriptions
            selected_profile = st.selectbox(
                "Select a Task Profile",
                options=profile_names,
                index=0,  # Default to toxicity_prediction
                format_func=lambda x: f"{x.replace('_', ' ').title()} - {profile_descriptions[x]}",
                help="Choose a predefined configuration for your ML task",
                key="profile_selector"
            )
            
            # Show profile details
            with st.expander("📋 Profile Information", expanded=False):
                profile_desc = profile_descriptions[selected_profile]
                st.write(f"**Description:** {profile_desc}")
            
            # Apply profile button
            if st.button("Apply Profile Settings", key="apply_profile_btn", type="primary"):
                try:
                    config, excludes, target = apply_profile(selected_profile, df)
                    st.session_state.profile_config = config
                    st.session_state.profile_excludes = excludes
                    st.session_state.profile_target = target
                    st.success(f"✅ Applied profile: **{selected_profile}**")
                    st.info(f"Target: **{target}** | Excluding: **{', '.join(excludes) if excludes else 'None'}**")
                except Exception as e:
                    st.error(f"Error applying profile: {str(e)}")
            
            st.divider()
            
            # Dataset configuration
            st.subheader("📊 Dataset Configuration")
            
            # Use profile settings if available, otherwise defaults
            use_profile = "profile_config" in st.session_state
            profile_config = st.session_state.get("profile_config")
            
            if use_profile:
                st.info("🎯 Using settings from applied profile")
                col1, col2 = st.columns(2)
                with col1:
                    task_name = st.text_input(
                        "Task Name",
                        value=profile_config.task_name,
                        help="Unique identifier for this task",
                    )
                with col2:
                    task_type = profile_config.task_type.value
                    st.selectbox(
                        "Task Type",
                        options=[profile_config.task_type.value],
                        disabled=True,
                        help="Auto-set from profile",
                    )
            else:
                col1, col2 = st.columns(2)
                with col1:
                    task_name = st.text_input(
                        "Task Name",
                        value="custom_task",
                        help="Unique identifier for this task",
                    )
                with col2:
                    task_type = st.selectbox(
                        "Task Type",
                        options=[
                            "predict_particle_size",
                            "predict_pdi",
                            "predict_toxicity",
                            "predict_uptake",
                            "predict_transfection",
                            "classify_toxicity_band",
                            "classify_uptake_band",
                            "classify_qc_pass",
                        ],
                        help="Select the specific ML prediction task",
                    )

            col1, col2 = st.columns(2)

            with col1:
                if use_profile:
                    # Convert columns to list to avoid pandas Index issues
                    columns_list = list(df.columns)
                    target_idx = 0
                    try:
                        if "profile_target" in st.session_state and st.session_state.profile_target in columns_list:
                            target_idx = columns_list.index(st.session_state.profile_target)
                    except (ValueError, KeyError):
                        target_idx = 0
                    
                    target_variable = st.selectbox(
                        "Target Variable",
                        options=columns_list,
                        index=target_idx,
                        help="Column to predict (auto-set from profile)",
                    )
                else:
                    target_variable = st.selectbox(
                        "Target Variable",
                        options=list(df.columns),
                        help="Column to predict",
                    )

            with col2:
                test_split = st.slider(
                    "Test Split Ratio",
                    min_value=0.1,
                    max_value=0.5,
                    value=0.2 if not use_profile else profile_config.test_split,
                    step=0.05,
                )

            # Feature selection
            st.subheader("Feature Selection")

            default_excludes = []
            if "profile_excludes" in st.session_state:
                default_excludes = st.session_state.profile_excludes
                st.info(f"✓ Profile recommends excluding: **{', '.join(default_excludes)}**")

            exclude_columns = st.multiselect(
                "Columns to Exclude",
                options=df.columns,
                default=default_excludes,
                help="Columns to exclude from training (profile recommendations shown above)",
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
                            st.metric("Train/Validation Split", f"{len(dataset['X_train'])}/{len(dataset['X_valid'])}")

                        # Store in session state
                        st.session_state.dataset = dataset
                        st.session_state.dataset_config = config
                        st.session_state.raw_dataframe = df  # Store original dataframe for training
                        
                        # Show dataset summary
                        with st.expander("📊 Dataset Summary", expanded=True):
                            st.write("**Features Used:**")
                            st.write(dataset.get("feature_names", []))

                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Dataset build error: {e}")

    # Tab 2: Train Models
    with tab2:
        st.header("🤖 Train Models")

        if "dataset" not in st.session_state:
            st.warning("⚠️ No dataset found!")
            st.info("👈 Please build a dataset first in the **Dataset Builder** tab, then come back here to train models.")
            st.stop()

        # Use the dataset from session_state
        dataset = st.session_state.dataset
        dataset_config = st.session_state.dataset_config
        raw_dataframe = st.session_state.raw_dataframe  # Get original dataframe for training
        
        st.success(f"✅ Using dataset: **{dataset_config.task_name}**")
        st.info(f"📊 Data: {dataset['n_samples']} samples, {dataset['n_features']} features | Train: {len(dataset['X_train'])}, Validation: {len(dataset['X_valid'])}")
        
        with st.expander("📋 Dataset Details", expanded=False):
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Task Name", dataset_config.task_name)
                st.metric("Target Variable", dataset_config.target_variable)
            with col2:
                st.metric("Total Samples", dataset['n_samples'])
                st.metric("Features Used", dataset['n_features'])
        
        st.divider()
        st.subheader("🎛️ Training Configuration")

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

                        # Use the built dataset from session_state
                        response = ml_service.train_models(raw_dataframe, request)

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
                                        if value is not None:
                                            st.write(f"  {metric}: {value:.4f}")
                                        else:
                                            st.write(f"  {metric}: N/A")

                                with col2:
                                    st.write("**Validation Metrics**")
                                    for metric, value in summary.validation_metrics.dict().items():
                                        if value is not None:
                                            st.write(f"  {metric}: {value:.4f}")
                                        else:
                                            st.write(f"  {metric}: N/A")

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

        try:
            from nanobio_studio.app.db.database import get_db, ModelRepository
            import os
            
            logger.info("="*60)
            logger.info("HISTORY LOAD: Starting training history load...")
            
            db = get_db()
            logger.info(f"HISTORY LOAD: Database instance ID: {id(db)}")
            logger.info(f"HISTORY LOAD: Engine ID: {id(db.engine)}")
            logger.info(f"HISTORY LOAD: Database engine: {db.engine.url}")
            
            # Check if database file exists
            db_url_str = str(db.engine.url)
            if "sqlite" in db_url_str:
                db_file = db_url_str.replace("sqlite:///", "")
                cwd = os.getcwd()
                logger.info(f"HISTORY LOAD: Current working directory: {cwd}")
                logger.info(f"HISTORY LOAD: Database file path (relative): {db_file}")
                
                # Try absolute path
                abs_db_path = os.path.abspath(db_file)
                logger.info(f"HISTORY LOAD: Database file path (absolute): {abs_db_path}")
                
                if os.path.exists(db_file):
                    file_size = os.path.getsize(db_file)
                    logger.info(f"✅ HISTORY LOAD: Database file EXISTS at relative path, size: {file_size} bytes")
                elif os.path.exists(abs_db_path):
                    file_size = os.path.getsize(abs_db_path)
                    logger.info(f"✅ HISTORY LOAD: Database file EXISTS at absolute path, size: {file_size} bytes")
                else:
                    logger.warning(f"❌ HISTORY LOAD: Database file NOT found at: {db_file} or {abs_db_path}")
                    st.warning("⚠️ Database file not found - training history cannot persist")
            
            session = db.get_session()
            logger.info(f"HISTORY LOAD: Session created: {id(session)}")
            
            # Check row count before retrieving
            from sqlalchemy import text
            result = session.execute(text("SELECT COUNT(*) FROM trained_models"))
            row_count = result.scalar()
            logger.info(f"HISTORY LOAD: Training table has {row_count} rows")
            
            if row_count > 0:
                # List all IDs to debug
                result = session.execute(text("SELECT id, task_name, created_at FROM trained_models ORDER BY created_at DESC"))
                for row in result:
                    logger.info(f"HISTORY LOAD: Record - ID: {row[0]}, Task: {row[1]}, Created: {row[2]}")
            
            model_repo = ModelRepository(session)
            trained_models = model_repo.get_all()
            
            logger.info(f"HISTORY LOAD: Retrieved {len(trained_models)} trained models from database")
            
            # Important: Detach objects from session before closing
            session.expunge_all()
            session.close()
            logger.info(f"HISTORY LOAD: Session closed")
            logger.info("="*60)
            
            if trained_models:
                st.success(f"Found {len(trained_models)} trained model(s)")
                
                # Display as table first
                with st.expander("📋 All Trained Models", expanded=True):
                    models_data = []
                    for model in trained_models:
                        models_data.append({
                            "Task": model.task_name,
                            "Model Type": model.model_type,
                            "Samples": model.n_training_samples,
                            "Features": model.n_features,
                            "Train R²": f"{model.train_score:.4f}" if model.train_score else "N/A",
                            "Valid R²": f"{model.validation_score:.4f}" if model.validation_score else "N/A",
                            "Created": model.created_at.strftime("%Y-%m-%d %H:%M:%S") if model.created_at else "N/A",
                        })
                    
                    models_df = pd.DataFrame(models_data)
                    st.dataframe(models_df, use_container_width=True)
                
                # Show detailed view for each model
                st.subheader("📊 Model Details")
                
                for model in trained_models:
                    with st.expander(f"{model.task_name} - {model.model_type}", expanded=False):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.metric("Samples", model.n_training_samples)
                            st.metric("Features", model.n_features)
                        
                        with col2:
                            st.metric("Model Type", model.model_type)
                            st.metric("Task Type", model.task_type.replace('predict_', '').replace('classify_', ''))
                        
                        with col3:
                            st.metric("Train R²", f"{model.train_score:.4f}" if model.train_score else "N/A")
                            st.metric("Valid R²", f"{model.validation_score:.4f}" if model.validation_score else "N/A")
                        
                        # Show evaluation details if available
                        if model.evaluation_summary:
                            st.write("**Detailed Metrics:**")
                            if 'train' in model.evaluation_summary and model.evaluation_summary['train']:
                                st.write("*Training Metrics:*")
                                for key, value in model.evaluation_summary['train'].items():
                                    if value is not None:
                                        st.write(f"  • {key}: {value:.4f}" if isinstance(value, float) else f"  • {key}: {value}")
                            
                            if 'validation' in model.evaluation_summary and model.evaluation_summary['validation']:
                                st.write("*Validation Metrics:*")
                                for key, value in model.evaluation_summary['validation'].items():
                                    if value is not None:
                                        st.write(f"  • {key}: {value:.4f}" if isinstance(value, float) else f"  • {key}: {value}")
                        
                        st.caption(f"Created: {model.created_at.strftime('%Y-%m-%d %H:%M:%S UTC') if model.created_at else 'Unknown'}")
            else:
                st.info("No training history yet. Train a model in the **Train Models** tab to get started!")
        
        except Exception as e:
            logger.error("="*60)
            logger.error(f"Error loading training history: {str(e)}", exc_info=True)
            logger.error("="*60)
            st.error(f"Error loading training history: {str(e)}")
            st.info("Using in-session training history (will be lost on page refresh)")
            
            # Fallback to session state if database fails
            if "last_training" in st.session_state:
                response = st.session_state.last_training
                st.subheader("Latest Training (In-Session)")
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Task", response.task_name)
                with col2:
                    st.metric("Best Model", response.best_model_type)
                with col3:
                    st.metric("Features", response.n_features)
            else:
                st.warning("No training history available")



if __name__ == "__main__":
    main()
