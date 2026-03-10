# core/deps.py
import streamlit as st

def check_plotly():
    try:
        import plotly.graph_objects as go  # noqa: F401
        import plotly.express as px        # noqa: F401
        return True
    except Exception:
        return False

def check_sklearn():
    try:
        import sklearn  # noqa: F401
        return True
    except Exception:
        return False

def warn_missing_deps(plotly_ok: bool, sklearn_ok: bool):
    if not sklearn_ok:
        st.warning("⚠️ scikit-learn not available. AI optimization disabled. Install: `pip install scikit-learn`")
    if not plotly_ok:
        st.info("ℹ️ Plotly not available. 3D module will be disabled. Install: `pip install plotly`")
