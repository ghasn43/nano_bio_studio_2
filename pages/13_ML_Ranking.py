"""
ML Ranking & Candidate Evaluation Page

Interactive page for ranking formulations against multiple criteria.
"""

import sys
from pathlib import Path

# Add biotech-lab-main to sys.path for imports from nanobio_studio
sys.path.insert(0, str(Path(__file__).parent.parent / "biotech-lab-main"))

import streamlit as st
import pandas as pd
import logging
import json
from nanobio_studio.app.services.ml_service import RankingService
from nanobio_studio.app.ml.schemas import RankingRequest
from nanobio_studio.app.auth import Permission
from nanobio_studio.app.ui.streamlit_auth import (
    require_login,
    require_permission,
    show_user_info,
)


logger = logging.getLogger(__name__)

st.set_page_config(
    page_title="ML Ranking",
    page_icon="🏆",
    layout="wide",
)


def main():
    """Main page content"""

    st.title("🏆 ML Ranking & Candidate Evaluation")

    # Check authentication
    if not require_login("ML Ranking"):
        return

    # Check permission
    if not require_permission(Permission.RANK_CREATE, "Candidate ranking"):
        return

    # Show user info
    show_user_info()

    st.divider()

    tab1, tab2 = st.tabs(["Rank Candidates", "Ranking Results"])

    with tab1:
        st.header("🎯 Rank Candidate Formulations")

        # Upload candidates
        uploaded_file = st.file_uploader(
            "Upload candidate formulations (CSV)",
            type=["csv"],
            key="ranking_upload",
        )

        if uploaded_file:
            candidates_df = pd.read_csv(uploaded_file)

            st.subheader("Candidates Preview")
            st.dataframe(candidates_df, use_container_width=True)

            st.info(f"Total candidates: {len(candidates_df)}")

            # Ranking criteria
            st.subheader("⚙️ Ranking Configuration")

            ranking_method = st.selectbox(
                "Ranking Method",
                options=[
                    "weighted_score",
                    "pareto_ranking",
                    "composite_index",
                    "multi_objective",
                ],
                help="Algorithm for ranking",
            )

            # Criteria selection
            st.subheader("Ranking Criteria")

            available_columns = list(candidates_df.columns)

            criteria = {}

            col1, col2 = st.columns([3, 1])

            with col1:
                st.write("**Select columns and optimization direction:**")

            num_criteria = st.slider(
                "Number of criteria",
                min_value=1,
                max_value=len(available_columns),
                value=min(3, len(available_columns)),
            )

            for i in range(num_criteria):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    column = st.selectbox(
                        f"Criterion {i+1}",
                        options=available_columns,
                        key=f"criterion_col_{i}",
                    )

                with col2:
                    direction = st.selectbox(
                        "Direction",
                        options=["maximize", "minimize"],
                        key=f"criterion_dir_{i}",
                    )

                with col3:
                    weight = st.number_input(
                        "Weight",
                        min_value=0.0,
                        max_value=10.0,
                        value=1.0,
                        step=0.1,
                        key=f"criterion_weight_{i}",
                    )

                criteria[column] = {"direction": direction, "weight": weight}

            if st.button("🚀 Rank Candidates", key="rank_btn"):
                try:
                    with st.spinner("Ranking candidates..."):
                        ranking_service = RankingService()

                        # Prepare request
                        candidates = candidates_df.to_dict("records")

                        request = RankingRequest(
                            candidates=candidates,
                            criteria=criteria,
                            method=ranking_method,
                        )

                        # Rank
                        results = ranking_service.rank_candidates(candidates, request)

                        st.success("✅ Ranking complete!")

                        # Display results
                        results_df = pd.DataFrame(results)

                        st.subheader("📊 Ranking Results")
                        st.dataframe(
                            results_df.head(20),
                            use_container_width=True,
                        )

                        # Store in session
                        st.session_state.ranking_results = results_df

                        # Download button
                        csv_data = results_df.to_csv(index=False)
                        st.download_button(
                            "⬇️ Download Results (CSV)",
                            data=csv_data,
                            file_name="ranking_results.csv",
                            mime="text/csv",
                        )

                except Exception as e:
                    st.error(f"Ranking Error: {str(e)}")
                    logger.error(f"Ranking error: {e}")

    with tab2:
        st.header("📊 Ranking Results")

        if "ranking_results" in st.session_state:
            results_df = st.session_state.ranking_results

            # Summary statistics
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric("Total Candidates", len(results_df))

            with col2:
                if "rank" in results_df.columns:
                    st.metric("Top Rank", results_df["rank"].min())

            with col3:
                if "score" in results_df.columns:
                    st.metric("Max Score", f"{results_df['score'].max():.4f}")

            st.subheader("Top Candidates")
            st.dataframe(results_df.head(10), use_container_width=True)

            # Visualization
            if "score" in results_df.columns:
                st.subheader("Score Distribution")

                chart_data = results_df.head(20).copy()
                chart_data["index"] = range(len(chart_data))

                st.bar_chart(
                    data=chart_data.set_index("index")["score"],
                    use_container_width=True,
                )

            # Export
            csv_data = results_df.to_csv(index=False)
            st.download_button(
                "⬇️ Download All Results",
                data=csv_data,
                file_name="all_ranking_results.csv",
                mime="text/csv",
            )

        else:
            st.info("👈 Rank candidates first in the Rank Candidates tab")


if __name__ == "__main__":
    main()
