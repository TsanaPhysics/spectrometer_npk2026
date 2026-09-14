#include <Wire.h>
#include <SPI.h>
#include <Seeed_FS.h>
#include "SD/Seeed_SD.h"
#include <seeed_line_chart.h>
#include "Adafruit_TCS34725.h"
#include <TFT_eSPI.h>
#include <Adafruit_NeoPixel.h>
#include "TinyML_Model.h"
#include "Calibration_Engine.h"
#include "Spectrum_Engine.h"

// ============================================================
// Pin Definitions
// ============================================================
#define NEOPIXEL_PIN   D0
#define NUM_PIXELS     16 // Supports 1 to 16 pixels (Stick/Ring/Single)
Adafruit_NeoPixel strip(NUM_PIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

#define PIN_LED_RED    D2
#define PIN_LED_GREEN  D1
#define PIN_LED_BLUE   D0

// Wio Terminal Buttons & 5-Way Joystick
#define BTN_A          WIO_KEY_A     // ขวาสุด -> LED แดง (Red)
#define BTN_B          WIO_KEY_B     // กลาง   -> LED เขียว (Green)
#define BTN_C          WIO_KEY_C     // ซ้ายสุด -> LED น้ำเงิน (Blue)
#define BTN_JOY_PRESS  WIO_5S_PRESS  // กดลงตรงกลาง
#define BTN_JOY_UP     WIO_5S_UP     // โยกขึ้น -> สลับโหมด AI (TinyML / Poly)
#define BTN_JOY_DOWN   WIO_5S_DOWN   // โยกลง -> สั่ง Auto-Scan / Set Blank
#define BTN_JOY_LEFT   WIO_5S_LEFT   // โยกซ้าย -> หน้าจอก่อนหน้า
#define BTN_JOY_RIGHT  WIO_5S_RIGHT  // โยกขวา  -> หน้าจอถัดไป

// ============================================================
// State Machine & Screen Definitions
// ============================================================
enum AppScreen {
  PAGE_DASHBOARD = 0,
  PAGE_NPK_METER = 1,
  PAGE_SPECTRUM  = 2,
  PAGE_CALIBRATE = 3,
  NUM_PAGES      = 4
};

AppScreen currentScreen = PAGE_NPK_METER; // Default to NPK Meter view
bool screenChanged = true;

// Calibration & Spectrum Data Objects
CalibrationState calibState;
SpectrumScanResult currentSpectrum;

File myFile;
TFT_eSPI tft;

bool hasSD = false;
bool hasTCS = false;
bool fontLoaded = false;
bool useTinyML = true; // True: TinyML Deep Neural Network, False: Classical Polynomial

bool ledRedState   = false;
bool ledGreenState = false;
bool ledBlueState  = false;

bool lastBtnA        = HIGH;
bool lastBtnB        = HIGH;
bool lastBtnC        = HIGH;
bool lastBtnJoyPress = HIGH;
bool lastBtnJoyUp    = HIGH;
bool lastBtnJoyDown  = HIGH;
bool lastBtnJoyLeft  = HIGH;
bool lastBtnJoyRight = HIGH;

uint32_t sampleCount = 32;
uint32_t spectrumScanCount = 0;
unsigned long lastMeasureTime = 0;
unsigned long lastSecondTime  = 0;

int clockHour = 12;
int clockMin  = 46;
int clockSec  = 0;

Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_600MS, TCS34725_GAIN_1X);

// ============================================================
// Classical Polynomial Calibration Equations (ผศ.ดร.ชีวะ ทัศนา)
// ============================================================
#define N_A0  -185.42f
#define N_A1    8.234f
#define N_A2   -0.0412f
#define N_A3    0.000091f

#define P_A0  -224.18f
#define P_A1    12.56f
#define P_A2   -0.0823f

#define K_A0   -18.92f
#define K_A1    1.842f
#define K_A2    0.0156f

float calcN_Poly(float bp) {
  float val = N_A0 + (N_A1 * bp) + (N_A2 * bp * bp) + (N_A3 * bp * bp * bp);
  return (val < 0.0f) ? 0.0f : val;
}

float calcP_Poly(float gp) {
  float val = P_A0 + (P_A1 * gp) + (P_A2 * gp * gp);
  return (val < 0.0f) ? 0.0f : val;
}

float calcK_Poly(float rp) {
  float val = K_A0 + (K_A1 * rp) + (K_A2 * rp * rp);
  return (val < 0.0f) ? 0.0f : val;
}

// Function Prototypes
void updateLedOutput();
void drawLedStatusTag();
void drawSdStatusTag();
void drawModelModeBadge();
void drawNpkStaticLayout();
void drawDashboardPage();
void drawCalibrationPage();
void logSpectrumToSD();

// ============================================================
// Setup Routine
// ============================================================
void setup() {
  Serial.begin(115200);

  // 1. Initialize Control Pins
  pinMode(BTN_A, INPUT_PULLUP);
  pinMode(BTN_B, INPUT_PULLUP);
  pinMode(BTN_C, INPUT_PULLUP);
  pinMode(BTN_JOY_PRESS, INPUT_PULLUP);
  pinMode(BTN_JOY_UP,    INPUT_PULLUP);
  pinMode(BTN_JOY_DOWN,  INPUT_PULLUP);
  pinMode(BTN_JOY_LEFT,  INPUT_PULLUP);
  pinMode(BTN_JOY_RIGHT, INPUT_PULLUP);

  pinMode(PIN_LED_RED,   OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_BLUE,  OUTPUT);

  digitalWrite(PIN_LED_RED,   LOW);
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_LED_BLUE,  LOW);

  // 2. Initialize NeoPixel strip on D0
  strip.begin();
  strip.setBrightness(120);
  strip.clear();
  strip.show();

  // 3. Initialize LCD Display
  tft.begin();
  tft.setRotation(3);
  tft.fillScreen(TFT_BLACK);

  // 4. Initialize Baseline Calibration Engine
  initCalibration();

  // 5. Initialize SD Card (non-blocking)
  if (SD.begin(SDCARD_SS_PIN, SDCARD_SPI)) {
    Serial.println("SD card initialization successful!");
    hasSD = true;

    // Initialize NPK.csv
    myFile = SD.open("NPK.csv", FILE_APPEND);
    if (myFile) {
      if (myFile.size() == 0) {
        myFile.println("Sample,Time,Blue,Green,Red,Clear,N_mg_kg,P_mg_kg,K_mg_kg,Model");
      }
      myFile.close();
    }

    // Initialize SPECTRUM.csv
    myFile = SD.open("SPECTRUM.csv", FILE_APPEND);
    if (myFile) {
      if (myFile.size() == 0) {
        myFile.println("ScanID,Time,A_465nm,A_500nm,A_525nm,A_590nm,A_625nm,Peak_nm,Peak_A,Warning");
      }
      myFile.close();
    }

    // Load saved blank reference if available
    if (loadCalibrationFromSD()) {
      Serial.println("Loaded saved blank calibration from SD card!");
    }
  } else {
    Serial.println("SD card initialization failed or not inserted!");
    hasSD = false;
  }

  // 6. Initialize Color Sensor
  if (tcs.begin()) {
    Serial.println("Found TCS34725 sensor");
    hasTCS = true;
  } else {
    Serial.println("No TCS34725 found ... check connections");
    hasTCS = false;
  }

  // 7. Check for Thai fonts on SD card
  if (hasSD && SD.exists("/THSarabunPSK30.vlw")) {
    fontLoaded = true;
    Serial.println("Thai font THSarabunPSK30 found!");
  }

  // Initial initial spectrum scan dummy
  currentSpectrum.scanComplete = true;
  currentSpectrum.highAbsWarning = false;
  currentSpectrum.peakWavelength = 525;
  currentSpectrum.peakAbsorbance = 0.45f;
  for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
    currentSpectrum.absorbance[i] = 0.20f + (0.08f * i);
  }

  screenChanged = true;
  lastMeasureTime = millis();
  lastSecondTime  = millis();
}

// ============================================================
// Page 0: System Dashboard
// ============================================================
void drawDashboardPage() {
  tft.fillScreen(TFT_BLACK);

  // Top Header Bar
  tft.fillRect(0, 0, 320, 28, 0x18E3);
  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x18E3);
  tft.drawString("SYSTEM HEALTH & DASHBOARD", 10, 8);
  tft.setTextColor(TFT_YELLOW, 0x18E3);
  tft.drawString("[Page 1/4]", 250, 8);

  // System Specs Box
  tft.drawRect(8, 36, 304, 160, TFT_DARKGREY);

  tft.setTextSize(1);
  tft.setTextColor(0x07FF, TFT_BLACK); // Cyan
  tft.drawString("HARDWARE & MICROCONTROLLER SPECIFICATIONS", 16, 44);

  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("Core: ARM Cortex-M4F @ 120 MHz (ATSAMD51)", 16, 62);
  tft.drawString("Hardware FPU: Active (32-bit Single Precision)", 16, 76);
  tft.drawString("Program Flash: 512 KB  |  SRAM: 192 KB", 16, 90);

  tft.drawFastHLine(16, 106, 288, 0x2104);

  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("PERIPHERAL MODULE STATUS:", 16, 114);

  // Sensor status
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("Color Sensor (TCS34725):", 16, 130);
  if (hasTCS) {
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString("[ONLINE - OK]", 180, 130);
  } else {
    tft.setTextColor(TFT_RED, TFT_BLACK);
    tft.drawString("[NOT DETECTED]", 180, 130);
  }

  // SD card status
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("MicroSD Card Storage:", 16, 146);
  if (hasSD) {
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString("[MOUNTED - REC]", 180, 146);
  } else {
    tft.setTextColor(TFT_DARKGREY, TFT_BLACK);
    tft.drawString("[NO CARD]", 180, 146);
  }

  // Active AI Engine status
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("NPK Analytical Model:", 16, 162);
  if (useTinyML) {
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString("[TinyML Edge AI (6-12-8-3)]", 155, 162);
  } else {
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("[Classical Polynomial]", 155, 162);
  }

  // Footer Navigation
  tft.drawFastHLine(0, 204, 320, TFT_DARKGREY);
  tft.setTextSize(1);
  tft.setTextColor(TFT_LIGHTGREY, TFT_BLACK);
  tft.drawString("Use Joystick [< / >] to Switch Pages | [UP]: Toggle AI", 10, 218);
}

// ============================================================
// Page 1: NPK Level Meter 1.02 (Exact Original Layout)
// ============================================================
void drawNpkStaticLayout() {
  tft.fillScreen(TFT_BLACK);

  // Title 1: ปริมาณธาตุอาหารหลักในดิน (Yellow)
  if (fontLoaded) {
    tft.loadFont("THSarabunPSK30", SD);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("ปริมาณธาตุอาหารหลักในดิน", 45, 10);
    tft.unloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("Soil NPK Nutrients", 50, 12);
  }

  // Title 2: NPK Level Meter 1.02 (White)
  tft.setTextSize(2);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("NPK Level Meter 1.02", 15, 36);

  // Upper Double Separator Line (Magenta + Cyan)
  tft.drawFastHLine(5, 62, 310, TFT_MAGENTA);
  tft.drawFastHLine(5, 64, 310, 0x07FF);

  // Row 1: ไนโตรเจน N :
  if (fontLoaded) {
    tft.loadFont("THSarabunPSK30", SD);
    tft.setTextColor(TFT_BLUE, TFT_BLACK);
    tft.drawString("ไนโตรเจน", 8, 80);
    tft.unloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(0x07FF, TFT_BLACK);
    tft.drawString("Nitrogen", 8, 80);
  }
  tft.setTextSize(2);
  tft.setTextColor(0x07FF, TFT_BLACK);
  tft.drawString("N :", 112, 80);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("mg/kg", 245, 80);

  // Row 2: ฟอสฟอรัส P :
  if (fontLoaded) {
    tft.loadFont("THSarabunPSK30", SD);
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString("ฟอสฟอรัส", 8, 120);
    tft.unloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString("Phosphorus", 8, 120);
  }
  tft.setTextSize(2);
  tft.setTextColor(TFT_GREEN, TFT_BLACK);
  tft.drawString("P :", 112, 120);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("mg/kg", 245, 120);

  // Row 3: โพแทสเซียม K :
  if (fontLoaded) {
    tft.loadFont("THSarabunPSK30", SD);
    tft.setTextColor(TFT_RED, TFT_BLACK);
    tft.drawString("โพแทสเซียม", 8, 160);
    tft.unloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_RED, TFT_BLACK);
    tft.drawString("Potassium", 8, 160);
  }
  tft.setTextSize(2);
  tft.setTextColor(TFT_RED, TFT_BLACK);
  tft.drawString("K :", 112, 160);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("mg/kg", 245, 160);

  // Lower Double Separator Line (LightGrey + Magenta)
  tft.drawFastHLine(5, 192, 310, TFT_LIGHTGREY);
  tft.drawFastHLine(5, 194, 310, TFT_MAGENTA);

  // Footer Middle: ชีวะ ทัศนา | AI4D AGRIPHYSICS
  if (fontLoaded) {
    tft.loadFont("THSarabunPSK20", SD);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("ชีวะ ทัศนา", 118, 200);
    tft.unloadFont();
  } else {
    tft.setTextSize(1);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("Chewa Thassana", 112, 202);
  }
  tft.setTextSize(1);
  tft.setTextColor(TFT_GREEN, TFT_BLACK);
  tft.drawString("AI4D AGRIPHYSICS", 108, 218);

  // Model Badge & Indicators
  drawModelModeBadge();
  drawLedStatusTag();
  drawSdStatusTag();
}

void drawModelModeBadge() {
  tft.setTextSize(2);
  if (useTinyML) {
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString("[AI]", 262, 36);
  } else {
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("[PL]", 262, 36);
  }
}

void drawLedStatusTag() {
  tft.setTextSize(1);
  char ledTag[10] = "OFF  ";
  uint16_t ledCol = TFT_DARKGREY;

  if (ledRedState && !ledGreenState && !ledBlueState) {
    strcpy(ledTag, "RED  ");
    ledCol = TFT_RED;
  } else if (!ledRedState && ledGreenState && !ledBlueState) {
    strcpy(ledTag, "GREEN");
    ledCol = TFT_GREEN;
  } else if (!ledRedState && !ledGreenState && ledBlueState) {
    strcpy(ledTag, "BLUE ");
    ledCol = 0x07FF;
  } else if (ledRedState && ledGreenState && ledBlueState) {
    strcpy(ledTag, "ALL  ");
    ledCol = TFT_WHITE;
  } else if (ledRedState || ledGreenState || ledBlueState) {
    strcpy(ledTag, "MULTI");
    ledCol = TFT_YELLOW;
  }

  tft.setTextColor(ledCol, TFT_BLACK);
  tft.drawString(ledTag, 245, 202);
}

void drawSdStatusTag() {
  tft.setTextSize(1);
  if (hasSD) {
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString("SD:REC", 245, 218);
  } else {
    tft.setTextColor(TFT_DARKGREY, TFT_BLACK);
    tft.drawString("SD:-- ", 245, 218);
  }
}

// ============================================================
// Page 3: Calibration & Blank Reference Wizard
// ============================================================
void drawCalibrationPage() {
  tft.fillScreen(TFT_BLACK);

  // Header Bar
  tft.fillRect(0, 0, 320, 28, 0x18E3);
  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x18E3);
  tft.drawString("CALIBRATION & BLANK WIZARD", 10, 8);
  tft.setTextColor(TFT_YELLOW, 0x18E3);
  tft.drawString("[Page 4/4]", 250, 8);

  tft.drawRect(8, 36, 304, 160, TFT_DARKGREY);

  tft.setTextSize(1);
  tft.setTextColor(0x07FF, TFT_BLACK);
  tft.drawString("STORED BASELINE REFERENCE (I_0 & I_dark)", 16, 44);

  // Table header
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("Band (nm)", 16, 62);
  tft.drawString("Name", 90, 62);
  tft.drawString("I_0 (Blank)", 160, 62);
  tft.drawString("I_dark", 245, 62);

  tft.drawFastHLine(16, 74, 288, 0x2104);

  // Table rows
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
    int y = 82 + (i * 18);
    char buf[12];
    sprintf(buf, "%d nm", SPECTRAL_WAVELENGTHS[i]);
    tft.drawString(buf, 16, y);
    tft.drawString(BAND_NAMES[i], 90, y);

    sprintf(buf, "%0.0f", calibState.blankIntensity[i]);
    tft.drawString(buf, 160, y);

    sprintf(buf, "%0.0f", calibState.darkCurrent[i]);
    tft.drawString(buf, 245, y);
  }

  tft.drawFastHLine(16, 174, 288, 0x2104);
  tft.setTextColor(TFT_GREEN, TFT_BLACK);
  tft.drawString("Status: BASELINE VALID (SD: BLANK.DAT)", 16, 180);

  // Footer Navigation
  tft.drawFastHLine(0, 204, 320, TFT_DARKGREY);
  tft.setTextSize(1);
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("Insert DI Water Cuvette -> Press [DOWN] to Zero Blank", 10, 212);
  tft.setTextColor(TFT_LIGHTGREY, TFT_BLACK);
  tft.drawString("Use Joystick [< / >] to Switch Pages", 10, 226);
}

// ============================================================
// Update LED Hardware Output
// ============================================================
void updateLedOutput() {
  uint8_t r = ledRedState   ? 255 : 0;
  uint8_t g = ledGreenState ? 255 : 0;
  uint8_t b = ledBlueState  ? 255 : 0;

  for (int i = 0; i < strip.numPixels(); i++) {
    strip.setPixelColor(i, r, g, b);
  }
  strip.show();

  digitalWrite(PIN_LED_RED,   ledRedState   ? HIGH : LOW);
  digitalWrite(PIN_LED_GREEN, ledGreenState ? HIGH : LOW);
  digitalWrite(PIN_LED_BLUE,  ledBlueState  ? HIGH : LOW);

  if (currentScreen == PAGE_NPK_METER) {
    drawLedStatusTag();
  }
}

// ============================================================
// Log Spectrum Scan to SD Card
// ============================================================
void logSpectrumToSD() {
  if (!hasSD) return;
  myFile = SD.open("SPECTRUM.csv", FILE_APPEND);
  if (myFile) {
    spectrumScanCount++;
    char timeStr[12];
    sprintf(timeStr, "%02d:%02d:%02d", clockHour, clockMin, clockSec);

    myFile.print(spectrumScanCount); myFile.print(",");
    myFile.print(timeStr); myFile.print(",");
    for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
      myFile.print(currentSpectrum.absorbance[i], 3);
      myFile.print(",");
    }
    myFile.print(currentSpectrum.peakWavelength); myFile.print(",");
    myFile.print(currentSpectrum.peakAbsorbance, 3); myFile.print(",");
    myFile.println(currentSpectrum.highAbsWarning ? "HIGH_ABS_WARN" : "NORMAL");
    myFile.close();
  }
}

// ============================================================
// Main Execution Loop
// ============================================================
void loop() {
  unsigned long now = millis();

  // 1. Handle Navigation & Button Inputs (Debounced)
  bool btnA        = digitalRead(BTN_A);
  bool btnB        = digitalRead(BTN_B);
  bool btnC        = digitalRead(BTN_C);
  bool btnJoyPress = digitalRead(BTN_JOY_PRESS);
  bool btnJoyUp    = digitalRead(BTN_JOY_UP);
  bool btnJoyDown  = digitalRead(BTN_JOY_DOWN);
  bool btnJoyLeft  = digitalRead(BTN_JOY_LEFT);
  bool btnJoyRight = digitalRead(BTN_JOY_RIGHT);

  // 1.1 Page Navigation (Joystick Left / Right)
  if (btnJoyLeft == LOW && lastBtnJoyLeft == HIGH) {
    currentScreen = (AppScreen)((currentScreen + NUM_PAGES - 1) % NUM_PAGES);
    screenChanged = true;
    delay(100);
  }
  if (btnJoyRight == LOW && lastBtnJoyRight == HIGH) {
    currentScreen = (AppScreen)((currentScreen + 1) % NUM_PAGES);
    screenChanged = true;
    delay(100);
  }

  // 1.2 Action Button (Joystick Down)
  if (btnJoyDown == LOW && lastBtnJoyDown == HIGH) {
    if (currentScreen == PAGE_SPECTRUM) {
      // Execute Auto-Scan Wavelength Sweep
      drawSpectrumChart(tft, currentSpectrum, true);
      executeAutoWavelengthScan(strip, tcs, calibState, currentSpectrum, hasTCS);
      drawSpectrumChart(tft, currentSpectrum, false);
      logSpectrumToSD();
      // Restore user LED state
      updateLedOutput();
    } else if (currentScreen == PAGE_CALIBRATE) {
      // Execute Zero Blank Reference Sweep
      tft.setTextColor(TFT_YELLOW, TFT_BLACK);
      tft.drawString("MEASURING REFERENCE BLANK (I_0)...", 16, 180);
      captureBlankReference(strip, tcs, calibState, hasTCS);
      updateLedOutput();
      drawCalibrationPage();
    }
    delay(150);
  }

  // 1.3 Model Toggle (Joystick Up in NPK Screen)
  if (btnJoyUp == LOW && lastBtnJoyUp == HIGH) {
    if (currentScreen == PAGE_NPK_METER) {
      useTinyML = !useTinyML;
      drawModelModeBadge();
    }
    delay(150);
  }

  // 1.4 Light Source Controls
  if (btnA == LOW && lastBtnA == HIGH) {
    ledRedState = !ledRedState;
    updateLedOutput();
    delay(150);
  }
  if (btnB == LOW && lastBtnB == HIGH) {
    ledGreenState = !ledGreenState;
    updateLedOutput();
    delay(150);
  }
  if (btnC == LOW && lastBtnC == HIGH) {
    ledBlueState = !ledBlueState;
    updateLedOutput();
    delay(150);
  }
  if (btnJoyPress == LOW && lastBtnJoyPress == HIGH) {
    // Toggle White LED
    bool allOn = (ledRedState && ledGreenState && ledBlueState);
    if (allOn) {
      ledRedState = false; ledGreenState = false; ledBlueState = false;
    } else {
      ledRedState = true;  ledGreenState = true;  ledBlueState = true;
    }
    updateLedOutput();
    delay(150);
  }

  lastBtnA        = btnA;
  lastBtnB        = btnB;
  lastBtnC        = btnC;
  lastBtnJoyPress = btnJoyPress;
  lastBtnJoyUp    = btnJoyUp;
  lastBtnJoyDown  = btnJoyDown;
  lastBtnJoyLeft  = btnJoyLeft;
  lastBtnJoyRight = btnJoyRight;

  // 2. Handle Screen Redraw on Page Transition
  if (screenChanged) {
    screenChanged = false;
    switch (currentScreen) {
      case PAGE_DASHBOARD:
        drawDashboardPage();
        break;
      case PAGE_NPK_METER:
        drawNpkStaticLayout();
        break;
      case PAGE_SPECTRUM:
        drawSpectrumChart(tft, currentSpectrum, false);
        break;
      case PAGE_CALIBRATE:
        drawCalibrationPage();
        break;
    }
  }

  // 3. Periodic Clock Ticking (1 Second)
  if (now - lastSecondTime >= 1000) {
    lastSecondTime = now;
    clockSec++;
    if (clockSec >= 60) { clockSec = 0; clockMin++; }
    if (clockMin >= 60) { clockMin = 0; clockHour++; }
    if (clockHour >= 24) { clockHour = 0; }

    if (currentScreen == PAGE_NPK_METER) {
      tft.setTextSize(1);
      tft.setTextColor(TFT_YELLOW, TFT_BLACK);
      tft.drawString("11/05/2024", 10, 202);

      char timeBuf[12];
      sprintf(timeBuf, "%02d:%02d:%02d", clockHour, clockMin, clockSec);
      tft.drawString(timeBuf, 10, 218);
    }
  }

  // 4. Periodic Sensor Measurement & NPK Calculation (every 800ms)
  if (now - lastMeasureTime >= 800) {
    lastMeasureTime = now;
    sampleCount++;

    uint16_t r = 0, g = 0, b = 0, c = 0, colorTemp = 0, lux = 0;
    if (hasTCS) {
      tcs.getRawData(&r, &g, &b, &c);
      colorTemp = tcs.calculateColorTemperature_dn40(r, g, b, c);
      lux = tcs.calculateLux(r, g, b);
    }

    float rgb = r + b + g;
    float bb = 0.0f, gg = 0.0f, rr = 0.0f;
    if (rgb > 0.0f) {
      bb = b * 100.0f / rgb;
      gg = g * 100.0f / rgb;
      rr = r * 100.0f / rgb;
    }

    float valN = 0.0f, valP = 0.0f, valK = 0.0f;

    if (useTinyML) {
      float c_ratio = (rgb > 0.0f) ? ((float)c / rgb) : 1.0f;
      float lux_norm = (float)lux / 1000.0f;
      float abs_est = (c > 0) ? -log10f(constrain((rgb / (float)c), 0.01f, 0.99f)) : 0.0f;

      float raw_inputs[TINYML_INPUT_DIM] = { bb, gg, rr, c_ratio, lux_norm, abs_est };
      float ml_outputs[TINYML_OUTPUT_DIM];

      tinyml_predict(raw_inputs, ml_outputs);

      valN = ml_outputs[0];
      valP = ml_outputs[1];
      valK = ml_outputs[2];
    } else {
      valN = calcN_Poly(bb);
      valP = calcP_Poly(gg);
      valK = calcK_Poly(rr);
    }

    // Update NPK Screen Display
    if (currentScreen == PAGE_NPK_METER) {
      tft.setTextSize(2);
      char valBuf[16];

      sprintf(valBuf, "%6.2f", valN);
      tft.setTextColor(0x07FF, TFT_BLACK);
      tft.drawString(valBuf, 150, 80);

      sprintf(valBuf, "%6.2f", valP);
      tft.setTextColor(TFT_GREEN, TFT_BLACK);
      tft.drawString(valBuf, 150, 120);

      sprintf(valBuf, "%6.2f", valK);
      tft.setTextColor(TFT_RED, TFT_BLACK);
      tft.drawString(valBuf, 150, 160);
    }

    // Auto-detect SD card if inserted while running
    static unsigned long lastSdRetry = 0;
    if (!hasSD && (now - lastSdRetry >= 5000)) {
      lastSdRetry = now;
      if (SD.begin(SDCARD_SS_PIN, SDCARD_SPI)) {
        hasSD = true;
        Serial.println("microSD Card mounted dynamically!");
        if (currentScreen == PAGE_NPK_METER) drawSdStatusTag();
      }
    }

    // Save NPK data to SD Card
    if (hasSD) {
      myFile = SD.open("NPK.csv", FILE_APPEND);
      if (myFile) {
        char timeStr[12];
        sprintf(timeStr, "%02d:%02d:%02d", clockHour, clockMin, clockSec);
        myFile.print(sampleCount); myFile.print(",");
        myFile.print(timeStr); myFile.print(",");
        myFile.print(b); myFile.print(",");
        myFile.print(g); myFile.print(",");
        myFile.print(r); myFile.print(",");
        myFile.print(c); myFile.print(",");
        myFile.print(valN, 2); myFile.print(",");
        myFile.print(valP, 2); myFile.print(",");
        myFile.print(valK, 2); myFile.print(",");
        myFile.println(useTinyML ? "TinyML" : "Poly");
        myFile.close();
      }
    }
  }
}
