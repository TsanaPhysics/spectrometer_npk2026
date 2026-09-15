#!/usr/bin/env python3
"""Figure 6 - wavelength audit: what the instrument illuminates and detects
versus where the analytes actually absorb."""
import os
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

BLUE, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"
GREY, INK, INK2 = "#b8b7b2", "#0b0b0b", "#52514e"
SURF = "#fcfcfb"

plt.rcParams.update({
    "figure.facecolor": SURF, "axes.facecolor": SURF, "savefig.facecolor": SURF,
    "font.family": "DejaVu Sans", "font.size": 9,
    "axes.edgecolor": "#8a8a85", "axes.linewidth": 0.8,
    "axes.labelcolor": INK, "text.color": INK,
    "xtick.color": INK2, "ytick.color": INK2,
    "xtick.labelsize": 8.5, "ytick.labelsize": 8.5,
    "axes.titlesize": 10, "axes.titleweight": "bold", "axes.titlelocation": "left",
    "axes.grid": True, "grid.color": "#e6e5e0", "grid.linewidth": 0.7,
    "axes.spines.top": False, "axes.spines.right": False,
    "legend.frameon": False, "legend.fontsize": 7.8,
    "savefig.dpi": 300, "savefig.bbox": "tight",
})


def gauss(x, mu, sd, amp=1.0):
    return amp * np.exp(-0.5 * ((x - mu) / sd) ** 2)


fig, axes = plt.subplots(2, 1, figsize=(8.4, 7.0),
                         gridspec_kw={"height_ratios": [1.45, 1.0], "hspace": 0.42})

# ---------------------------------------------------------------- panel (a)
ax = axes[0]
wl = np.linspace(400, 950, 1200)

# NeoPixel RGB emission dies (the only three bands the device can actually emit)
led_b = gauss(wl, 465, 12)
led_g = gauss(wl, 525, 17)
led_r = gauss(wl, 625, 9)
for y, col, nm in [(led_b, BLUE, 465), (led_g, AQUA, 525), (led_r, ORANGE, 625)]:
    ax.fill_between(wl, 0, y, color=col, alpha=0.30, lw=0, zorder=2)
    ax.plot(wl, y, color=col, lw=1.6, zorder=3)
    ax.text(nm, 1.04, f"{nm}", ha="center", fontsize=7.6, color=col, fontweight="bold")

# TCS34725 red-channel responsivity (peaks near 700 nm, IR filter cuts beyond)
det_r = gauss(wl, 700, 55) * (wl < 780) + gauss(wl, 700, 55) * (wl >= 780) * np.exp(-(wl - 780) / 28)
ax.plot(wl, det_r, color=INK2, lw=1.6, ls=(0, (5, 2)), zorder=4)
ax.text(583, 0.78, "TCS34725 red-channel responsivity\n(peaks ~700 nm)", fontsize=7.4, color=INK2, ha="center")

# Sb-ascorbic acid phosphomolybdenum blue: main peak 880 nm, second peak 710 nm
pmb = 0.98 * gauss(wl, 880, 62) + 0.62 * gauss(wl, 710, 48)
pmb = pmb / pmb.max()
ax.plot(wl, pmb, color=VIOLET, lw=2.4, zorder=5)
ax.text(880, 1.04, "880", ha="center", fontsize=7.6, color=VIOLET, fontweight="bold")
ax.text(710, 0.70, "710", ha="center", fontsize=7.6, color=VIOLET, fontweight="bold")
ax.text(862, 0.22, "phosphomolybdenum blue\n(Sb–ascorbic acid)\nλmax 880 nm, 2nd peak 710 nm",
        fontsize=7.4, color=VIOLET, ha="center")

# Nessler N ~420 nm
nes = gauss(wl, 420, 30)
ax.plot(wl, nes, color="#8a8a85", lw=1.4, zorder=3)
ax.text(414, 0.60, "Nessler N\n~420 nm", fontsize=7.2, color="#75746f", ha="center")

# where P is actually measured
ax.annotate("", xy=(625, 0.02), xytext=(625, 0.90),
            arrowprops=dict(arrowstyle="-|>", color=ORANGE, lw=2.0))
ax.text(620, 0.93, "P measured here", fontsize=8, color=ORANGE, ha="right", fontweight="bold")
ax.annotate("", xy=(710, 0.02), xytext=(710, 0.62),
            arrowprops=dict(arrowstyle="-|>", color=VIOLET, lw=2.0, ls=":"))
ax.text(726, 0.05, "should be here\n(and the detector\npeaks here too)",
        fontsize=8, color=VIOLET, ha="left", fontweight="bold")

ax.axvspan(780, 950, color="#f0efe9", zorder=0)
ax.text(945, 0.60, "blocked by the sensor's\non-chip IR filter",
        fontsize=7.4, color=INK2, ha="right", style="italic")

ax.set_xlim(400, 950)
ax.set_ylim(0, 1.16)
ax.set_xlabel("Wavelength (nm)")
ax.set_ylabel("Normalised response / absorbance")
ax.set_title("(a) Illumination and detection versus where the analytes absorb")
ax.set_yticks([0, 0.5, 1.0])

# ---------------------------------------------------------------- panel (b)
ax = axes[1]
kin = pd.read_csv(f"{ROOT}/data/phosphorus_1_10_reagent_kinetics.csv")
C = kin.concentration_mg_L.values
m = C <= 6
chans = [("abs_red", "Red\n~625 nm illum.", ORANGE),
         ("abs_white", "Clear\nbroadband", GREY),
         ("abs_green", "Green\n~525 nm", AQUA),
         ("abs_blue", "Blue\n~465 nm", BLUE)]
slopes, r2s, labels, cols = [], [], [], []
for ch, lab, col in chans:
    sl = stats.linregress(C[m], kin[ch].values[m])
    slopes.append(sl.slope); r2s.append(sl.rvalue ** 2)
    labels.append(lab); cols.append(col)

x = np.arange(len(slopes))
bars = ax.bar(x, slopes, color=cols, width=0.6)
for xi, s, r in zip(x, slopes, r2s):
    ax.text(xi, s + 0.0022, f"{s:.4f}", ha="center", fontsize=8, color=INK, fontweight="bold")
    ax.text(xi, s + 0.0075, f"R² = {r:.4f}", ha="center", fontsize=7.4, color=INK2)
ax.set_xticks(x); ax.set_xticklabels(labels, fontsize=7.8)
ax.set_ylabel("Sensitivity to P, dA/dC\n(AU per mg L$^{-1}$)")
ax.set_title("(b) Measured sensitivity of each channel to phosphorus, 1–6 mg L$^{-1}$")
ax.set_ylim(0, 0.098)
ax.text(0.0, -0.30, "Computed from the project's own standards. The red channel carries the P signal, "
        "confirming the assignment is directionally right —\nbut the 625 nm source sits on the rising flank "
        "below the complex's 710 nm peak, which is why the gain must be pushed until the detector saturates.",
        transform=ax.transAxes, fontsize=7.2, color=INK2, va="top")

fig.savefig(f"{ROOT}/figures/fig6_wavelength_audit.png")
print("wrote figures/fig6_wavelength_audit.png")
