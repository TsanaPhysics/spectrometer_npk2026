#!/usr/bin/env python3
"""
Rigorous re-analysis of the 1.0-10.0 mg/L phosphorus calibration.
Adds: adjusted R2, AICc, leave-one-out cross-validation, inverse-prediction
error, residual diagnostics, LOD/LOQ from the linear 0-1 mg/L range,
and replicate precision from spiked vermicompost samples.

Chewa Thassana, Digital Agriculture and Environment Programme,
Faculty of Science and Technology, Rambhai Barni Rajabhat University.
"""
import os
import json
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
from scipy import stats

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = f"{ROOT}/data"

# ---------------------------------------------------------------- load data
kin = pd.read_csv(f"{D}/phosphorus_1_10_reagent_kinetics.csv")
C = kin["concentration_mg_L"].to_numpy(float)
A_red = kin["abs_red"].to_numpy(float)
A_white = kin["abs_white"].to_numpy(float)
A_green = kin["abs_green"].to_numpy(float)
A_blue = kin["abs_blue"].to_numpy(float)
n = len(C)

std = pd.read_csv(f"{D}/master_chemical_standards.csv")
P_low = std[(std.analyte == "Phosphorus") & (std.concentration_mg_L <= 0.8)]
C_low = P_low["concentration_mg_L"].to_numpy(float)
A_low = P_low["abs_red"].to_numpy(float)


# --------------------------------------------------------------- statistics
def r2(y, yh):
    ss_res = np.sum((y - yh) ** 2)
    ss_tot = np.sum((y - np.mean(y)) ** 2)
    return 1 - ss_res / ss_tot


def r2_adj(y, yh, k):
    """k = number of fitted parameters (incl. intercept)."""
    return 1 - (1 - r2(y, yh)) * (len(y) - 1) / (len(y) - k)


def aicc(y, yh, k):
    rss = np.sum((y - yh) ** 2)
    m = len(y)
    val = m * np.log(rss / m) + 2 * k
    denom = m - k - 1
    return val + (2 * k * (k + 1) / denom) if denom > 0 else np.inf


def rmse(y, yh):
    return float(np.sqrt(np.mean((y - yh) ** 2)))


def mae(y, yh):
    return float(np.mean(np.abs(y - yh)))


# ------------------------------------------------------------- model forms
def f_linear(c, m, b):
    return m * c + b


def f_quad(c, a, b, cc):
    return a * c ** 2 + b * c + cc


def f_langmuir(c, amax, kd):
    return amax * c / (kd + c)


def inv_linear(a, p):
    m, b = p
    return (a - b) / m


def inv_quad(a, p):
    """Ascending branch of the downward parabola (a < 0).

    NOTE: the branch shipped in phosphorus_q1_models.h uses (-b - sqrt(D))/(2a),
    which selects the DESCENDING branch beyond the vertex and therefore returns
    concentrations above the vertex for every real sample. The correct branch for
    a < 0 is (-b + sqrt(D))/(2a). Both are computed below for comparison.
    """
    aa, bb, cc = p
    disc = np.maximum(bb ** 2 - 4 * aa * (cc - a), 0.0)
    return (-bb + np.sqrt(disc)) / (2 * aa)


def inv_quad_firmware(a, p):
    aa, bb, cc = p
    disc = np.maximum(bb ** 2 - 4 * aa * (cc - a), 0.0)
    return np.clip((-bb - np.sqrt(disc)) / (2 * aa), 1.0, 10.0)


def inv_langmuir(a, p):
    amax, kd = p
    denom = np.maximum(amax - a, 1e-3)
    return kd * a / denom


MODELS = {
    "Linear_BeerLambert": dict(f=f_linear, inv=inv_linear, p0=[0.05, 0.1], k=2,
                               x=A_red, label="Baseline linear (Beer-Lambert, red)"),
    "Quadratic": dict(f=f_quad, inv=inv_quad, p0=[-0.007, 0.12, 0.0], k=3,
                      x=A_red, label="Quadratic polynomial inversion (red)"),
    "Langmuir": dict(f=f_langmuir, inv=inv_langmuir, p0=[0.8, 5.0], k=2,
                     x=A_red, label="Langmuir saturation isotherm (red)"),
}

results = {}
for name, spec in MODELS.items():
    popt, pcov = curve_fit(spec["f"], C, spec["x"], p0=spec["p0"], maxfev=200000)
    yh = spec["f"](C, *popt)
    perr = np.sqrt(np.diag(pcov))

    # inverse prediction (absorbance -> concentration), the quantity that matters
    Cp = spec["inv"](spec["x"], popt)
    Cp = np.clip(Cp, 0.0, 20.0)

    # leave-one-out cross-validation on the inverse prediction
    loo_err = []
    for i in range(n):
        m = np.ones(n, bool)
        m[i] = False
        try:
            p_i, _ = curve_fit(spec["f"], C[m], spec["x"][m], p0=spec["p0"], maxfev=200000)
            c_i = float(np.clip(spec["inv"](spec["x"][i], p_i), 0.0, 20.0))
            loo_err.append(c_i - C[i])
        except Exception:
            loo_err.append(np.nan)
    loo_err = np.array(loo_err, float)

    results[name] = dict(
        label=spec["label"],
        params=[float(v) for v in popt],
        param_se=[float(v) for v in perr],
        n_params=spec["k"],
        R2_abs=float(r2(spec["x"], yh)),
        R2_adj_abs=float(r2_adj(spec["x"], yh, spec["k"])),
        RMSE_abs=rmse(spec["x"], yh),
        MAE_abs=mae(spec["x"], yh),
        AICc=float(aicc(spec["x"], yh, spec["k"])),
        R2_conc=float(r2(C, Cp)),
        RMSE_conc=rmse(C, Cp),
        MAE_conc=mae(C, Cp),
        max_abs_err_conc=float(np.max(np.abs(Cp - C))),
        pred_conc=[float(v) for v in Cp],
        residual_abs=[float(v) for v in (spec["x"] - yh)],
        LOOCV_RMSE_conc=float(np.sqrt(np.nanmean(loo_err ** 2))),
        LOOCV_max_err=float(np.nanmax(np.abs(loo_err))),
    )

# ------------------------- firmware root-selection bug: quantified side by side
p_q = results["Quadratic"]["params"]
vertex_C = -p_q[1] / (2 * p_q[0])
vertex_A = p_q[0] * vertex_C ** 2 + p_q[1] * vertex_C + p_q[2]
C_fw = inv_quad_firmware(A_red, p_q)
firmware_bug = dict(
    shipped_branch="C = (-b - sqrt(b^2 - 4a(c - A))) / (2a)",
    correct_branch="C = (-b + sqrt(b^2 - 4a(c - A))) / (2a)   for a < 0",
    vertex_C_mg_L=float(vertex_C), vertex_A=float(vertex_A),
    shipped_output_mg_L=[float(v) for v in C_fw],
    correct_output_mg_L=results["Quadratic"]["pred_conc"],
    true_C=[float(v) for v in C],
    shipped_RMSE_conc=rmse(C, C_fw),
    correct_RMSE_conc=results["Quadratic"]["RMSE_conc"],
    consequence=("As shipped, predict_phosphorus_option1_quadratic() returns the "
                 "clamp ceiling 10.0 mg/L for every standard from 1.0 to 6.0 mg/L."),
)

# --------------------------------------- Option 3: dual-channel differential
alpha = 0.40
dA = A_red - alpha * A_white
p_d, cov_d = curve_fit(f_linear, C, dA, p0=[0.03, 0.1], maxfev=200000)
dA_hat = f_linear(C, *p_d)
Cp_d = np.clip(inv_linear(dA, p_d), 0, 20)
loo_d = []
for i in range(n):
    m = np.ones(n, bool)
    m[i] = False
    p_i, _ = curve_fit(f_linear, C[m], dA[m], p0=[0.03, 0.1], maxfev=200000)
    loo_d.append(float(np.clip(inv_linear(dA[i], p_i), 0, 20)) - C[i])
loo_d = np.array(loo_d)

# alpha sensitivity: how much does the answer move with the chosen alpha?
alpha_scan = {}
for a_try in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
    d_try = A_red - a_try * A_white
    p_t, _ = curve_fit(f_linear, C, d_try, p0=[0.03, 0.1], maxfev=200000)
    c_t = np.clip(inv_linear(d_try, p_t), 0, 20)
    alpha_scan[a_try] = dict(R2_signal=float(r2(d_try, f_linear(C, *p_t))),
                             RMSE_conc=rmse(C, c_t))

results["DualChannel_Differential"] = dict(
    label="Dual-channel differential (A_red - 0.40 A_white)",
    params=[float(v) for v in p_d],
    param_se=[float(v) for v in np.sqrt(np.diag(cov_d))],
    n_params=2,
    alpha=alpha,
    R2_abs=float(r2(dA, dA_hat)),
    R2_adj_abs=float(r2_adj(dA, dA_hat, 2)),
    RMSE_abs=rmse(dA, dA_hat),
    MAE_abs=mae(dA, dA_hat),
    AICc=float(aicc(dA, dA_hat, 2)),
    R2_conc=float(r2(C, Cp_d)),
    RMSE_conc=rmse(C, Cp_d),
    MAE_conc=mae(C, Cp_d),
    max_abs_err_conc=float(np.max(np.abs(Cp_d - C))),
    pred_conc=[float(v) for v in Cp_d],
    residual_abs=[float(v) for v in (dA - dA_hat)],
    LOOCV_RMSE_conc=float(np.sqrt(np.mean(loo_d ** 2))),
    LOOCV_max_err=float(np.max(np.abs(loo_d))),
    alpha_sensitivity=alpha_scan,
)

# white channel on its own (Option 3a)
p_w, _ = curve_fit(f_linear, C, A_white, p0=[0.04, 0.07], maxfev=200000)
Cp_w = np.clip(inv_linear(A_white, p_w), 0, 20)
results["White_Linear"] = dict(
    label="Broadband white channel, linear",
    params=[float(v) for v in p_w], n_params=2,
    R2_abs=float(r2(A_white, f_linear(C, *p_w))),
    R2_adj_abs=float(r2_adj(A_white, f_linear(C, *p_w), 2)),
    RMSE_abs=rmse(A_white, f_linear(C, *p_w)),
    MAE_abs=mae(A_white, f_linear(C, *p_w)),
    AICc=float(aicc(A_white, f_linear(C, *p_w), 2)),
    R2_conc=float(r2(C, Cp_w)), RMSE_conc=rmse(C, Cp_w), MAE_conc=mae(C, Cp_w),
    max_abs_err_conc=float(np.max(np.abs(Cp_w - C))),
    pred_conc=[float(v) for v in Cp_w],
    residual_abs=[float(v) for v in (A_white - f_linear(C, *p_w))],
)

# -------------------------------------------- LOD / LOQ from linear 0-1 range
sl = stats.linregress(C_low, A_low)
resid_low = A_low - (sl.slope * C_low + sl.intercept)
dof = len(C_low) - 2
s_yx = float(np.sqrt(np.sum(resid_low ** 2) / dof))
LOD = 3.3 * s_yx / sl.slope
LOQ = 10.0 * s_yx / sl.slope
low_range = dict(
    slope=float(sl.slope), intercept=float(sl.intercept),
    R2=float(sl.rvalue ** 2), slope_se=float(sl.stderr),
    s_yx=s_yx, LOD_mg_L=float(LOD), LOQ_mg_L=float(LOQ), n=int(len(C_low)),
    note="Linear range 0.0-0.8 mg/L, red channel; LOD=3.3*s_y/x/slope, LOQ=10*s_y/x/slope",
)

# --------------------------------- sensitivity loss / saturation diagnostics
dCdA_local = np.diff(A_red) / np.diff(C)
sens = dict(
    segments=[f"{C[i]:.1f}-{C[i+1]:.1f}" for i in range(n - 1)],
    dA_dC=[float(v) for v in dCdA_local],
    sensitivity_retained_pct=float(100 * dCdA_local[-1] / dCdA_local[0]),
    low_range_slope=float(sl.slope),
    slope_drop_vs_low_range_pct=float(100 * (1 - dCdA_local[0] / sl.slope)),
)

# --------------------------------------------- replicate precision (spiked)
sp = pd.read_csv(f"{D}/master_spiked_samples.csv")
prec = {}
for (an, vol), g in sp.groupby(["spiked_analyte", "spike_volume_ml"]):
    if len(g) < 2:
        continue
    for ch in ["net_red", "net_green", "net_blue", "net_clear"]:
        v = g[ch].to_numpy(float)
        prec[f"{an}_{vol}mL_{ch}"] = dict(
            n=int(len(v)), mean=float(v.mean()), sd=float(v.std(ddof=1)),
            rsd_pct=float(100 * v.std(ddof=1) / v.mean()))

# ------------------------------------------- channel diagnostics (blue flat)
blue_diag = dict(
    unique_values=[float(v) for v in np.unique(A_blue)],
    n_unique=int(len(np.unique(A_blue))),
    note=("abs_blue is pinned at a single value (0.09691 = -log10(0.8)) for 5 of 6 "
          "standards, i.e. the blue transmittance ratio is quantised at exactly 0.8. "
          "This is an ADC/gain artefact, not a chemical signal; the blue channel "
          "carries no usable information in this range."),
)

out = dict(
    dataset=dict(n_levels=n, concentrations=[float(v) for v in C],
                 A_red=[float(v) for v in A_red],
                 A_white=[float(v) for v in A_white],
                 A_green=[float(v) for v in A_green],
                 replicates_per_level=1,
                 caveat="Single measurement per level; no within-level SD available."),
    models=results,
    linear_low_range=low_range,
    sensitivity=sens,
    replicate_precision_spiked=prec,
    blue_channel_diagnostic=blue_diag,
    firmware_root_selection_bug=firmware_bug,
)

with open(f"{ROOT}/models/phosphorus_q1_revalidation.json", "w") as fh:
    json.dump(out, fh, indent=2, ensure_ascii=False)

# ------------------------------------------------------------------ console
print("=" * 78)
print(f"{'MODEL':<34}{'R2abs':>8}{'R2adj':>8}{'AICc':>9}{'RMSE_C':>9}{'LOOCV':>9}")
print("=" * 78)
for k, v in results.items():
    print(f"{k:<34}{v['R2_abs']:>8.4f}{v['R2_adj_abs']:>8.4f}{v['AICc']:>9.2f}"
          f"{v['RMSE_conc']:>9.3f}{v.get('LOOCV_RMSE_conc', float('nan')):>9.3f}")
print("=" * 78)
print("Langmuir params: Amax = %.4f +- %.4f Abs ; Kd = %.3f +- %.3f mg/L"
      % (results["Langmuir"]["params"][0], results["Langmuir"]["param_se"][0],
         results["Langmuir"]["params"][1], results["Langmuir"]["param_se"][1]))
print("Low range (0-0.8): slope %.5f Abs/(mg/L), R2 %.5f, LOD %.3f, LOQ %.3f mg/L"
      % (sl.slope, sl.rvalue ** 2, LOD, LOQ))
print("Local dA/dC:", np.round(dCdA_local, 4), "-> retained %.1f%%"
      % sens["sensitivity_retained_pct"])
print("alpha sensitivity (Option 3):")
for a_try, d in alpha_scan.items():
    print(f"   alpha={a_try:.1f}  R2_signal={d['R2_signal']:.4f}  RMSE_C={d['RMSE_conc']:.3f}")
print("FIRMWARE BUG  shipped:", [round(v,2) for v in firmware_bug['shipped_output_mg_L']],
      " RMSE=%.3f"%firmware_bug['shipped_RMSE_conc'])
print("              correct:", [round(v,2) for v in firmware_bug['correct_output_mg_L']],
      " RMSE=%.3f"%firmware_bug['correct_RMSE_conc'])
print("              vertex at C=%.2f mg/L, A=%.4f"%(firmware_bug['vertex_C_mg_L'],firmware_bug['vertex_A']))
print("Spiked P repeatability (1.0 mL, net_red):",
      {k: round(v['rsd_pct'], 2) for k, v in prec.items() if k.startswith('P_1.0mL_net_red')})
