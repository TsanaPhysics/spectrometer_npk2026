/**
 * ============================================================================
 * Phosphorus inference models - CORRECTED BUILD, 15 September 2026
 *
 * Supersedes research_q1_phosphorus/firmware/phosphorus_q1_models.h
 *
 * Changes from the superseded file, with the reason for each:
 *
 *  1. ROOT SELECTION FIXED. The previous quadratic inverse used
 *        (-b - sqrtf(disc)) / (2a)
 *     With a = -0.00727 < 0 the parabola opens downward and its vertex sits at
 *     C* = -b/2a = 8.51 mg/L. That branch is the DESCENDING branch above the
 *     vertex, so every absorbance mapped to a concentration above C*, which the
 *     clamp then pinned to the 10.0 mg/L ceiling. As shipped, the function
 *     returned 10.0 mg/L for every standard from 1.0 to 6.0 mg/L
 *     (RMSE 5.78 mg/L). The correct branch for a < 0 is (-b + sqrtf(disc))/(2a)
 *     (RMSE 1.26 mg/L).
 *
 *  2. WORKING RANGE NARROWED TO 1.0-6.0 mg/L. Local sensitivity dA/dC falls to
 *     0.0076 AU per mg/L over 6-8 mg/L and reverses to -0.0015 over 8-10 mg/L.
 *     The response is not monotonic above 6 mg/L, so no inverse exists there.
 *     Above the ceiling the device must ask for a dilution, not return a number.
 *
 *  3. LINEAR MODEL PROMOTED TO PRIMARY. On 1.0-6.0 mg/L an ordinary linear fit
 *     gives R2 = 0.9944 and RMSE 0.144 mg/L, 8.8x better than the quadratic
 *     over 1-10 mg/L. The non-linear models are retained for comparison only.
 *
 *  4. STATUS CODES ADDED. Every predictor reports whether its answer is inside
 *     the validated range, so calling code can never silently present a clamped
 *     value as a measurement.
 *
 *  Chewa Thassana, Digital Agriculture and Environment Programme,
 *  Faculty of Science and Technology, Rambhai Barni Rajabhat University.
 * ============================================================================
 */

#ifndef PHOSPHORUS_Q1_MODELS_FIXED_H
#define PHOSPHORUS_Q1_MODELS_FIXED_H

#include <math.h>

/* --------------------------------------------------------------------------
 * Validated working range. Derived from the sensitivity analysis, not chosen.
 * -------------------------------------------------------------------------- */
#define P_RANGE_MIN_MGL   (1.0f)
#define P_RANGE_MAX_MGL   (6.0f)

typedef enum {
    P_OK              = 0,  /* result lies inside the validated range          */
    P_BELOW_RANGE     = 1,  /* below 1.0 mg/L: use the 0-1 mg/L calibration    */
    P_ABOVE_RANGE     = 2,  /* above 6.0 mg/L: DILUTE AND RE-MEASURE           */
    P_SATURATED       = 3   /* detector saturated: no concentration recoverable*/
} p_status_t;

typedef struct {
    float      concentration_mg_L;
    p_status_t status;
} p_result_t;

/* Saturation guard. A(6.0 mg/L) = 0.4929 AU and A(8.0 mg/L) = 0.5082 AU; the
 * threshold sits between them, so the 6.0 mg/L standard is still accepted while
 * anything on the plateau is rejected. Above it the response is not monotonic,
 * so no inverse exists and any number returned would be fabricated. */
#define P_ABS_SATURATION (0.5000f)


/* ==========================================================================
 * PRIMARY MODEL - linear, 1.0 to 6.0 mg/L
 *   A = 0.07534 C + 0.04982      R2 = 0.9944, RMSE_conc = 0.144 mg/L, n = 4
 * ========================================================================== */
#define P_LIN_SLOPE      (0.075340f)
#define P_LIN_INTERCEPT  (0.049820f)

static inline p_result_t predict_phosphorus_linear(float a_red)
{
    p_result_t r;

    /* Reject a reading that has run into the saturated plateau before doing
     * any arithmetic. Past this point the response is not monotonic, so an
     * inverse does not exist and a returned number would be fabricated. */
    if (a_red > P_ABS_SATURATION) {
        r.concentration_mg_L = P_RANGE_MAX_MGL;
        r.status = P_ABOVE_RANGE;
        return r;
    }

    r.concentration_mg_L = (a_red - P_LIN_INTERCEPT) / P_LIN_SLOPE;

    if (r.concentration_mg_L < P_RANGE_MIN_MGL) {
        r.status = P_BELOW_RANGE;      /* value is reported, but flagged */
    } else {
        r.status = P_OK;
    }
    return r;
}


/* ==========================================================================
 * LOW-RANGE MODEL - linear, 0.0 to 0.8 mg/L
 *   A = 0.23450 C + 0.00280      R2 = 0.99895, n = 5
 *   LOD = 0.039 mg/L, LOQ = 0.118 mg/L
 *
 * WARNING: this calibration was acquired at a DIFFERENT gain and integration
 * time from the 1-6 mg/L set above. The two must not be joined into one curve.
 * Select the model that matches the acquisition settings actually in use.
 * ========================================================================== */
#define P_LOW_SLOPE      (0.234500f)
#define P_LOW_INTERCEPT  (0.002800f)
#define P_LOD_MGL        (0.039f)
#define P_LOQ_MGL        (0.118f)

static inline p_result_t predict_phosphorus_low_range(float a_red)
{
    p_result_t r;
    r.concentration_mg_L = (a_red - P_LOW_INTERCEPT) / P_LOW_SLOPE;
    r.status = (r.concentration_mg_L > 0.8f) ? P_ABOVE_RANGE : P_OK;
    return r;
}


/* ==========================================================================
 * COMPARISON MODEL A - quadratic polynomial, CORRECTED ROOT
 *   A = -0.0072697 C^2 + 0.1237041 C - 0.0060346
 *   R2_abs = 0.9925 but RMSE_conc = 1.264 mg/L over 1-10 mg/L.
 *   Retained for reproducing the published comparison. NOT for production:
 *   near the vertex dC/dA diverges and small absorbance errors are amplified
 *   into concentration errors of up to 2.93 mg/L.
 * ========================================================================== */
#define P_POLY_A    (-0.0072697f)
#define P_POLY_B    ( 0.1237041f)
#define P_POLY_C    (-0.0060346f)
#define P_POLY_VERTEX_MGL (8.508f)   /* -b / 2a */

static inline p_result_t predict_phosphorus_quadratic(float a_red)
{
    p_result_t r;
    float disc = (P_POLY_B * P_POLY_B) - 4.0f * P_POLY_A * (P_POLY_C - a_red);

    if (disc < 0.0f) {
        /* Absorbance lies above the parabola's maximum: physically impossible
         * input, or the detector has saturated. Do not invent a value. */
        r.concentration_mg_L = P_POLY_VERTEX_MGL;
        r.status = P_SATURATED;
        return r;
    }

    /* a < 0, so the ASCENDING branch below the vertex is the + root.
     * Using the - root here was the defect in the previous release. */
    r.concentration_mg_L = (-P_POLY_B + sqrtf(disc)) / (2.0f * P_POLY_A);

    if (r.concentration_mg_L > P_RANGE_MAX_MGL) {
        r.status = P_ABOVE_RANGE;
    } else if (r.concentration_mg_L < P_RANGE_MIN_MGL) {
        r.status = P_BELOW_RANGE;
    } else {
        r.status = P_OK;
    }
    return r;
}


/* ==========================================================================
 * COMPARISON MODEL B - Langmuir saturation isotherm
 *   A = (0.82581 C) / (5.20853 + C)      =>   C = (Kd A) / (Amax - A)
 *   RMSE_conc = 1.040 mg/L fitted, 1.522 mg/L under leave-one-out CV.
 *
 *   Amax = 0.8258 +/- 0.1270 AU and Kd = 5.209 +/- 1.751 mg/L. Amax exceeds the
 *   largest absorbance actually measured (0.508 AU) by 63 percent, so it is an
 *   extrapolation. Do not read Kd as a reagent-depletion constant.
 * ========================================================================== */
#define P_LANG_AMAX (0.825814f)
#define P_LANG_KD   (5.208531f)

static inline p_result_t predict_phosphorus_langmuir(float a_red)
{
    p_result_t r;
    float denom = P_LANG_AMAX - a_red;

    if (denom < 0.01f) {
        r.concentration_mg_L = P_RANGE_MAX_MGL;
        r.status = P_SATURATED;
        return r;
    }

    r.concentration_mg_L = (P_LANG_KD * a_red) / denom;

    if (r.concentration_mg_L > P_RANGE_MAX_MGL) {
        r.status = P_ABOVE_RANGE;
    } else if (r.concentration_mg_L < P_RANGE_MIN_MGL) {
        r.status = P_BELOW_RANGE;
    } else {
        r.status = P_OK;
    }
    return r;
}


/* ==========================================================================
 * Self-test. Call once at start-up, or run on the host in CI.
 * Feeds the six measured standards through the primary model and checks the
 * returned concentrations against the true values. A test of exactly this
 * shape would have caught the root-selection defect in the previous release,
 * which returned in-range-looking values for every input and so passed every
 * bounds check it was given.
 * Returns 0 on pass, or the 1-based index of the first standard that failed.
 * ========================================================================== */
static inline int phosphorus_selftest(float tolerance_mg_L)
{
    /* Measured absorbance and true concentration, 1-6 mg/L standards. */
    static const float abs_in[4]  = {0.124939f, 0.191886f, 0.368976f, 0.492916f};
    static const float conc_ref[4] = {1.0f, 2.0f, 4.0f, 6.0f};

    for (int i = 0; i < 4; ++i) {
        p_result_t r = predict_phosphorus_linear(abs_in[i]);
        /* P_BELOW_RANGE is tolerated: the 1.0 mg/L standard sits on the lower
         * boundary and may round just under it. ABOVE/SATURATED is a failure. */
        if (r.status == P_ABOVE_RANGE || r.status == P_SATURATED) return i + 1;
        if (fabsf(r.concentration_mg_L - conc_ref[i]) > tolerance_mg_L) return i + 1;
    }
    return 0;   /* pass; tolerance of 0.30 mg/L is met by the fitted model */
}

#endif /* PHOSPHORUS_Q1_MODELS_FIXED_H */
