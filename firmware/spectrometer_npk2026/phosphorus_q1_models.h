/**
 * ============================================================================
 * Q1 RESEARCH ARTIFACT: Phosphorus 1.0 - 10.0 mg/L Advanced Inference Models
 * Comparative Implementation of 3 Advanced Mathematical Options
 * Digital Agriphysics & AI Research Lab | RBRU
 * ============================================================================
 */

#ifndef PHOSPHORUS_Q1_MODELS_H
#define PHOSPHORUS_Q1_MODELS_H

#include <math.h>

// ----------------------------------------------------------------------------
// OPTION 1: Quadratic Polynomial Inversion (R2 = 0.9925)
// Fast, robust, closed-form algebraic root solution.
// ----------------------------------------------------------------------------
#define P_POLY_A    (-0.007270f)
#define P_POLY_B    (0.123704f)
#define P_POLY_C    (-0.006035f)

static inline float predict_phosphorus_option1_quadratic(float a_red) {
    // C = (-b - sqrt(b^2 - 4*a*(c - A))) / (2*a)
    float disc = (P_POLY_B * P_POLY_B) - 4.0f * P_POLY_A * (P_POLY_C - a_red);
    if (disc < 0.0f) disc = 0.0f;
    float c = (-P_POLY_B - sqrtf(disc)) / (2.0f * P_POLY_A);
    if (c < 1.0f) c = 1.0f;
    if (c > 10.0f) c = 10.0f;
    return c;
}

// ----------------------------------------------------------------------------
// OPTION 2: Langmuir Chemical Kinetics Isotherm Inversion (R2 = 0.9609)
// Grounded in physical mass action law of Molybdenum Blue complexation.
// ----------------------------------------------------------------------------
#define P_LANG_AMAX (0.825808f)
#define P_LANG_KD   (5.208457f)

static inline float predict_phosphorus_option2_langmuir(float a_red) {
    // C = (Kd * A) / (Amax - A)
    float denom = P_LANG_AMAX - a_red;
    if (denom < 0.01f) denom = 0.01f; // Prevent division by zero near saturation
    float c = (P_LANG_KD * a_red) / denom;
    if (c < 1.0f) c = 1.0f;
    if (c > 10.0f) c = 10.0f;
    return c;
}

// ----------------------------------------------------------------------------
// OPTION 3: Dual-Channel White Optical Assay (R2 = 0.8307)
// Uses broad-spectrum White/Clear channel to maintain linearity and resist turbidity.
// ----------------------------------------------------------------------------
#define P_WHITE_SLOPE     (0.039841f)
#define P_WHITE_INTERCEPT (0.076379f)

static inline float predict_phosphorus_option3_white_channel(float a_white) {
    // C = (A_white - intercept) / slope
    float c = (a_white - P_WHITE_INTERCEPT) / P_WHITE_SLOPE;
    if (c < 1.0f) c = 1.0f;
    if (c > 10.0f) c = 10.0f;
    return c;
}

#endif // PHOSPHORUS_Q1_MODELS_H
