#ifndef CALIBRATION_ENGINE_H
#define CALIBRATION_ENGINE_H

#include <Arduino.h>
#include <Seeed_FS.h>
#include "SD/Seeed_SD.h"

// ============================================================
// Wavelength Channels Definition (5 Discrete Bands)
// ============================================================
#define NUM_SPECTRAL_BANDS 5

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
// Calibration State Structure
// ============================================================
struct CalibrationState {
  float blankIntensity[NUM_SPECTRAL_BANDS]; // I_0(lambda)
  float darkCurrent[NUM_SPECTRAL_BANDS];    // I_dark(lambda)
  bool isCalibrated;
  uint32_t calibrationTimestamp;
};

extern CalibrationState calibState;

// Initialize default baseline reference
inline void initCalibration() {
  // Default reference intensity (based on clean deionized water in 10mm cuvette)
  calibState.blankIntensity[0] = 3850.0f; // 465 nm
  calibState.blankIntensity[1] = 4200.0f; // 500 nm
  calibState.blankIntensity[2] = 4950.0f; // 525 nm
  calibState.blankIntensity[3] = 4600.0f; // 590 nm
  calibState.blankIntensity[4] = 4300.0f; // 625 nm

  for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
    calibState.darkCurrent[i] = 12.0f; // default ambient dark count
  }
  calibState.isCalibrated = true;
  calibState.calibrationTimestamp = 0;
}

// Save Blank Reference to SD Card
inline bool saveCalibrationToSD() {
  File f = SD.open("BLANK.DAT", FILE_WRITE);
  if (!f) return false;
  f.write((const uint8_t*)&calibState, sizeof(CalibrationState));
  f.close();
  return true;
}

// Load Blank Reference from SD Card
inline bool loadCalibrationFromSD() {
  if (!SD.exists("BLANK.DAT")) return false;
  File f = SD.open("BLANK.DAT", FILE_READ);
  if (!f) return false;
  if (f.size() == sizeof(CalibrationState)) {
    f.read((uint8_t*)&calibState, sizeof(CalibrationState));
    f.close();
    return true;
  }
  f.close();
  return false;
}

#endif // CALIBRATION_ENGINE_H
