#ifndef LIQUID_ENGINE_H
#define LIQUID_ENGINE_H

#include <Arduino.h>
#include <TFT_eSPI.h>
#include <Adafruit_NeoPixel.h>
#include "Adafruit_TCS34725.h"
#include "Calibration_Engine.h"
#include "Spectrum_Engine.h"

// ============================================================
// Liquid Metrology Scan Result Structure
// ============================================================
struct LiquidScanResult {
  float refractiveIndex_n;  // Refractive Index (e.g. 1.3330 - 1.4700)
  float density_g_cm3;      // Density in g/cm3 (e.g. 0.9982 - 1.2500)
  float brix_deg;           // Solute/Sugar concentration in degBrix
  float transmittance_pct;  // Mean optical transmittance (0 - 100%)
  float absorbance[NUM_SPECTRAL_BANDS];
  uint16_t peakWavelength;
  float peakAbsorbance;
  char clarity[20];         // "CLEAR", "SLIGHT TURBID", "TURBID"
  bool scanComplete;
  unsigned long timestamp;
};

// ============================================================
// Analyze Liquid Optics & Metrology (n, rho, Brix, %T)
// ============================================================
inline void analyzeLiquidOptics(
    Adafruit_NeoPixel &strip,
    Adafruit_TCS34725 &tcs,
    CalibrationState &calib,
    LiquidScanResult &result,
    bool hasTCS)
{
  SpectrumScanResult sweepRes;
  executeAutoWavelengthScan(strip, tcs, calib, sweepRes, hasTCS);

  result.scanComplete = true;
  result.timestamp = millis();
  result.peakWavelength = sweepRes.peakWavelength;
  result.peakAbsorbance = sweepRes.peakAbsorbance;

  float sumAbs = 0.0f;
  float sumTrans = 0.0f;

  for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
    result.absorbance[i] = sweepRes.absorbance[i];
    sumAbs += sweepRes.absorbance[i];
    sumTrans += sweepRes.transmittance[i];
  }

  float meanAbs = sumAbs / (float)NUM_SPECTRAL_BANDS;
  float meanT   = (sumTrans / (float)NUM_SPECTRAL_BANDS) * 100.0f;
  result.transmittance_pct = constrain(meanT, 0.0f, 100.0f);

  // 1. Calculate Brix (Solute Concentration from Optical Attenuation)
  float brix = meanAbs * 26.5f;
  result.brix_deg = constrain(brix, 0.0f, 65.0f);

  // 2. Calculate Refractive Index (n) based on ICUMSA Standard Relation
  // Pure water: n = 1.3330. Sugar/solutes increase n by ~0.00143 per degBrix
  float n = 1.3330f + (0.00143f * result.brix_deg) + (0.0000045f * result.brix_deg * result.brix_deg);
  result.refractiveIndex_n = constrain(n, 1.3330f, 1.5200f);

  // 3. Calculate Density (rho in g/cm3) via Gladstone-Dale & Lorentz-Lorenz
  // Pure water at 20C: rho = 0.9982 g/cm3. Increases by ~0.00385 g/cm3 per degBrix
  float rho = 0.9982f + (0.00385f * result.brix_deg) + (0.000012f * result.brix_deg * result.brix_deg);
  result.density_g_cm3 = constrain(rho, 0.9982f, 1.3500f);

  // 4. Determine Clarity / Turbidity Status
  if (meanAbs < 0.12f) {
    strcpy(result.clarity, "CLEAR (ใส)");
  } else if (meanAbs < 0.38f) {
    strcpy(result.clarity, "SLIGHT TURBID (ขุ่นเบา)");
  } else {
    strcpy(result.clarity, "TURBID (ขุ่นแขวนลอย)");
  }
}

// ============================================================
// Render Liquid Optics & Metrology Page on Wio Terminal LCD
// ============================================================
inline void drawLiquidOpticsPage(
    TFT_eSPI &tft,
    const LiquidScanResult &res,
    bool isScanning,
    bool fontLoaded)
{
  tft.fillScreen(TFT_BLACK);

  // 1. Top Header Banner Box
  tft.fillRect(0, 0, 320, 56, 0x0842);

  // Draw Optical Logo at top-left
  extern void drawSpectrometerLogo(int x, int y);
  drawSpectrometerLogo(8, 8);

  // Banner Titles
  if (fontLoaded) {
    tft.loadFont("THSarabunPSK30", SD);
    tft.setTextColor(TFT_YELLOW, 0x0842);
    tft.drawString("วิเคราะห์สมบัติแสงของเหลว", 78, 6);

    tft.loadFont("THSarabunPSK20", SD);
    tft.setTextColor(0x07FF, 0x0842);
    tft.drawString("ดัชนีหักเห ความหนาแน่น สเปกตรัมดูดกลืน", 78, 34);
    tft.unloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_YELLOW, 0x0842);
    tft.drawString("LIQUID OPTICS", 78, 10);

    tft.setTextSize(1);
    tft.setTextColor(0x07FF, 0x0842);
    tft.drawString("Refractive Index & Density Analyzer", 78, 34);
  }

  // Page Indicator Badge
  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("[5/5]", 285, 10);

  // Double Divider Lines
  tft.drawFastHLine(0, 56, 320, TFT_MAGENTA);
  tft.drawFastHLine(0, 58, 320, 0x07FF);

  // 2. Card 1: Physical & Metrological Properties (Left Box)
  tft.fillRoundRect(6, 64, 150, 134, 4, 0x0842);
  tft.drawRoundRect(6, 64, 150, 134, 4, 0x07FF);
  tft.fillRoundRect(7, 65, 148, 22, 3, 0x10E4);

  if (fontLoaded) {
    tft.loadFont("THSarabunPSK20", SD);
    tft.setTextColor(TFT_WHITE, 0x10E4);
    tft.drawString("สมบัติทางกายภาพ", 28, 68);
    tft.unloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_WHITE, 0x10E4);
    tft.drawString("METROLOGY", 22, 68);
  }

  // Refractive Index (Large TextSize 2)
  tft.setTextSize(1);
  tft.setTextColor(TFT_LIGHTGREY, 0x0842);
  tft.drawString("Refractive Index (n):", 12, 92);

  char nBuf[12];
  sprintf(nBuf, "n = %0.4f", res.refractiveIndex_n);
  tft.setTextSize(2);
  tft.setTextColor(0x07FF, 0x0842); // Bright Cyan
  tft.drawString(nBuf, 12, 104);

  // Density (rho in g/cm3)
  tft.setTextSize(1);
  tft.setTextColor(TFT_LIGHTGREY, 0x0842);
  tft.drawString("Density (rho):", 12, 124);

  char rhoBuf[18];
  sprintf(rhoBuf, "%0.3f g/cm3", res.density_g_cm3);
  tft.setTextSize(2);
  tft.setTextColor(TFT_GREEN, 0x0842); // Bright Green
  tft.drawString(rhoBuf, 12, 136);

  // Solute / Brix & Clarity
  tft.setTextSize(1);
  tft.setTextColor(TFT_YELLOW, 0x0842);
  char brixBuf[20];
  sprintf(brixBuf, "Brix: %0.1f degBx", res.brix_deg);
  tft.drawString(brixBuf, 12, 158);

  tft.setTextColor(TFT_WHITE, 0x0842);
  char tBuf[20];
  sprintf(tBuf, "T: %0.1f%% | %s", res.transmittance_pct, (res.absorbance[2] < 0.15f ? "CLEAR" : "TURBID"));
  tft.drawString(tBuf, 12, 172);

  // 3. Card 2: Spectral Absorbance Profile (Right Box)
  tft.fillRoundRect(164, 64, 150, 134, 4, 0x0842);
  tft.drawRoundRect(164, 64, 150, 134, 4, TFT_MAGENTA);
  tft.fillRoundRect(165, 65, 148, 22, 3, 0x2084);

  if (fontLoaded) {
    tft.loadFont("THSarabunPSK20", SD);
    tft.setTextColor(TFT_WHITE, 0x2084);
    tft.drawString("สเปกตรัมการดูดกลืน", 175, 68);
    tft.unloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_WHITE, 0x2084);
    tft.drawString("SPECTRUM A", 172, 68);
  }

  // Absorbance values table
  tft.setTextSize(1);
  const uint16_t rowColors[NUM_SPECTRAL_BANDS] = { 0x07FF, 0x27E0, TFT_GREEN, TFT_YELLOW, TFT_RED };
  for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
    int y = 92 + (i * 15);
    tft.setTextColor(rowColors[i], 0x0842);
    char rowBuf[24];
    sprintf(rowBuf, "%dnm: A = %0.3f", SPECTRAL_WAVELENGTHS[i], res.absorbance[i]);
    tft.drawString(rowBuf, 172, y);
  }

  tft.drawFastHLine(172, 168, 134, 0x2104);

  // Peak detection
  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x0842);
  char peakBuf[24];
  sprintf(peakBuf, "Peak: %dnm (A=%0.2f)", res.peakWavelength, res.peakAbsorbance);
  tft.drawString(peakBuf, 172, 174);

  // 4. Footer Bar
  tft.drawFastHLine(0, 204, 320, TFT_DARKGREY);
  tft.drawFastHLine(0, 206, 320, 0x2104);

  if (isScanning) {
    tft.setTextSize(1);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString(">> SCANNING LIQUID OPTICS IN PROGRESS <<", 30, 216);
  } else {
    if (fontLoaded) {
      tft.loadFont("THSarabunPSK20", SD);
      tft.setTextColor(TFT_YELLOW, TFT_BLACK);
      tft.drawString("[DOWN] สแกนของเหลว | [PRESS] เทียบน้ำกลั่น | [< / >] สลับหน้า", 10, 214);
      tft.unloadFont();
    } else {
      tft.setTextSize(1);
      tft.setTextColor(TFT_YELLOW, TFT_BLACK);
      tft.drawString("[DOWN] Scan Liquid | [PRESS] Water Zero | [< / >] Pages", 10, 216);
    }
  }
}

#endif // LIQUID_ENGINE_H
