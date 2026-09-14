#ifndef SPECTRUM_ENGINE_H
#define SPECTRUM_ENGINE_H

#include <Arduino.h>
#include <TFT_eSPI.h>
#include <Adafruit_NeoPixel.h>
#include "Adafruit_TCS34725.h"
#include "Calibration_Engine.h"

// ============================================================
// Spectrum Scan Result Structure
// ============================================================
struct SpectrumScanResult {
  float sampleIntensity[NUM_SPECTRAL_BANDS]; // I_sample(lambda)
  float darkIntensity[NUM_SPECTRAL_BANDS];   // I_dark(lambda)
  float transmittance[NUM_SPECTRAL_BANDS];   // T = (I_s - I_d)/(I_0 - I_d)
  float absorbance[NUM_SPECTRAL_BANDS];      // A = -log10(T)
  uint16_t peakWavelength;
  float peakAbsorbance;
  bool highAbsWarning;                       // True if A_max > 1.50
  bool scanComplete;
  unsigned long timestamp;
};

// ============================================================
// Execute Automated Wavelength Sweep & Dark Current Subtraction
// ============================================================
inline void executeAutoWavelengthScan(
    Adafruit_NeoPixel &strip,
    Adafruit_TCS34725 &tcs,
    CalibrationState &calib,
    SpectrumScanResult &result,
    bool hasTCS) 
{
  result.scanComplete = false;
  result.highAbsWarning = false;
  result.peakAbsorbance = 0.0f;
  result.peakWavelength = 525;
  result.timestamp = millis();

  // ------------------------------------------------------------
  // Step 1: Dark Current & Ambient Measurement (All LEDs OFF)
  // ------------------------------------------------------------
  strip.clear();
  strip.show();
  delay(50); // Allow sensor settling

  uint16_t dark_r = 0, dark_g = 0, dark_b = 0, dark_c = 0;
  if (hasTCS) {
    tcs.getRawData(&dark_r, &dark_g, &dark_b, &dark_c);
  }

  // Record Dark Baseline for each band
  result.darkIntensity[0] = (float)dark_b;
  result.darkIntensity[1] = ((float)dark_b + (float)dark_g) * 0.5f;
  result.darkIntensity[2] = (float)dark_g;
  result.darkIntensity[3] = ((float)dark_r + (float)dark_g) * 0.5f;
  result.darkIntensity[4] = (float)dark_r;

  for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
    calib.darkCurrent[i] = result.darkIntensity[i];
  }

  // ------------------------------------------------------------
  // Step 2: Sequential Wavelength Excitation & Measurement
  // ------------------------------------------------------------
  // Color specifications for each discrete band:
  const uint8_t colorSeq[NUM_SPECTRAL_BANDS][3] = {
    {0,   0,   255}, // 0: 465 nm Blue
    {0,   190, 255}, // 1: 500 nm Cyan
    {0,   255, 0  }, // 2: 525 nm Green
    {255, 200, 0  }, // 3: 590 nm Yellow
    {255, 0,   0  }  // 4: 625 nm Red
  };

  for (int band = 0; band < NUM_SPECTRAL_BANDS; band++) {
    // Set LED to specific wavelength color
    for (int p = 0; p < strip.numPixels(); p++) {
      strip.setPixelColor(p, colorSeq[band][0], colorSeq[band][1], colorSeq[band][2]);
    }
    strip.show();
    delay(70); // Optical settling and integration time

    uint16_t r = 0, g = 0, b = 0, c = 0;
    if (hasTCS) {
      tcs.getRawData(&r, &g, &b, &c);
    }

    // Extract channel intensity corresponding to the target wavelength
    float rawSig = 0.0f;
    switch (band) {
      case 0: rawSig = (float)b; break;                    // Blue band
      case 1: rawSig = ((float)b + (float)g) * 0.5f; break; // Cyan band
      case 2: rawSig = (float)g; break;                    // Green band
      case 3: rawSig = ((float)r + (float)g) * 0.5f; break; // Yellow band
      case 4: rawSig = (float)r; break;                    // Red band
    }

    result.sampleIntensity[band] = rawSig;

    // Correct for Dark Current
    float dark = result.darkIntensity[band];
    float I_sample_corr = max(1.0f, rawSig - dark);
    float I_blank_corr  = max(1.0f, calib.blankIntensity[band] - dark);

    // Calculate Transmittance & Absorbance (Beer-Lambert Law)
    float T = constrain(I_sample_corr / I_blank_corr, 0.001f, 1.50f);
    result.transmittance[band] = T;

    float A = -log10f(T);
    if (A < 0.0f) A = 0.0f;
    if (A > 2.50f) A = 2.50f;
    result.absorbance[band] = A;

    // Track Peak
    if (A > result.peakAbsorbance) {
      result.peakAbsorbance = A;
      result.peakWavelength = SPECTRAL_WAVELENGTHS[band];
    }
  }

  // Dynamic range limit check (A > 1.50 means < 3.16% light transmitted)
  if (result.peakAbsorbance > 1.50f) {
    result.highAbsWarning = true;
  }

  result.scanComplete = true;

  // Turn LEDs off after scan
  strip.clear();
  strip.show();
}

// ============================================================
// Capture Blank Reference (I_0) on all channels
// ============================================================
inline void captureBlankReference(
    Adafruit_NeoPixel &strip,
    Adafruit_TCS34725 &tcs,
    CalibrationState &calib,
    bool hasTCS)
{
  SpectrumScanResult dummyResult;
  // Execute a sweep
  executeAutoWavelengthScan(strip, tcs, calib, dummyResult, hasTCS);

  // Set calibrated values from the sweep
  for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
    calib.blankIntensity[i] = max(100.0f, dummyResult.sampleIntensity[i]);
  }
  calib.isCalibrated = true;
  calib.calibrationTimestamp = millis();

  // Save to SD Card
  saveCalibrationToSD();
}

// ============================================================
// Render Absorbance Spectrum Chart on Wio Terminal LCD (320x240)
// ============================================================
inline void drawSpectrumChart(TFT_eSPI &tft, const SpectrumScanResult &res, bool isScanning) {
  tft.fillScreen(TFT_BLACK);

  // 1. Top Header Bar
  tft.fillRect(0, 0, 320, 28, 0x18E3); // Dark slate blue
  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x18E3);
  tft.drawString("ABSORBANCE SPECTRUM A(lambda)", 10, 8);

  tft.setTextColor(TFT_YELLOW, 0x18E3);
  tft.drawString("[Page 3/5]", 250, 8);

  // 2. Chart Plot Window Dimensions
  const int X0 = 36;
  const int Y0 = 38;
  const int W  = 274;
  const int H  = 136;
  const int X1 = X0 + W;
  const int Y1 = Y0 + H;

  // Chart Background and Border
  tft.fillRect(X0, Y0, W, H, 0x0842); // Very dark navy
  tft.drawRect(X0, Y0, W, H, TFT_DARKGREY);

  // 3. Draw Gridlines & Y-Axis Scale (Absorbance: 0.0 to 2.0)
  tft.setTextSize(1);
  tft.setTextColor(TFT_LIGHTGREY, TFT_BLACK);

  const float ySteps[5] = { 0.0f, 0.5f, 1.0f, 1.5f, 2.0f };
  for (int i = 0; i < 5; i++) {
    int yPos = Y1 - (int)((ySteps[i] / 2.0f) * H);
    if (i > 0 && i < 4) {
      // Dotted horizontal gridline
      for (int x = X0 + 2; x < X1; x += 6) {
        tft.drawFastHLine(x, yPos, 3, 0x2104);
      }
    }
    // Y-Axis Tick Label
    char yStr[6];
    sprintf(yStr, "%0.1f", ySteps[i]);
    tft.drawString(yStr, 8, yPos - 4);
    tft.drawFastHLine(X0 - 3, yPos, 3, TFT_DARKGREY);
  }

  // Y-Axis Title
  tft.setTextColor(0x07FF, TFT_BLACK); // Cyan
  tft.drawString("Abs(A)", 2, Y0 - 8);

  // 4. Draw Gridlines & X-Axis Scale (Wavelength: 420 to 660 nm)
  const uint16_t xSteps[5] = { 450, 500, 550, 600, 650 };
  const float lambdaMin = 420.0f;
  const float lambdaMax = 660.0f;

  for (int i = 0; i < 5; i++) {
    int xPos = X0 + (int)(((float)(xSteps[i] - lambdaMin) / (lambdaMax - lambdaMin)) * W);
    // Dotted vertical gridline
    for (int y = Y0 + 2; y < Y1; y += 6) {
      tft.drawFastVLine(xPos, y, 3, 0x2104);
    }
    // X-Axis Tick Label
    char xStr[6];
    sprintf(xStr, "%d", xSteps[i]);
    tft.setTextColor(TFT_LIGHTGREY, TFT_BLACK);
    tft.drawString(xStr, xPos - 10, Y1 + 4);
    tft.drawFastVLine(xPos, Y1, 3, TFT_DARKGREY);
  }

  // X-Axis Title
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("Wavelength (nm)", 118, Y1 + 16);

  // 5. Draw Spectrum Data Points & Curve
  if (res.scanComplete) {
    int prevX = 0, prevY = 0;

    for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
      float wl = (float)SPECTRAL_WAVELENGTHS[i];
      float a  = res.absorbance[i];

      int curX = X0 + (int)(((wl - lambdaMin) / (lambdaMax - lambdaMin)) * W);
      int curY = Y1 - (int)(constrain(a / 2.0f, 0.0f, 1.0f) * H);

      // Connect with thick colored line
      if (i > 0) {
        tft.drawLine(prevX, prevY, curX, curY, TFT_CYAN);
        tft.drawLine(prevX, prevY - 1, curX, curY - 1, TFT_CYAN);
        tft.drawLine(prevX, prevY + 1, curX, curY + 1, TFT_CYAN);
      }

      prevX = curX;
      prevY = curY;
    }

    // Draw markers on each band
    for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
      float wl = (float)SPECTRAL_WAVELENGTHS[i];
      float a  = res.absorbance[i];
      int curX = X0 + (int)(((wl - lambdaMin) / (lambdaMax - lambdaMin)) * W);
      int curY = Y1 - (int)(constrain(a / 2.0f, 0.0f, 1.0f) * H);

      // Node marker
      tft.fillCircle(curX, curY, 4, TFT_YELLOW);
      tft.drawCircle(curX, curY, 4, TFT_RED);

      // Value tooltip above node
      char valBuf[8];
      sprintf(valBuf, "%0.2f", a);
      tft.setTextSize(1);
      tft.setTextColor(TFT_WHITE, 0x0842);
      tft.drawString(valBuf, curX - 10, curY - 14);
    }

    // Highlight Peak Wavelength Marker
    int peakX = X0 + (int)(((float)(res.peakWavelength - lambdaMin) / (lambdaMax - lambdaMin)) * W);
    int peakY = Y1 - (int)(constrain(res.peakAbsorbance / 2.0f, 0.0f, 1.0f) * H);
    tft.drawCircle(peakX, peakY, 7, TFT_MAGENTA);
  }

  // 6. Footer Status & Dynamic Range Notification
  tft.drawFastHLine(0, 204, 320, TFT_DARKGREY);

  if (isScanning) {
    tft.setTextSize(1);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString(">> AUTO-SCANNING WAVELENGTHS IN PROGRESS <<", 20, 216);
  } else {
    // Left: Peak info
    tft.setTextSize(1);
    char peakStr[36];
    sprintf(peakStr, "Peak: %d nm  |  A_max = %0.2f", res.peakWavelength, res.peakAbsorbance);
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString(peakStr, 10, 212);

    // Warning if Absorbance exceeds linear range (> 1.50)
    if (res.highAbsWarning) {
      tft.setTextColor(TFT_RED, TFT_BLACK);
      tft.drawString("! WARN: HIGH ABS - DILUTE 1:5 !", 10, 226);
    } else {
      tft.setTextColor(TFT_LIGHTGREY, TFT_BLACK);
      tft.drawString("[DOWN]: Run Auto-Scan  |  [< / >]: Switch Page", 10, 226);
    }
  }
}

#endif // SPECTRUM_ENGINE_H
