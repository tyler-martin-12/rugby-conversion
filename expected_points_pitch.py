"""
Expected points (try + conversion) vs. lateral try location,
rendered on a top-down rugby pitch diagram.

Layout
------
- Top panel  : top-down pitch with a heat-gradient bar drawn along the try line
               showing expected-point value at each lateral position.
- Bottom panel: EP curve (5 = try alone, up to ~6.94 = try + near-certain conversion)
                sharing the same x-axis as the pitch.

Pitch dimensions (approximate, World Rugby standard)
  length : 100 m playing area  + 10 m in-goal each end  = 120 m total
  width  : 70 m
"""

import matplotlib
matplotlib.use("Agg")

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
import matplotlib.cm as cm
from scipy.optimize import curve_fit

# ---------------------------------------------------------------------------
# Re-use the same logistic model + anchor points from conversion_probability.py
# ---------------------------------------------------------------------------
anchors_x = np.array([ 0,  5, 10, 15, 20, 25, 30, 35, 40], dtype=float)
anchors_p = np.array([0.97, 0.93, 0.85, 0.76, 0.65, 0.53, 0.42, 0.30, 0.20])

def logistic(x, L, x0, k, b):
    return b + (L - b) / (1 + np.exp(k * (x - x0)))

popt, _ = curve_fit(logistic, anchors_x, anchors_p, p0=[1.0, 18.0, 0.12, 0.10], maxfev=10_000)

# Lateral offsets run -35 → +35 m (full field half-width = 35 m)
# We use |offset| for the conversion probability (symmetric)
HALF_WIDTH = 35.0          # m from centre to touchline
lat = np.linspace(-HALF_WIDTH, HALF_WIDTH, 600)   # lateral positions along try line
p_conv = logistic(np.abs(lat), *popt)
ep = 5 + 2 * p_conv        # expected points

EP_MIN, EP_MAX = ep.min(), ep.max()

# ---------------------------------------------------------------------------
# Figure: two-row layout — pitch on top, curve on bottom
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13, 10))
gs  = fig.add_gridspec(2, 1, height_ratios=[1.6, 1], hspace=0.08)

ax_pitch  = fig.add_subplot(gs[0])
ax_curve  = fig.add_subplot(gs[1], sharex=ax_pitch)

# ── Pitch dimensions in "lateral metres" coordinates ─────────────────────────
PITCH_LEN   = 120.0   # total (incl. in-goals)
IN_GOAL     = 10.0    # depth of in-goal at each end
PLAY_LEN    = 100.0
TRY_LINE_Y  = 0.0     # we'll put the try line at y=0 in pitch coords
# Pitch runs from y = -IN_GOAL (attacking in-goal) to y = PLAY_LEN + IN_GOAL
# but we only need a slice around the try line for context.
# Show from -IN_GOAL to 30 m into the field.
Y_BOT = -IN_GOAL
Y_TOP = 30.0

# ── Draw pitch background ─────────────────────────────────────────────────────
ax_pitch.set_facecolor("#2d6a2d")   # grass green

# Alternating lighter/darker grass stripes (5 m bands)
stripe_colors = ["#2d6a2d", "#316e31"]
for i, y_start in enumerate(range(int(Y_BOT), int(Y_TOP), 5)):
    ax_pitch.add_patch(mpatches.Rectangle(
        (-HALF_WIDTH, y_start), 2 * HALF_WIDTH, 5,
        color=stripe_colors[i % 2], zorder=0
    ))

# In-goal shading
ax_pitch.add_patch(mpatches.Rectangle(
    (-HALF_WIDTH, Y_BOT), 2 * HALF_WIDTH, IN_GOAL,
    color="#1f4f1f", zorder=1, alpha=0.6
))

# White pitch lines
line_kw = dict(color="white", lw=1.5, zorder=3)

# Touchlines
ax_pitch.axvline(-HALF_WIDTH, **line_kw)
ax_pitch.axvline( HALF_WIDTH, **line_kw)

# Try line (y = 0) — thicker
ax_pitch.axhline(TRY_LINE_Y, color="white", lw=3, zorder=4)

# Dead-ball line
ax_pitch.axhline(Y_BOT, **line_kw)

# 5 m, 10 m, 22 m lines
for y in [5, 10, 22]:
    ax_pitch.axhline(y, color="white", lw=0.8, ls="--", alpha=0.5, zorder=3)
    ax_pitch.text(HALF_WIDTH + 0.5, y, f"{y} m", color="white",
                  fontsize=7.5, va="center", zorder=5)

# ── Goal posts (centred, 5.6 m apart) ─────────────────────────────────────────
POST_SEP = 5.6 / 2
post_kw  = dict(color="yellow", lw=3, zorder=6)
ax_pitch.plot([-POST_SEP, -POST_SEP], [Y_BOT, 0], **post_kw)
ax_pitch.plot([ POST_SEP,  POST_SEP], [Y_BOT, 0], **post_kw)
ax_pitch.plot([-POST_SEP,  POST_SEP], [0, 0],     **post_kw)  # crossbar at try line

# ── Heat-gradient bar along the try line ─────────────────────────────────────
BAR_HEIGHT = 4.0   # m into the in-goal — visual thickness of the colour strip
cmap  = cm.RdYlGn
norm  = Normalize(vmin=EP_MIN, vmax=EP_MAX)

# Build a LineCollection: one short segment per sample, coloured by EP
points  = np.array([lat, np.full_like(lat, -BAR_HEIGHT / 2)]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=8, zorder=7)
lc.set_array(ep[:-1])
ax_pitch.add_collection(lc)

# Colourbar inside the pitch axes
cbar = fig.colorbar(lc, ax=ax_pitch, orientation="horizontal",
                    fraction=0.035, pad=0.01, aspect=40)
cbar.set_label("Expected points (try + conversion)", color="white", fontsize=9)
cbar.ax.xaxis.set_tick_params(color="white")
plt.setp(cbar.ax.xaxis.get_ticklabels(), color="white", fontsize=8)

# Labels
ax_pitch.text(-HALF_WIDTH + 1, Y_BOT + 1, "IN-GOAL", color="white",
              fontsize=9, alpha=0.7, zorder=8)
ax_pitch.text(-HALF_WIDTH + 1, 0.8, "TRY LINE", color="white",
              fontsize=9, alpha=0.9, zorder=8)
ax_pitch.text(0, -BAR_HEIGHT / 2 - 0.5, "← EP gradient along try line →",
              color="white", fontsize=8, ha="center", va="top", zorder=8)

ax_pitch.set_xlim(-HALF_WIDTH - 2, HALF_WIDTH + 6)
ax_pitch.set_ylim(Y_BOT - 1, Y_TOP + 1)
ax_pitch.set_aspect("equal")
ax_pitch.axis("off")
ax_pitch.set_title("Expected Points from Try + Conversion by Lateral Try Location",
                   fontsize=14, color="black", pad=8)

# ── Bottom panel: EP curve ────────────────────────────────────────────────────
ax_curve.set_facecolor("#f5f5f5")

# Fill under curve
ax_curve.fill_between(lat, 5, ep, alpha=0.25, color="#4caf50")

# Colour the curve by EP value using a LineCollection
points2   = np.array([lat, ep]).T.reshape(-1, 1, 2)
segments2 = np.concatenate([points2[:-1], points2[1:]], axis=1)
lc2 = LineCollection(segments2, cmap=cmap, norm=norm, linewidth=3, zorder=4)
lc2.set_array(ep[:-1])
ax_curve.add_collection(lc2)

# Try-only baseline
ax_curve.axhline(5, color="#888", lw=1.2, ls="--", zorder=3)
ax_curve.text(HALF_WIDTH - 1, 5.03, "Try alone (5 pts)", color="#555",
              fontsize=8.5, ha="right", va="bottom")

# Vertical post lines
for xv in [-POST_SEP, POST_SEP]:
    ax_curve.axvline(xv, color="goldenrod", lw=1.2, ls=":", zorder=3)
ax_curve.axvline(0, color="white", lw=0.8, ls=":", zorder=3)

# Annotate peak & wing
ax_curve.annotate(f"Centre: {ep[len(ep)//2]:.2f} pts",
                  xy=(0, ep[len(ep)//2]), xytext=(5, 6.6),
                  arrowprops=dict(arrowstyle="->", color="#333"), fontsize=9)
ax_curve.annotate(f"Touchline: {ep[0]:.2f} pts",
                  xy=(-HALF_WIDTH, ep[0]), xytext=(-HALF_WIDTH + 3, 5.65),
                  arrowprops=dict(arrowstyle="->", color="#333"), fontsize=9)

ax_curve.set_xlim(-HALF_WIDTH - 2, HALF_WIDTH + 6)
ax_curve.set_ylim(4.8, 7.2)
ax_curve.set_xlabel("Lateral position along try line  (m from centre / goal posts)", fontsize=11)
ax_curve.set_ylabel("Expected points", fontsize=11)
ax_curve.xaxis.set_major_locator(plt.MultipleLocator(5))
ax_curve.grid(axis="y", ls="--", alpha=0.4)

# Touchline labels on x-axis
ax_curve.set_xticks(list(ax_curve.get_xticks()) + [-HALF_WIDTH, HALF_WIDTH])
ax_curve.set_xticklabels(
    [f"{int(t)}" if t not in (-HALF_WIDTH, HALF_WIDTH) else "TL"
     for t in ax_curve.get_xticks()],
    fontsize=8
)

fig.tight_layout()
out = "expected_points_pitch.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"Saved → {out}")
