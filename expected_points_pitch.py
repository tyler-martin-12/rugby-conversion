"""
Expected points (try + conversion) vs. lateral try location —
visualised as a filled curve drawn inside the in-goal zone of a
top-down rugby pitch.

The in-goal (10 m deep) is used as the plotting canvas:
  try line  (y = 0)   ↔  5 pts  (try alone, zero conversion bonus)
  dead-ball (y = -10) ↔  7 pts  (try + certain conversion)

The filled curve shows how much expected value above 5 pts the
kicker adds, as a function of where the try was scored laterally.

Data: 13,338 conversion attempts from goal_kicking_data.csv
(WhartonSABI / Quarrie & Hopkins, 2000-2012).
"""

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyArrowPatch
from scipy.interpolate import UnivariateSpline

# ---------------------------------------------------------------------------
# Load & fit empirical conversion data
# ---------------------------------------------------------------------------
df   = pd.read_csv("goal_kicking_data.csv")
conv = df[df["Type"] == 2].copy()
conv["lateral_m"] = (conv["X1 Metres"] - 35).abs()

bins = np.arange(0, 37.5, 2.5)
conv["bin"] = pd.cut(conv["lateral_m"], bins=bins, include_lowest=True)
agg = (
    conv.groupby("bin", observed=True)
        .agg(attempts=("Quality", "count"),
             made=("Quality", lambda x: (x == 1).sum()))
)
agg["prob"]    = agg["made"] / agg["attempts"]
agg["bin_mid"] = [i.mid for i in agg.index]

bin_mid = agg["bin_mid"].values
bin_p   = agg["prob"].values
n       = agg["attempts"].values

spl = UnivariateSpline(bin_mid, bin_p, w=np.sqrt(n), k=3, s=len(bin_mid))

HALF_WIDTH = 35.0
lat    = np.linspace(-HALF_WIDTH, HALF_WIDTH, 700)
p_conv = np.clip(spl(np.abs(lat)), 0, 1)
ep     = 5 + 2 * p_conv

# ---------------------------------------------------------------------------
# Map expected points → in-goal y-coordinate
# 5 pts → y = 0 (try line), 7 pts → y = -10 (dead-ball line)
# ---------------------------------------------------------------------------
def ep_to_y(e):
    return -(e - 5) * 5.0          # 2 pts spans 10 m

curve_y = ep_to_y(ep)

# ---------------------------------------------------------------------------
# Figure
# ---------------------------------------------------------------------------
IN_GOAL  = 10.0
Y_BOT    = -IN_GOAL          # dead-ball line
Y_TOP    = 30.0              # show 30 m of field above try line
POST_SEP = 5.6 / 2

fig, ax = plt.subplots(figsize=(13, 8))
ax.set_facecolor("#2d6a2d")

# ── Grass stripes ─────────────────────────────────────────────────────────────
stripe_colors = ["#2d6a2d", "#316e31"]
for i, y_start in enumerate(range(int(Y_BOT), int(Y_TOP), 5)):
    ax.add_patch(mpatches.Rectangle(
        (-HALF_WIDTH, y_start), 2 * HALF_WIDTH, 5,
        color=stripe_colors[i % 2], zorder=0
    ))

# ── In-goal darker tint ───────────────────────────────────────────────────────
ax.add_patch(mpatches.Rectangle(
    (-HALF_WIDTH, Y_BOT), 2 * HALF_WIDTH, IN_GOAL,
    color="#1f4f1f", zorder=1, alpha=0.5
))

# ── EP fill: between try line (y=0) and the EP curve ─────────────────────────
# Shade from curve_y up to 0 (try line) with a warm golden fill
ax.fill_between(lat, curve_y, 0,
                color="#f5c518", alpha=0.55, zorder=2, linewidth=0)

# ── EP curve ──────────────────────────────────────────────────────────────────
ax.plot(lat, curve_y, color="white", lw=2.5, zorder=5)

# ── Pitch lines ───────────────────────────────────────────────────────────────
line_kw = dict(color="white", lw=1.5, zorder=3)
ax.axvline(-HALF_WIDTH, **line_kw)
ax.axvline( HALF_WIDTH, **line_kw)
ax.axhline(0,    color="white", lw=3,   zorder=4)    # try line
ax.axhline(Y_BOT, **line_kw)                          # dead-ball line
for y in [5, 10, 22]:
    ax.axhline(y, color="white", lw=0.8, ls="--", alpha=0.45, zorder=3)
    ax.text(HALF_WIDTH + 0.6, y, f"{y} m",
            color="white", fontsize=8, va="center", zorder=5)

# ── Goal posts ────────────────────────────────────────────────────────────────
post_kw = dict(color="#FFD700", lw=3.5, zorder=6)
ax.plot([-POST_SEP, -POST_SEP], [Y_BOT, 0], **post_kw)
ax.plot([ POST_SEP,  POST_SEP], [Y_BOT, 0], **post_kw)
ax.plot([-POST_SEP,  POST_SEP], [0,     0], **post_kw)   # crossbar

# ── EP scale on left edge ─────────────────────────────────────────────────────
scale_x = -HALF_WIDTH - 3.5
for pts in [5, 5.5, 6, 6.5, 7]:
    y = ep_to_y(pts)
    ax.plot([scale_x - 0.5, scale_x + 0.5], [y, y], color="white", lw=1, zorder=7)
    ax.text(scale_x - 0.8, y, f"{pts:.1f}",
            color="white", fontsize=8, ha="right", va="center", zorder=7)

# Bracket
ax.annotate("", xy=(scale_x, Y_BOT), xytext=(scale_x, 0),
            arrowprops=dict(arrowstyle="<->", color="white", lw=1.2))
ax.text(scale_x - 2.2, Y_BOT / 2, "Expected\npoints",
        color="white", fontsize=8.5, ha="center", va="center",
        rotation=90, zorder=7)

# ── Labels on try line & dead-ball line ──────────────────────────────────────
ax.text(-HALF_WIDTH + 1, 0.8,  "TRY LINE",       color="white", fontsize=9, zorder=8)
ax.text(-HALF_WIDTH + 1, Y_BOT + 0.8, "DEAD-BALL LINE", color="white", fontsize=8,
        alpha=0.7, zorder=8)
ax.text(-HALF_WIDTH + 1, Y_BOT + 3,  "IN-GOAL",  color="white", fontsize=9,
        alpha=0.6, zorder=8)

# ── Key annotations ───────────────────────────────────────────────────────────
ep_centre = float(5 + 2 * np.clip(spl(0), 0, 1))
ep_tl     = float(ep[0])
y_ctr     = ep_to_y(ep_centre)
y_tl      = ep_to_y(ep_tl)

ax.annotate(f"{ep_centre:.2f} pts",
            xy=(0, y_ctr), xytext=(8, y_ctr - 1.5),
            color="white", fontsize=9, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="white", lw=1))
ax.annotate(f"{ep_tl:.2f} pts",
            xy=(-HALF_WIDTH, y_tl), xytext=(-HALF_WIDTH + 4, y_tl - 1.5),
            color="white", fontsize=9, fontweight="bold",
            arrowprops=dict(arrowstyle="->", color="white", lw=1))

# ── Title & layout ────────────────────────────────────────────────────────────
ax.set_title(
    "Expected Points (Try + Conversion) by Lateral Try Location\n"
    "Curve height in in-goal = EP above 5 pts baseline  ·  "
    "13,338 conversion attempts · 2000–2012",
    fontsize=12, color="black", pad=10
)

ax.set_xlim(-HALF_WIDTH - 7, HALF_WIDTH + 5)
ax.set_ylim(Y_BOT - 1.5, Y_TOP + 1)
ax.set_aspect("equal")

# x-axis labels (lateral metres)
ax.set_xticks([-35, -25, -15, -5, 0, 5, 15, 25, 35])
ax.set_xticklabels(
    ["TL\n−35", "−25", "−15", "−5", "0\n(posts)", "5", "15", "25", "TL\n35"],
    color="black", fontsize=8.5
)
ax.xaxis.set_ticks_position("bottom")
ax.set_xlabel("Lateral position along try line  (m from goal posts)", fontsize=11)
ax.yaxis.set_visible(False)
ax.spines[:].set_visible(False)

fig.tight_layout()
out = "expected_points_pitch.png"
fig.savefig(out, dpi=150, bbox_inches="tight", facecolor="#2d6a2d")
print(f"Saved → {out}")
