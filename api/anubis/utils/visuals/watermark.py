from datetime import datetime


def add_watermark(ax):
    ax.text(
        0.97, 0.9, f"Generated {datetime.now()}",
        transform=ax.transAxes, fontsize=12, color="gray", alpha=0.5,
        ha="right", va="center",
    )
