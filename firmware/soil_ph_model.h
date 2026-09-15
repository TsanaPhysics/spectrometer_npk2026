/**
 * ============================================================================
 * SOIL pH OPTICAL RATIOMETRIC PRE-MODEL ENGINE
 * Analytical Spectrophotometry for Soil pH Indicator Assays
 * Based on Henderson-Hasselbalch Ratiometric Absorbance (Green/Red Band Ratio)
 * Project: Digital Agriphysics & AI Soil Nutrient Sensing (RBRU)
 * Author: Asst. Prof. Dr. Chewa Thassana & AgriPhysics Research Team
 * ============================================================================
 */

#ifndef SOIL_PH_MODEL_H
#define SOIL_PH_MODEL_H

#include <math.h>

// ----------------------------------------------------------------------------
// Theoretical Optical Constants for Universal / Mixed pH Indicators
// (Bromothymol Blue + Methyl Red + Phenolphthalein Dye Matrices)
// ----------------------------------------------------------------------------
// In-situ dye equilibrium: HIn (Acid form, absorbs Red/Yellow) <-> In- (Base form, absorbs Green/Cyan)
// pH = pKa + log10([In-] / [HIn]) = pKa + slope * log10((A_green + offset) / (A_red + offset))

#define SOIL_PH_THEORETICAL_PKA       (6.80f)   // Mean pKa of bromothymol blue conjugate system
#define SOIL_PH_THEORETICAL_SLOPE     (2.65f)   // Ratiometric sensitivity factor
#define SOIL_PH_ABSORBANCE_OFFSET     (0.015f)  // Zero-division avoidance & baseline stray light offset
#define SOIL_PH_MIN_MEASURABLE        (3.50f)   // Extreme Acid boundary
#define SOIL_PH_MAX_MEASURABLE        (8.50f)   // Alkaline boundary

// Pre-configured 3-Point In-Situ Calibration Placeholders (Ready for Future Empirical Buffer Data)
// Standard Buffers: pH 4.01 (Acid), pH 7.00 (Neutral), pH 10.01 (Alkaline)
struct SoilPhCalibrationTable {
    float buffer_ph[3];      // 4.01, 7.00, 10.01
    float measured_ratio[3];  // Ratio (A_green / A_red)
    bool is_calibrated;
};

// ----------------------------------------------------------------------------
// Soil Health & Durian Agronomy Interpretation Classifications
// ----------------------------------------------------------------------------
enum SoilPhClass {
    PH_STRONGLY_ACIDIC  = 0, // pH < 4.5  (เสี่ยงเป็นพิษจาก Al/Fe ดินกรดรุนแรง)
    PH_MODERATELY_ACIDIC = 1, // 4.5 <= pH < 5.5 (กรดปานกลาง พืชเริ่มดูดซึม P ได้ลดลง)
    PH_OPTIMAL_DURIAN    = 2, // 5.5 <= pH <= 6.5 (ช่วงที่เหมาะสมที่สุดสำหรับทุเรียนและพืชเขตร้อน)
    PH_SLIGHTLY_ALKALINE = 3, // 6.5 < pH <= 7.5 (เป็นกลางถึงด่างอ่อน)
    PH_STRONGLY_ALKALINE = 4  // pH > 7.5 (ดินด่าง ธาตุอาหารจุลธาตุ Zn/Fe ขาดแคลน)
};

/**
 * Predicts Soil pH using Optical Ratiometric Absorbance
 * @param a_red   Absorbance measured at 625 nm (Acid form protonated absorbance)
 * @param a_green Absorbance measured at 525 nm (Base form deprotonated absorbance)
 * @param a_blue  Absorbance measured at 465 nm (Secondary reference for baseline drift)
 * @return Estimated Soil pH (constrained between 3.50 and 8.50)
 */
static inline float predict_soil_ph_optical(float a_red, float a_green, float a_blue) {
    // 1. Compensate baseline scattering if blue has non-specific turbidity
    float a_g_eff = (a_green > 0.001f) ? a_green : 0.001f;
    float a_r_eff = (a_red > 0.001f) ? a_red : 0.001f;

    // 2. Optical Ratiometric calculation
    float ratio = (a_g_eff + SOIL_PH_ABSORBANCE_OFFSET) / (a_r_eff + SOIL_PH_ABSORBANCE_OFFSET);
    if (ratio < 0.01f) ratio = 0.01f;
    if (ratio > 100.0f) ratio = 100.0f;

    // 3. Sigmoidal / Logarithmic Henderson-Hasselbalch response
    float estimated_ph = SOIL_PH_THEORETICAL_PKA + (SOIL_PH_THEORETICAL_SLOPE * log10f(ratio));

    // 4. Bound check within reasonable soil agronomic boundary
    if (estimated_ph < SOIL_PH_MIN_MEASURABLE) estimated_ph = SOIL_PH_MIN_MEASURABLE;
    if (estimated_ph > SOIL_PH_MAX_MEASURABLE) estimated_ph = SOIL_PH_MAX_MEASURABLE;

    return estimated_ph;
}

/**
 * Classifies Soil pH into Agronomic Action Categories
 */
static inline SoilPhClass classify_soil_ph(float ph_val) {
    if (ph_val < 4.50f) return PH_STRONGLY_ACIDIC;
    if (ph_val < 5.50f) return PH_MODERATELY_ACIDIC;
    if (ph_val <= 6.50f) return PH_OPTIMAL_DURIAN;
    if (ph_val <= 7.50f) return PH_SLIGHTLY_ALKALINE;
    return PH_STRONGLY_ALKALINE;
}

/**
 * Returns Short Text Recommendation for Display
 */
static inline const char* get_soil_ph_desc(SoilPhClass ph_class) {
    switch (ph_class) {
        case PH_STRONGLY_ACIDIC:   return "Very Acidic (Add Lime)";
        case PH_MODERATELY_ACIDIC: return "Moderate Acid (Adjust)";
        case PH_OPTIMAL_DURIAN:    return "OPTIMAL (Durian Best)";
        case PH_SLIGHTLY_ALKALINE: return "Neutral / Mild Base";
        case PH_STRONGLY_ALKALINE: return "Alkaline (Needs Gypsum)";
        default:                   return "Standard Range";
    }
}

#endif // SOIL_PH_MODEL_H
