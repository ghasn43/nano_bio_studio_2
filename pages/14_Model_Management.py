"""
Model Management & Monitoring Page

Page for viewing, managing, and monitoring trained ML models.
"""

import streamlit as st
import pandas as pd
import logging
from nanobio_studio.app.db.database import get_db, ModelRepository
from nanobio_studio.app.auth import Permission
from nanobio_studio.app.ui.streamlit_auth import (
    require_login,
    require_permission,
    show_user_info,
)


logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="Model Management",
    page_icon="📦",
    layout="wide",
)


def main():
    """Main page content"""

    st.title("📦 ML Model Management")

    # Check authentication
    if not require_login("Model Management"):
        return

    # Check permission (read is minimum, admin ops need higher perms)
    if not require_permission(Permission.MODEL_READ, "Model viewing"):
        return

    # Show user info
    show_user_info()

    st.divider()

    tab1, tab2, tab3 = st.tabs(["Available Models", "Model Details", "Performance Comparison"])

    with tab1:
        st.header("🏠 Available Models")

        try:
            # Get database session
            db = get_db()
            session = db.get_session()
            model_repo = ModelRepository(session)

            # Get all models
            models = model_repo.get_all()
            session.close()

            if not models:
                st.info("No trained models available yet. Train a model in the ML Training page.")
                return

            # Display models table
            models_data = []
            for model in models:
                models_data.append({
                    "Task Name": model.task_name,
                    "Model Type": model.model_type,
                    "Task Type": model.task_type,
                    "Target": model.target_variable,
                    "Train Score": f"{model.train_score:.4f}" if model.train_score else "N/A",
                    "Validation Score": f"{model.validation_score:.4f}" if model.validation_score else "N/A",
                    "Samples": model.n_training_samples,
                    "Features": model.n_features,
                    "Created": model.created_at.strftime("%Y-%m-%d %H:%M") if model.created_at else "N/A",
                })

            models_df = pd.DataFrame(models_data)

            st.dataframe(
                models_df,
                use_container_width=True,
                height=400,
            )

            st.info(f"Total models: {len(models)}")

        except Exception as e:
            st.error(f"Error loading models: {str(e)}")
            logger.error(f"Model loading error: {e}")

    with tab2:
        st.header("🔍 Model Details")

        try:
            db = get_db()
            session = db.get_session()
            model_repo = ModelRepository(session)
            models = model_repo.get_all()
            session.close()

            if not models:
                st.info("No models available")
                return

            # Select model
            model_names = [m.task_name for m in models]
            selected_task = st.selectbox(
                "Select Model",
                options=model_names,
            )

            # Get selected model
            session = db.get_session()
            selected_model = model_repo.get_by_task(selected_task)
            session.close()

            if selected_model:
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**Basic Information**")
                    st.write(f"Task Name: {selected_model.task_name}")
                    st.write(f"Model Type: {selected_model.model_type}")
                    st.write(f"Task Type: {selected_model.task_type}")
                    st.write(f"Target Variable: {selected_model.target_variable}")

                with col2:
                    st.write("**Performance**")
                    st.write(f"Training Score: {selected_model.train_score:.4f}" if selected_model.train_score else "N/A")
                    st.write(f"Validation Score: {selected_model.validation_score:.4f}" if selected_model.validation_score else "N/A")
                    st.write(f"Samples: {selected_model.n_training_samples}")
                    st.write(f"Features: {selected_model.n_features}")

                # Configuration
                if selected_model.task_config:
                    st.subheader("Task Configuration")
                    st.json(selected_model.task_config)

                # Evaluation summary
                if selected_model.evaluation_summary:
                    st.subheader("Evaluation Summary")

                    eval_summary = selected_model.evaluation_summary
                    for model_type, metrics in eval_summary.items():
                        with st.expander(f"📊 {model_type}"):
                            col1, col2 = st.columns(2)

                            with col1:
                                st.write("**Training Metrics**")
                                if "train" in metrics:
                                    for metric, value in metrics["train"].items():
                                        st.write(f"  {metric}: {value:.4f}")

                            with col2:
                                st.write("**Validation Metrics**")
                                if "validation" in metrics:
                                    for metric, value in metrics["validation"].items():
                                        st.write(f"  {metric}: {value:.4f}")

                # Model actions
                st.subheader("Actions")

                col1, col2 = st.columns(2)

                with col1:
                    if st.button("📥 Download Model", key="download_model_btn"):
                        if selected_model.model_path:
                            st.info(f"Model location: {selected_model.model_path}")
                            st.write("Download functionality would be implemented here")

                with col2:
                    if require_permission(Permission.MODEL_DELETE, "Model deletion"):
                        if st.button("🗑️ Delete Model", key="delete_model_btn"):
                            if st.confirm("Are you sure you want to delete this model?"):
                                db = get_db()
                                session = db.get_session()
                                model_repo = ModelRepository(session)
                                model_repo.delete_by_task(selected_task)
                                session.close()
                                st.success("✅ Model deleted")
                                st.rerun()

        except Exception as e:
            st.error(f"Error: {str(e)}")
            logger.error(f"Model details error: {e}")

    with tab3:
        st.header("📈 Performance Comparison")

        try:
            db = get_db()
            session = db.get_session()
            model_repo = ModelRepository(session)
            models = model_repo.get_all()
            session.close()

            if not models:
                st.info("No models to compare")
                return

            # Create comparison dataframe
            comparison_data = []
            for model in models:
                comparison_data.append({
                    "Task": model.task_name,
                    "Model": model.model_type,
                    "Train Score": model.train_score or 0,
                    "Val Score": model.validation_score or 0,
                })

            comparison_df = pd.DataFrame(comparison_data)

            # Display metrics
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Training Scores")
                st.bar_chart(
                    data=comparison_df.set_index("Task")["Train Score"],
                    use_container_width=True,
                )

            with col2:
                st.subheader("Validation Scores")
                st.bar_chart(
                    data=comparison_df.set_index("Task")["Val Score"],
                    use_container_width=True,
                )

            st.subheader("Full Comparison")
            st.dataframe(comparison_df, use_container_width=True)

        except Exception as e:
            st.error(f"Error: {str(e)}")
            logger.error(f"Comparison error: {e}")


if __name__ == "__main__":
    main()
