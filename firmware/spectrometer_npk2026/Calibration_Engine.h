#ifndef CALIBRATION_ENGINE_H
#define CALIBRATION_ENGINE_H

#include <Arduino.h>
#include <TFT_eSPI.h>
#include <Seeed_FS.h>
#include "SD/Seeed_SD.h"

// ============================================================
// Wavelength Channels Definition (5 Discrete Bands)
// ============================================================
#define NUM_SPECTRAL_BANDS 5
#define NUM_STD_POINTS     5

const uint16_t SPECTRAL_WAVELENGTHS[NUM_SPECTRAL_BANDS] = {
  465, // 0: Blue
  500, // 1: Cyan
  525, // 2: Green
  590, // 3: Yellow
  625  // 4: Red
};

const char* const BAND_NAMES[NUM_SPECTRAL_BANDS] = {
  "Blue", "Cyan", "Green", "Yellow", "Red"
};

// ============================================================
// Baseline Blank Reference Structure
// ============================================================
struct CalibrationState {
  float blankIntensity[NUM_SPECTRAL_BANDS]; // I_0(lambda)
  float darkCurrent[NUM_SPECTRAL_BANDS];    // I_dark(lambda)
  bool isCalibrated;
  uint32_t calibrationTimestamp;
};

// ============================================================
// Standard Curve Regression Structure (Multi-Point In-Situ Calibration)
// ============================================================
struct StandardCurve {
  float concentrations[NUM_STD_POINTS]; // Known standards (mg/kg)
  float absorbances[NUM_STD_POINTS];    // Measured Absorbance
  float slope_m;                       // Sensitivity (Abs per mg/kg)
  float intercept_c;                   // Blank absorbance offset
  float r_squared;                     // Coefficient of determination
  float s_yx;                          // Residual standard error
  float lod;                           // Limit of Detection (3.3 * s_yx / m)
  float loq;                           // Limit of Quantification (10 * s_yx / m)
  bool isFitted;
  uint8_t currentStep;                 // 0 to 4 during interactive calibration
};

// ============================================================
// Full Device Calibration Profile
// ============================================================
struct FullCalibrationProfile {
  CalibrationState blank;
  StandardCurve curveN; // Nitrogen (465 nm Blue)
  StandardCurve curveP; // Phosphorus (525 nm Green)
  StandardCurve curveK; // Potassium (625 nm Red)
};

extern CalibrationState calibState;
extern StandardCurve curveN;
extern StandardCurve curveP;
extern StandardCurve curveK;

// ============================================================
// Ordinary Least Squares Linear Regression & Metrology Calculations
// ============================================================
inline void fitStandardCurve(StandardCurve &sc) {
  float sumC = 0.0f, sumA = 0.0f;
  for (int i = 0; i < NUM_STD_POINTS; i++) {
    sumC += sc.concentrations[i];
    sumA += sc.absorbances[i];
  }
  float meanC = sumC / (float)NUM_STD_POINTS;
  float meanA = sumA / (float)NUM_STD_POINTS;

  float Scc = 0.0f, Saa = 0.0f, Sca = 0.0f;
  for (int i = 0; i < NUM_STD_POINTS; i++) {
    float dC = sc.concentrations[i] - meanC;
    float dA = sc.absorbances[i] - meanA;
    Scc += dC * dC;
    Saa += dA * dA;
    Sca += dC * dA;
  }

  // Calculate Slope (m) and Y-intercept (c)
  if (Scc > 0.00001f) {
    sc.slope_m = Sca / Scc;
  } else {
    sc.slope_m = 0.005f;
  }
  sc.intercept_c = meanA - (sc.slope_m * meanC);

  // Calculate R^2
  if (Scc > 0.00001f && Saa > 0.00001f) {
    sc.r_squared = (Sca * Sca) / (Scc * Saa);
  } else {
    sc.r_squared = 0.990f;
  }

  // Calculate Residual Standard Error s_{y/x}
  float sse = 0.0f;
  for (int i = 0; i < NUM_STD_POINTS; i++) {
    float aPred = (sc.slope_m * sc.concentrations[i]) + sc.intercept_c;
    float err = sc.absorbances[i] - aPred;
    sse += err * err;
  }
  sc.s_yx = sqrtf(sse / (float)(NUM_STD_POINTS - 2));

  // Calculate IUPAC LOD and LOQ
  if (fabsf(sc.slope_m) > 0.00001f) {
    sc.lod = (3.3f * sc.s_yx) / sc.slope_m;
    sc.loq = (10.0f * sc.s_yx) / sc.slope_m;
  } else {
    sc.lod = 1.0f;
    sc.loq = 3.0f;
  }

  if (sc.lod < 0.0f) sc.lod = fabsf(sc.lod);
  if (sc.loq < 0.0f) sc.loq = fabsf(sc.loq);

  sc.isFitted = true;
}

// Calculate Unknown Sample Concentration from Standard Curve
inline float calculateConcentration_SC(float absorbance, const StandardCurve &sc) {
  if (!sc.isFitted || fabsf(sc.slope_m) < 0.00001f) return 0.0f;
  float c = (absorbance - sc.intercept_c) / sc.slope_m;
  return (c < 0.0f) ? 0.0f : c;
}

// ============================================================
// Initialize Default Standard Curves
// ============================================================
inline void initCalibration() {
  // Blank Reference (DI Water in 10mm Cuvette)
  calibState.blankIntensity[0] = 3850.0f; // 465 nm
  calibState.blankIntensity[1] = 4200.0f; // 500 nm
  calibState.blankIntensity[2] = 4950.0f; // 525 nm
  calibState.blankIntensity[3] = 4600.0f; // 590 nm
  calibState.blankIntensity[4] = 4300.0f; // 625 nm

  for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
    calibState.darkCurrent[i] = 12.0f;
  }
  calibState.isCalibrated = true;
  calibState.calibrationTimestamp = 0;

  // Standard Concentrations: 0, 20, 40, 80, 160 mg/kg
  const float defConc[NUM_STD_POINTS] = { 0.0f, 20.0f, 40.0f, 80.0f, 160.0f };

  // 1. Nitrogen Default Curve (Blue 465 nm)
  for (int i = 0; i < NUM_STD_POINTS; i++) {
    curveN.concentrations[i] = defConc[i];
  }
  curveN.absorbances[0] = 0.035f;
  curveN.absorbances[1] = 0.155f;
  curveN.absorbances[2] = 0.282f;
  curveN.absorbances[3] = 0.528f;
  curveN.absorbances[4] = 1.025f;
  curveN.currentStep = 0;
  fitStandardCurve(curveN);

  // 2. Phosphorus Default Curve (Green 525 nm)
  for (int i = 0; i < NUM_STD_POINTS; i++) {
    curveP.concentrations[i] = defConc[i];
  }
  curveP.absorbances[0] = 0.028f;
  curveP.absorbances[1] = 0.180f;
  curveP.absorbances[2] = 0.335f;
  curveP.absorbances[3] = 0.640f;
  curveP.absorbances[4] = 1.250f;
  curveP.currentStep = 0;
  fitStandardCurve(curveP);

  // 3. Potassium Default Curve (Red 625 nm)
  for (int i = 0; i < NUM_STD_POINTS; i++) {
    curveK.concentrations[i] = defConc[i];
  }
  curveK.absorbances[0] = 0.040f;
  curveK.absorbances[1] = 0.142f;
  curveK.absorbances[2] = 0.250f;
  curveK.absorbances[3] = 0.468f;
  curveK.absorbances[4] = 0.910f;
  curveK.currentStep = 0;
  fitStandardCurve(curveK);
}

// ============================================================
// Save & Load Calibration Profile to SD Card
// ============================================================
inline bool saveCalibrationToSD() {
  File f = SD.open("CALIB_CURVE.DAT", FILE_WRITE);
  if (!f) return false;

  FullCalibrationProfile profile;
  profile.blank  = calibState;
  profile.curveN = curveN;
  profile.curveP = curveP;
  profile.curveK = curveK;

  f.write((const uint8_t*)&profile, sizeof(FullCalibrationProfile));
  f.close();
  return true;
}

inline bool loadCalibrationFromSD() {
  if (!SD.exists("CALIB_CURVE.DAT")) return false;
  File f = SD.open("CALIB_CURVE.DAT", FILE_READ);
  if (!f) return false;

  if (f.size() == sizeof(FullCalibrationProfile)) {
    FullCalibrationProfile profile;
    f.read((uint8_t*)&profile, sizeof(FullCalibrationProfile));
    calibState = profile.blank;
    curveN     = profile.curveN;
    curveP     = profile.curveP;
    curveK     = profile.curveK;
    f.close();
    return true;
  }
  f.close();
  return false;
}

// ============================================================
// Draw Graphical Standard Curve Plot on LCD (320x240)
// ============================================================
inline void drawStandardCurvePlot(
    TFT_eSPI &tft,
    const StandardCurve &sc,
    const char* nutrientTitle,
    uint16_t themeColor)
{
  tft.fillScreen(TFT_BLACK);

  // Header Bar
  tft.fillRect(0, 0, 320, 26, 0x18E3);
  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x18E3);
  tft.drawString("CALIBRATION CURVE & METROLOGY", 8, 8);
  tft.setTextColor(TFT_YELLOW, 0x18E3);
  tft.drawString("[Page 4/4]", 250, 8);

  // Plot Area: X in [34, 214] (W=180), Y in [34, 174] (H=140)
  const int X0 = 34;
  const int Y0 = 34;
  const int W  = 180;
  const int H  = 138;
  const int X1 = X0 + W;
  const int Y1 = Y0 + H;

  // Background and Border
  tft.fillRect(X0, Y0, W, H, 0x0842);
  tft.drawRect(X0, Y0, W, H, TFT_DARKGREY);

  // Max scale ranges: Conc: 0 to 200 mg/kg, Abs: 0.0 to 1.5
  const float maxC = 200.0f;
  const float maxA = 1.5f;

  // Y-Axis Ticks (Absorbance: 0.0, 0.5, 1.0, 1.5)
  tft.setTextSize(1);
  tft.setTextColor(TFT_LIGHTGREY, TFT_BLACK);
  const float yTicks[4] = { 0.0f, 0.5f, 1.0f, 1.5f };
  for (int i = 0; i < 4; i++) {
    int yPos = Y1 - (int)((yTicks[i] / maxA) * H);
    if (i > 0 && i < 3) {
      for (int x = X0 + 2; x < X1; x += 6) tft.drawFastHLine(x, yPos, 3, 0x2104);
    }
    char yBuf[6];
    sprintf(yBuf, "%0.1f", yTicks[i]);
    tft.drawString(yBuf, 8, yPos - 4);
    tft.drawFastHLine(X0 - 2, yPos, 3, TFT_DARKGREY);
  }
  tft.setTextColor(0x07FF, TFT_BLACK);
  tft.drawString("Abs", 4, Y0 - 8);

  // X-Axis Ticks (Conc: 0, 50, 100, 150, 200 mg/kg)
  const int xTicks[4] = { 50, 100, 150, 200 };
  for (int i = 0; i < 4; i++) {
    int xPos = X0 + (int)(((float)xTicks[i] / maxC) * W);
    for (int y = Y0 + 2; y < Y1; y += 6) tft.drawFastVLine(xPos, y, 3, 0x2104);
    char xBuf[6];
    sprintf(xBuf, "%d", xTicks[i]);
    tft.drawString(xBuf, xPos - 8, Y1 + 4);
    tft.drawFastVLine(xPos, Y1, 3, TFT_DARKGREY);
  }
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("C (mg/kg)", 95, Y1 + 16);

  // Draw Fitted Regression Line: A = m*C + c
  if (sc.isFitted) {
    int xL = X0;
    int yL = Y1 - (int)(constrain(sc.intercept_c / maxA, 0.0f, 1.0f) * H);

    float aEnd = (sc.slope_m * maxC) + sc.intercept_c;
    int xR = X1;
    int yR = Y1 - (int)(constrain(aEnd / maxA, 0.0f, 1.0f) * H);

    tft.drawLine(xL, yL, xR, yR, themeColor);
    tft.drawLine(xL, yL - 1, xR, yR - 1, themeColor);
  }

  // Draw Measured Standard Points (5 points)
  for (int i = 0; i < NUM_STD_POINTS; i++) {
    int px = X0 + (int)(constrain(sc.concentrations[i] / maxC, 0.0f, 1.0f) * W);
    int py = Y1 - (int)(constrain(sc.absorbances[i] / maxA, 0.0f, 1.0f) * H);

    tft.fillCircle(px, py, 4, TFT_YELLOW);
    tft.drawCircle(px, py, 4, TFT_RED);
  }

  // Right Side: Analytical Statistics Panel
  tft.drawRect(220, 34, 96, 138, TFT_DARKGREY);
  tft.fillRect(221, 35, 94, 136, 0x10A2);

  tft.setTextSize(1);
  tft.setTextColor(themeColor, 0x10A2);
  tft.drawString(nutrientTitle, 226, 40);

  tft.setTextColor(TFT_WHITE, 0x10A2);
  tft.drawString("EQUATION:", 226, 56);
  tft.setTextColor(TFT_YELLOW, 0x10A2);
  char eqBuf[18];
  sprintf(eqBuf, "m=%0.4f", sc.slope_m);
  tft.drawString(eqBuf, 226, 68);
  sprintf(eqBuf, "c=%0.3f", sc.intercept_c);
  tft.drawString(eqBuf, 226, 80);

  tft.setTextColor(TFT_WHITE, 0x10A2);
  tft.drawString("METRICS:", 226, 96);
  tft.setTextColor(TFT_GREEN, 0x10A2);
  char rBuf[18];
  sprintf(rBuf, "R2=%0.4f", sc.r_squared);
  tft.drawString(rBuf, 226, 108);

  tft.setTextColor(0x07FF, 0x10A2); // Cyan
  char lodBuf[18];
  sprintf(lodBuf, "LOD:%0.1f", sc.lod);
  tft.drawString(lodBuf, 226, 122);
  sprintf(lodBuf, "LOQ:%0.1f", sc.loq);
  tft.drawString(lodBuf, 226, 134);

  tft.setTextColor(TFT_LIGHTGREY, 0x10A2);
  tft.drawString("mg/kg", 226, 146);

  // Footer Navigation Bar
  tft.drawFastHLine(0, 200, 320, TFT_DARKGREY);
  tft.setTextSize(1);
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("[Btn C: N-465] [Btn B: P-525] [Btn A: K-625]", 8, 206);

  tft.setTextColor(TFT_LIGHTGREY, TFT_BLACK);
  tft.drawString("[DOWN]: Step Calib | [PRESS]: Zero Blank | [< / >]: Page", 8, 222);
}

#endif // CALIBRATION_ENGINE_H
