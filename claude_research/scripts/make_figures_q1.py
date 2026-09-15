#!/usr/bin/env python3
"""Publication figures for the phosphorus 1-10 mg/L re-analysis."""
import os
import json
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
R = json.load(open(f"{ROOT}/models/phosphorus_q1_revalidation.json"))

# validated categorical slots (dataviz reference palette, light mode)
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
    "legend.frameon": False, "legend.fontsize": 8,
    "savefig.dpi": 300, "savefig.bbox": "tight",
})

C = np.array(R["dataset"]["concentrations"])
A_red = np.array(R["dataset"]["A_red"])
A_white = np.array(R["dataset"]["A_white"])
M = R["models"]
grid = np.linspace(0.5, 10.5, 400)

lin_p = M["Linear_BeerLambert"]["params"]
qua_p = M["Quadratic"]["params"]
lan_p = M["Langmuir"]["params"]
SAT = 6.0  # onset of the saturated / non-invertible zone


def shade_sat(ax):
    ax.axvspan(SAT, 10.6, color="#f0efe9", zorder=0)


# ---------------------------------------------------------------- Figure 1
fig, ax = plt.subplots(figsize=(6.6, 4.3))
shade_sat(ax)
ax.plot(grid, lin_p[0] * grid + lin_p[1], color=GREY, lw=2, ls="--", zorder=2)
ax.plot(grid, qua_p[0] * grid**2 + qua_p[1] * grid + qua_p[2], color=ORANGE, lw=2, zorder=3)
ax.plot(grid, lan_p[0] * grid / (lan_p[1] + grid), color=BLUE, lw=2, zorder=3)
ax.plot(C, A_red, "o", ms=8, mfc="white", mec=INK, mew=1.6, zorder=5)

vx = R["firmware_root_selection_bug"]["vertex_C_mg_L"]
vy = R["firmware_root_selection_bug"]["vertex_A"]
ax.plot([vx], [vy], marker="v", ms=8, color=ORANGE, zorder=6)
ax.annotate(f"parabola vertex\n{vx:.2f} mg/L", (vx, vy), xytext=(vx - 2.9, vy + 0.055),
            fontsize=7.5, color=ORANGE, ha="left",
            arrowprops=dict(arrowstyle="-", color=ORANGE, lw=0.8))

ax.text(9.9, 0.105, "saturated zone\n(dA/dC ≈ 0)", ha="right", va="bottom",
        fontsize=7.5, color=INK2, style="italic")
ax.text(9.6, lin_p[0] * 9.6 + lin_p[1] + 0.012, "linear", color="#75746f", fontsize=8, ha="right")
ax.text(5.1, qua_p[0] * 5.1**2 + qua_p[1] * 5.1 + qua_p[2] - 0.055, "quadratic",
        color=ORANGE, fontsize=8)
ax.text(2.35, lan_p[0] * 2.35 / (lan_p[1] + 2.35) - 0.055, "Langmuir", color=BLUE, fontsize=8)

ax.set_xlabel("Phosphorus concentration (mg L$^{-1}$)")
ax.set_ylabel("Absorbance, red channel (AU)")
ax.set_title("Calibration of the molybdenum blue response, 1.0–10.0 mg L$^{-1}$")
ax.set_xlim(0.4, 10.6); ax.set_ylim(0.05, 0.60)
ax.xaxis.set_major_locator(MultipleLocator(2))
ax.text(0.0, -0.20, "n = 6 standards, single measurement per level. Curves fitted to the "
        "measured points; shading marks the range where the response is no longer invertible.",
        transform=ax.transAxes, fontsize=7.2, color=INK2, va="top")
fig.savefig(f"{ROOT}/figures/fig1_calibration_curves.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 2
fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9))

ax = axes[0]
order = [("Linear_BeerLambert", GREY, "Linear"), ("Quadratic", ORANGE, "Quadratic"),
         ("Langmuir", BLUE, "Langmuir")]
for key, col, lab in order:
    ax.plot(C, M[key]["residual_abs"], "o-", color=col, lw=1.6, ms=6, label=lab,
            mfc="white", mew=1.4, mec=col)
ax.axhline(0, color=INK, lw=1)
ax.set_xlabel("Phosphorus concentration (mg L$^{-1}$)")
ax.set_ylabel("Residual in absorbance (AU)")
ax.set_title("(a) Residual structure")
ax.legend(loc="lower right")
ax.xaxis.set_major_locator(MultipleLocator(2))

ax = axes[1]
shade_sat(ax)
ax.plot([0, 11], [0, 11], color=INK, lw=1, ls=":", zorder=1)
for key, col, lab in order:
    ax.plot(C, M[key]["pred_conc"], "o", color=col, ms=7, label=lab,
            mfc="white", mew=1.6, mec=col, zorder=4)
ax.set_xlabel("True concentration (mg L$^{-1}$)")
ax.set_ylabel("Predicted concentration (mg L$^{-1}$)")
ax.set_title("(b) Inverse prediction vs. 1:1 line")
ax.set_xlim(0, 11); ax.set_ylim(0, 11)
ax.legend(loc="upper left")
ax.text(10.4, 0.6, "saturated", ha="right", fontsize=7.5, color=INK2, style="italic")
fig.savefig(f"{ROOT}/figures/fig2_residuals_and_inverse.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 3
fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9))

S = R["sensitivity"]
ax = axes[0]
seg, dv = S["segments"], np.array(S["dA_dC"])
cols = [BLUE if v > 0.03 else ORANGE for v in dv]
bars = ax.bar(seg, dv, color=cols, width=0.62)
for b, v in zip(bars, dv):
    ax.text(b.get_x() + b.get_width() / 2, v + (0.0035 if v >= 0 else -0.008),
            f"{v:.4f}", ha="center", va="bottom" if v >= 0 else "top",
            fontsize=7.6, color=INK)
ax.axhline(0, color=INK, lw=1)
ax.set_xlabel("Concentration interval (mg L$^{-1}$)")
ax.set_ylabel("Local sensitivity dA/dC (AU per mg L$^{-1}$)")
ax.set_title("(a) Sensitivity collapse above 6 mg L$^{-1}$")
ax.tick_params(axis="x", labelsize=7.6)
ax.set_ylim(-0.02, 0.112)

ax = axes[1]
L = R["linear_low_range"]
cl = np.array([0.0, 0.2, 0.4, 0.6, 0.8])
al = L["slope"] * cl + L["intercept"]
ax.plot(cl, al, "o-", color=AQUA, lw=2, ms=7, mfc="white", mew=1.6, mec=AQUA)
ax.plot(C[:3], A_red[:3], "s--", color=VIOLET, lw=2, ms=7, mfc="white", mew=1.6, mec=VIOLET)
ax.text(0.18, 0.27, f"0–0.8 mg/L set\nslope {L['slope']:.4f} AU/(mg/L)", color=AQUA, fontsize=8)
ax.text(2.25, 0.105, f"1–10 mg/L set\nslope {S['dA_dC'][0]:.4f} AU/(mg/L)", color=VIOLET, fontsize=8)
ax.set_xlabel("Phosphorus concentration (mg L$^{-1}$)")
ax.set_ylabel("Absorbance, red channel (AU)")
ax.set_title("(b) Slope discontinuity between the two data sets")
ax.set_xlim(-0.15, 4.4); ax.set_ylim(0, 0.42)
fig.savefig(f"{ROOT}/figures/fig3_sensitivity_and_discontinuity.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 4
B = R["firmware_root_selection_bug"]
fig, ax = plt.subplots(figsize=(6.6, 4.0))
x = np.arange(len(C)); w = 0.38
ax.bar(x - w / 2, B["shipped_output_mg_L"], w, color=ORANGE, label="Shipped branch  (−b − √D)/(2a)")
ax.bar(x + w / 2, B["correct_output_mg_L"], w, color=BLUE, label="Correct branch  (−b + √D)/(2a)")
ax.plot(x, C, "D", color=INK, ms=7, label="True concentration", zorder=5)
for xi, v in zip(x, B["shipped_output_mg_L"]):
    ax.text(xi - w / 2, v + 0.18, f"{v:.1f}", ha="center", fontsize=7.4, color=ORANGE)
for xi, v in zip(x, B["correct_output_mg_L"]):
    ax.text(xi + w / 2, v + 0.18, f"{v:.1f}", ha="center", fontsize=7.4, color=BLUE)
ax.set_xticks(x); ax.set_xticklabels([f"{c:.0f}" for c in C])
ax.set_xlabel("True phosphorus concentration (mg L$^{-1}$)")
ax.set_ylabel("Concentration returned by the model (mg L$^{-1}$)")
ax.set_title("Root selection in the quadratic inversion", pad=26)
ax.set_ylim(0, 11.6)
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.02), ncol=3,
          handlelength=1.4, columnspacing=1.4, borderaxespad=0)
ax.text(0.0, -0.19, f"RMSE as shipped {B['shipped_RMSE_conc']:.2f} mg L$^{{-1}}$  ·  "
        f"RMSE with the correct branch {B['correct_RMSE_conc']:.2f} mg L$^{{-1}}$. "
        "The shipped branch saturates at the 10.0 mg/L clamp for every standard up to 6 mg/L.",
        transform=ax.transAxes, fontsize=7.2, color=INK2, va="top")
fig.savefig(f"{ROOT}/figures/fig4_root_selection.png")
plt.close(fig)

# ---------------------------------------------------------------- Figure 5
fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9))
keys = ["Linear_BeerLambert", "White_Linear", "DualChannel_Differential", "Quadratic", "Langmuir"]
names = ["Linear\n(red)", "Linear\n(white)", "Dual-channel\nΔA", "Quadratic", "Langmuir"]

ax = axes[0]
fit = [M[k]["RMSE_conc"] for k in keys]
loo = [M[k].get("LOOCV_RMSE_conc", np.nan) for k in keys]
x = np.arange(len(keys)); w = 0.38
ax.bar(x - w / 2, fit, w, color=AQUA, label="Fitted (resubstitution)")
ax.bar(x + w / 2, loo, w, color=VIOLET, label="Leave-one-out CV")
for xi, v in zip(x, fit):
    ax.text(xi - w / 2, v + 0.03, f"{v:.2f}", ha="center", fontsize=7.4, color=INK)
for xi, v in zip(x, loo):
    if np.isfinite(v):
        ax.text(xi + w / 2, v + 0.03, f"{v:.2f}", ha="center", fontsize=7.4, color=INK)
ax.set_xticks(x); ax.set_xticklabels(names, fontsize=7.6)
ax.set_ylabel("RMSE in concentration (mg L$^{-1}$)")
ax.set_title("(a) Fitted vs. cross-validated error")
ax.legend(loc="upper right"); ax.set_ylim(0, 2.3)

ax = axes[1]
sc = M["DualChannel_Differential"]["alpha_sensitivity"]
a_vals = sorted(float(k) for k in sc)
rm = [sc[str(a) if str(a) in sc else a]["RMSE_conc"] for a in a_vals]
ax.plot(a_vals, rm, "o-", color=BLUE, lw=2, ms=7, mfc="white", mew=1.6, mec=BLUE)
i04 = a_vals.index(0.4)
ax.plot([0.4], [rm[i04]], "o", ms=11, mfc="none", mec=ORANGE, mew=2)
ax.annotate("α = 0.40 as published", (0.4, rm[i04]), xytext=(0.06, rm[i04] + 0.19),
            fontsize=8, color=ORANGE,
            arrowprops=dict(arrowstyle="->", color=ORANGE, lw=1))
ax.set_xlabel("Turbidity compensation coefficient α")
ax.set_ylabel("RMSE in concentration (mg L$^{-1}$)")
ax.set_title("(b) The choice of α was not optimised")
ax.set_ylim(1.0, 1.75)
fig.savefig(f"{ROOT}/figures/fig5_model_comparison.png")
plt.close(fig)

print("figures written:")
import os
for f in sorted(os.listdir(f"{ROOT}/figures")):
    print("  ", f, os.path.getsize(f"{ROOT}/figures/{f}"), "bytes")
