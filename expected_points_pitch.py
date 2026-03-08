"""
Expected points (try + conversion) vs. lateral try location,
rendered on a top-down rugby pitch diagram.

Data
----
Same source as conversion_probability.py: 13,338 conversion attempts
from goal_kicking_data.csv (WhartonSABI/rugby-ep, Quarrie & Hopkins,
2000-2012).  Spline is fit to empirical 2.5 m bins.

Layout
------
- Top panel  : top-down pitch with a heat-gradient bar along the try line
               coloured by expected points.
- Bottom panel: EP curve sharing the same x-axis as the pitch.

Pitch dimensions (World Rugby standard)
  width  : 70 m  (posts at X = 35 m  →  half-width = 35 m from centre)
"""

import matplotlib
matplotlib.use("Agg")

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.collections import LineCollection
from matplotlib.colors import Normalize
import matplotlib.cm as cm
from scipy.interpolate import UnivariateSpline

# ---------------------------------------------------------------------------
# Load & aggregate empirical conversion data
# ---------------------------------------------------------------------------
df   = pd.read_csv("goal_kicking_data.csv")
conv = df[df["Type"] == 2].copy()
conv["lateral_m"] = (conv["X1 Metres"] - 35).abs()

bins = np.arange(0, 37.5, 2.5)
conv["bin"] = pd.cut(conv["lateral_m"], bins=bins, include_lowest=True)
agg = (
    conv.groupby("bin", observed=True)
        .agg(attempts=("Quality", "count"), made=("Quality", lambda x: (x == 1).sum()))
)
agg["prob"]    = agg["made"] / agg["attempts"]
agg["bin_mid"] = [i.mid for i in agg.index]

bin_mid = agg["bin_mid"].values
bin_p   = agg["prob"].values
n       = agg["attempts"].values

# Fit weighted smoothing spline
spl = UnivariateSpline(bin_mid, bin_p, w=np.sqrt(n), k=3, s=len(bin_mid))

# Symmetric lateral positions across the full pitch width
HALF_WIDTH = 35.0
lat    = np.linspace(-HALF_WIDTH, HALF_WIDTH, 700)
p_conv = np.clip(spl(np.abs(lat)), 0, 1)
ep     = 5 + 2 * p_conv

EP_MIN, EP_MAX = ep.min(), ep.max()

# ---------------------------------------------------------------------------
# Figure: two-row layout
# ---------------------------------------------------------------------------
fig = plt.figure(figsize=(13, 10))
gs  = fig.add_gridspec(2, 1, height_ratios=[1.6, 1], hspace=0.08)

ax_pitch = fig.add_subplot(gs[0])
ax_curve = fig.add_subplot(gs[1], sharex=ax_pitch)

# ── Pitch geometry ────────────────────────────────────────────────────────────
IN_GOAL    = 10.0
TRY_LINE_Y = 0.0
Y_BOT      = -IN_GOAL
Y_TOP      = 30.0

# Alternating grass stripes
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

# White lines
line_kw = dict(color="white", lw=1.5, zorder=3)
ax_pitch.axvline(-HALF_WIDTH, **line_kw)
ax_pitch.axvline( HALF_WIDTH, **line_kw)
ax_pitch.axhline(TRY_LINE_Y, color="white", lw=3, zorder=4)
ax_pitch.axhline(Y_BOT, **line_kw)
for y in [5, 10, 22]:
    ax_pitch.axhline(y, color="white", lw=0.8, ls="--", alpha=0.5, zorder=3)
    ax_pitch.text(HALF_WIDTH + 0.5, y, f"{y} m", color="white",
                  fontsize=7.5, va="center", zorder=5)

# Goal posts (5.6 m between uprights)
POST_SEP = 5.6 / 2
post_kw  = dict(color="yellow", lw=3, zorder=6)
ax_pitch.plot([-POST_SEP, -POST_SEP], [Y_BOT, 0], **post_kw)
ax_pitch.plot([ POST_SEP,  POST_SEP], [Y_BOT, 0], **post_kw)
ax_pitch.plot([-POST_SEP,  POST_SEP], [0, 0],     **post_kw)

# ── Heat-gradient bar along the try line ─────────────────────────────────────
BAR_HEIGHT = 4.0
cmap = cm.RdYlGn
norm = Normalize(vmin=EP_MIN, vmax=EP_MAX)

points   = np.array([lat, np.full_like(lat, -BAR_HEIGHT / 2)]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
lc = LineCollection(segments, cmap=cmap, norm=norm, linewidth=8, zorder=7)
lc.set_array(ep[:-1])
ax_pitch.add_collection(lc)

cbar = fig.colorbar(lc, ax=ax_pitch, orientation="horizontal",
                    fraction=0.035, pad=0.01, aspect=40)
cbar.set_label("Expected points (try + conversion)", color="white", fontsize=9)
cbar.ax.xaxis.set_tick_params(color="white")
plt.setp(cbar.ax.xaxis.get_ticklabels(), color="white", fontsize=8)

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
ax_pitch.set_title(
    "Expected Points from Try + Conversion by Lateral Try Location\n"
    "Empirical data · 13,338 conversion attempts · 2000–2012 (WhartonSABI / Quarrie & Hopkins)",
    fontsize=13, color="black", pad=8
)

# ── Bottom panel: EP curve ────────────────────────────────────────────────────
ax_curve.set_facecolor("#f5f5f5")
ax_curve.fill_between(lat, 5, ep, alpha=0.20, color="#4caf50")

points2   = np.array([lat, ep]).T.reshape(-1, 1, 2)
segments2 = np.concatenate([points2[:-1], points2[1:]], axis=1)
lc2 = LineCollection(segments2, cmap=cmap, norm=norm, linewidth=3, zorder=4)
lc2.set_array(ep[:-1])
ax_curve.add_collection(lc2)

# Overlay raw empirical EP dots (symmetric)
ep_raw = 5 + 2 * bin_p
ax_curve.scatter(bin_mid,  ep_raw, s=n/10, color="#1a6faf", zorder=5,
                 alpha=0.75, label="Empirical bins (size ∝ n)")
ax_curve.scatter(-bin_mid, ep_raw, s=n/10, color="#1a6faf", zorder=5,
                 alpha=0.75)

# Baselines
ax_curve.axhline(5, color="#888", lw=1.2, ls="--", zorder=3)
ax_curve.text(HALF_WIDTH - 1, 5.03, "Try alone (5 pts)", color="#555",
              fontsize=8.5, ha="right", va="bottom")

for xv in [-POST_SEP, POST_SEP]:
    ax_curve.axvline(xv, color="goldenrod", lw=1.2, ls=":", zorder=3)

# Annotations
ep_centre  = float(spl(0))
ep_centre  = np.clip(ep_centre, 0, 1)
ep_pts_ctr = 5 + 2 * ep_centre
ep_pts_tl  = float(ep[0])

ax_curve.annotate(f"Centre: {ep_pts_ctr:.2f} pts",
                  xy=(0, ep_pts_ctr), xytext=(4, ep_pts_ctr + 0.25),
                  arrowprops=dict(arrowstyle="->", color="#333"), fontsize=9)
ax_curve.annotate(f"Touchline: {ep_pts_tl:.2f} pts",
                  xy=(-HALF_WIDTH, ep_pts_tl), xytext=(-HALF_WIDTH + 3, ep_pts_tl + 0.25),
                  arrowprops=dict(arrowstyle="->", color="#333"), fontsize=9)

ax_curve.set_xlim(-HALF_WIDTH - 2, HALF_WIDTH + 6)
ax_curve.set_ylim(4.8, 7.2)
ax_curve.set_xlabel("Lateral position along try line  (m from centre / goal posts)", fontsize=11)
ax_curve.set_ylabel("Expected points", fontsize=11)
ax_curve.xaxis.set_major_locator(plt.MultipleLocator(5))
ax_curve.grid(axis="y", ls="--", alpha=0.4)
ax_curve.legend(fontsize=9)

# Touchline tick labels
xticks = list(ax_curve.get_xticks())
for xv in [-HALF_WIDTH, HALF_WIDTH]:
    if xv not in xticks:
        xticks.append(xv)
ax_curve.set_xticks(xticks)
ax_curve.set_xticklabels(
    ["TL" if t in (-HALF_WIDTH, HALF_WIDTH) else f"{int(t)}" for t in xticks],
    fontsize=8
)

fig.tight_layout()
out = "expected_points_pitch.png"
fig.savefig(out, dpi=150, bbox_inches="tight")
print(f"Saved → {out}")
