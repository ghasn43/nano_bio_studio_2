# core/scoring.py
from __future__ import annotations

import streamlit as st
import numpy as np


def compute_impact(design: dict) -> dict:
    """Compute delivery (0-100), toxicity (0-10), cost (0-100)."""

    d = design

    # ---- Delivery Score (0-100)
    # Size: optimal is 80-120nm
    if 80 <= d["Size"] <= 120:
        size_score = 100
    elif d["Size"] < 80:
        size_score = (d["Size"] / 80.0) * 100
    else:
        size_score = max(0, 100 - ((d["Size"] - 120) / 2))

    # Charge: optimal is -10 to +10 mV
    if abs(d["Charge"]) <= 10:
        charge_score = 100
    else:
        charge_score = max(0, 100 - ((abs(d["Charge"]) - 10) * 3))

    # Encapsulation: direct percentage
    encap_score = float(d["Encapsulation"])

    # Advanced properties (safe defaults if missing)
    pdi = float(d.get("PDI", 0.15))
    hyd_size = float(d.get("HydrodynamicSize", d["Size"] * 1.2))
    stability = float(d.get("Stability", 85))
    surface_area = float(d.get("SurfaceArea", 250))
    degradation_time = float(d.get("DegradationTime", 30))

    # PDI score (lower is better)
    pdi_score = max(0, 100 - (pdi * 200))

    # Hydrodynamic/core ratio score (closer to ~1.15 is good)
    size_ratio = hyd_size / d["Size"] if d["Size"] else 1.0
    if 1.0 <= size_ratio <= 1.3:
        hydrodynamic_score = 100
    else:
        hydrodynamic_score = max(0, 100 - (abs(size_ratio - 1.15) * 50))

    # Weighted average delivery
    delivery = (
        size_score * 0.25
        + charge_score * 0.20
        + encap_score * 0.25
        + pdi_score * 0.15
        + hydrodynamic_score * 0.10
        + stability * 0.05
    )

    # ---- Toxicity (0-10)
    base_toxicity = min(
        10,
        (abs(d["Charge"]) / 10) + (max(0, abs(d["Size"] - 100)) / 50),
    )

    pdi_toxicity = pdi * 2
    degradation_toxicity = max(0, (degradation_time - 30) / 30)

    toxicity = min(10, base_toxicity + pdi_toxicity + degradation_toxicity)

    # ---- Cost (0-100)
    base_cost = min(
        100,
        (100 - encap_score) * 0.8 + (d["Size"] / 4),
    )

    surface_area_cost = surface_area / 20
    pdi_cost = (0.2 - min(pdi, 0.2)) * 100
    degradation_cost = max(0, (degradation_time - 60) / 10)

    cost = min(100, base_cost + surface_area_cost + pdi_cost + degradation_cost)

    return {"Delivery": float(delivery), "Toxicity": float(toxicity), "Cost": float(cost)}


def get_recommendations(design: dict) -> list[str]:
    recommendations: list[str] = []

    if design["Size"] < 80:
        recommendations.append("🔴 **Increase size to 80–120nm** for better stability and circulation")
    elif design["Size"] > 150:
        recommendations.append("🔴 **Reduce size to 80–120nm** for better cellular uptake")

    if abs(design["Charge"]) > 15:
        recommendations.append("🟡 **Lower surface charge** to ±10mV for reduced toxicity")
    elif abs(design["Charge"]) > 10:
        recommendations.append("🟡 **Reduce charge** closer to neutral for optimal safety")

    if design["Encapsulation"] < 70:
        recommendations.append("🔴 **Improve encapsulation to >80%** for better drug delivery efficiency")
    elif design["Encapsulation"] < 85:
        recommendations.append("🟡 **Aim for >85% encapsulation** for optimal performance")

    if not recommendations:
        recommendations.append("✅ **Excellent design!** All parameters are within optimal ranges")

    return recommendations


def validate_parameter(param: str, value: float, optimal_range: list[float]) -> str:
    lo, hi = optimal_range
    if lo <= value <= hi:
        return "✅"
    if abs(value - lo) < 20 or abs(value - hi) < 20:
        return "🟡"
    return "🔴"


def regulatory_checklist(design: dict) -> float:
    checklist = {
        "Size < 200nm": design["Size"] <= 200,
        "PDI < 0.3": float(design.get("PDI", 0.15)) < 0.3,
        "Charge within ±30mV": abs(design["Charge"]) <= 30,
        "Encapsulation > 70%": design["Encapsulation"] >= 70,
        "Stability > 80%": float(design.get("Stability", 85)) >= 80,
        "Material approved for medical use": design.get("Material") in ["Lipid NP", "PLGA"],
        "Degradation products characterized": float(design.get("DegradationTime", 30)) < 90,
        "Sterilization method defined": True,
    }

    passed = sum(bool(v) for v in checklist.values())
    total = len(checklist)
    return (passed / total) * 100.0


def overall_score_from_impact(impact: dict) -> float:
    """Convenience helper used by multiple tabs."""
    return float(
        np.clip(
            (impact["Delivery"] * 0.6)
            + ((10 - impact["Toxicity"]) * 3)
            + ((100 - impact["Cost"]) * 0.1),
            0,
            100,
        )
    )
