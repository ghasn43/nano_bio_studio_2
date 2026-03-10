# viz/dial.py
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from matplotlib.patches import Wedge

def show_circular_dial(value: float, label: str = "Overall Design Score", size: float = 3.0):
    score = float(np.clip(value, 0, 100))
    fig, ax = plt.subplots(figsize=(size, size))

    segments = [
        (180, 240, "#FF4E4E"), (240, 300, "#FFC200"), (300, 360, "#4CAF50"),
        (0, 60, "#4CAF50"), (60, 120, "#FFC200"), (120, 180, "#FF4E4E"),
    ]
    for start, end, color in segments:
        ax.add_patch(Wedge((0, 0), 1.0, start, end, width=0.3, color=color, alpha=0.3))

    ax.add_patch(Wedge((0, 0), 1.0, 0, 360, width=0.3, fill=False, edgecolor="#444", linewidth=2))

    needle_angle = 180 + (score / 100.0) * 180
    angle_rad = np.radians(needle_angle)
    x_end = 0.8 * np.cos(angle_rad)
    y_end = 0.8 * np.sin(angle_rad)
    ax.plot([0, x_end], [0, y_end], color="#333", linewidth=3)
    ax.plot(0, 0, "ko", markersize=6)

    ax.text(0, 0, f"{score:.0f}%", ha="center", va="center", fontsize=16, fontweight="bold", color="#333")
    ax.text(0, -1.2, label, ha="center", va="center", fontsize=12, color="#555", fontweight="600")

    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.set_aspect("equal")
    ax.axis("off")

    st.pyplot(fig, width='content')
