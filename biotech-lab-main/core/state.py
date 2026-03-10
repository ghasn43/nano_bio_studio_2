# core/state.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple


# -----------------------------
# Defaults + Session State Init
# -----------------------------

DEFAULTS: Dict[str, Any] = {
    # Feature flags (capability checks)
    "plotly_ok": True,
    "sklearn_ok": True,
    "py3dmol_ok": True,
    "rdkit_ok": False,

    # UI / navigation
    "active_tab": "Home",
    "sidebar_collapsed": False,

    # App data placeholders (adjust to your project)
    "materials": [],
    "designs": [],
    "delivery_plan": {},
    "toxicity_results": {},
    "cost_results": {},
    "protocol_steps": [],
    "quiz_state": {},

    # Any other state used across tabs
    "debug": False,
}


def init_state(overrides: Optional[Dict[str, Any]] = None) -> None:
    """
    Initializes st.session_state with DEFAULTS.
    Safe to call multiple times.
    """
    import streamlit as st

    if overrides is None:
        overrides = {}

    for k, v in DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v

    # Apply overrides last (only if key not set, or you want to force set)
    for k, v in overrides.items():
        if k not in st.session_state:
            st.session_state[k] = v


def ensure_state() -> None:
    """
    Alias used by older imports. Keeps your app stable if tabs import ensure_state().
    """
    init_state()


# --------------------------------
# Tabs registry (single source truth)
# --------------------------------

@dataclass(frozen=True)
class TabSpec:
    key: str          # stable internal key
    title: str        # label shown in UI
    module: str       # tabs.<module_name>
    order: int = 0    # for sorting
    enabled: bool = True


# IMPORTANT: keep this list as your one-and-only definition of tabs
TAB_SPECS: List[TabSpec] = [
    TabSpec(key="home",      title="Home",      module="tabs.home",      order=10),
    TabSpec(key="materials", title="Materials", module="tabs.materials", order=20),
    TabSpec(key="design",    title="Design",    module="tabs.design",    order=30),
    TabSpec(key="delivery",  title="Delivery",  module="tabs.delivery",  order=40),
    TabSpec(key="toxicity",  title="Toxicity",  module="tabs.toxicity",  order=50),
    TabSpec(key="cost",      title="Cost",      module="tabs.cost",      order=60),
    TabSpec(key="protocol",  title="Protocol",  module="tabs.protocol",  order=70),
    TabSpec(key="quiz",      title="Quiz",      module="tabs.quiz",      order=80),
    TabSpec(key="view3d",    title="3D View",   module="tabs.view3d",    order=90),
    TabSpec(key="optimize",  title="Optimize",  module="tabs.optimize",  order=100),
]


def get_available_tabs() -> List[TabSpec]:
    """
    Returns enabled TabSpec list sorted by order.
    You can extend this later to hide tabs depending on feature flags.
    """
    tabs = [t for t in TAB_SPECS if t.enabled]
    return sorted(tabs, key=lambda x: x.order)


# --------------------------------
# Optional: compatibility exports
# --------------------------------

def get_tab_titles() -> List[str]:
    return [t.title for t in get_available_tabs()]


def set_active_tab(title: str) -> None:
    import streamlit as st
    st.session_state["active_tab"] = title


def get_active_tab() -> str:
    import streamlit as st
    return st.session_state.get("active_tab", "Home")
