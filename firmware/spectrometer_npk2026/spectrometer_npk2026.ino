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
#define BTN_A          WIO_KEY_A     // ขวาสุด
#define BTN_B          WIO_KEY_B     // กลาง
#define BTN_C          WIO_KEY_C     // ซ้ายสุด
#define BTN_JOY_PRESS  WIO_5S_PRESS  // กดลงตรงกลาง
#define BTN_JOY_UP     WIO_5S_UP     // โยกขึ้น -> สลับโหมดวิเคราะห์ (AI / Poly / StdCurve)
#define BTN_JOY_DOWN   WIO_5S_DOWN   // โยกลง -> สั่ง Auto-Scan / Step Calib
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

enum ModelMode {
  MODEL_TINYML  = 0, // [AI] Deep Neural Network (Green)
  MODEL_POLY    = 1, // [PL] Classical Polynomial (Yellow)
  MODEL_STDCURV = 2  // [SC] In-Situ Standard Curve (Cyan)
};

enum CalibNutrient {
  CALIB_N = 0, // Nitrogen (465 nm Blue)
  CALIB_P = 1, // Phosphorus (525 nm Green)
  CALIB_K = 2  // Potassium (625 nm Red)
};

AppScreen currentScreen = PAGE_NPK_METER; // Default to NPK Meter view
ModelMode currentModel  = MODEL_TINYML;
CalibNutrient activeCalibNutrient = CALIB_N;
bool screenChanged = true;

// Calibration & Spectrum Data Objects
CalibrationState calibState;
StandardCurve curveN;
StandardCurve curveP;
StandardCurve curveK;
SpectrumScanResult currentSpectrum;

File myFile;
TFT_eSPI tft;

bool hasSD = false;
bool hasTCS = false;
bool fontLoaded = false;

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
void drawActiveCalibrationScreen();
void logSpectrumToSD();
void logCalibToSD(const char* nutName, const StandardCurve &sc);

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

  // 4. Initialize Baseline & Standard Curves
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

    // Initialize CALIB_LOG.csv
    myFile = SD.open("CALIB_LOG.csv", FILE_APPEND);
    if (myFile) {
      if (myFile.size() == 0) {
        myFile.println("Time,Nutrient,Wavelength_nm,Slope_m,Intercept_c,R2,s_yx,LOD_mg_kg,LOQ_mg_kg");
      }
      myFile.close();
    }

    // Load saved blank & standard curves if available
    if (loadCalibrationFromSD()) {
      Serial.println("Loaded saved full calibration profile from SD card!");
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

  // Initial spectrum scan baseline
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
// Draw Embedded Optical Spectrometer Logo
// ============================================================
void drawSpectrometerLogo(int x, int y) {
  // 1. Triangular Optical Glass Prism
  tft.fillTriangle(x + 24, y + 2, x + 6, y + 38, x + 42, y + 38, 0x10E4);
  tft.drawTriangle(x + 24, y + 2, x + 6, y + 38, x + 42, y + 38, 0x07FF);
  tft.drawTriangle(x + 24, y + 3, x + 7, y + 37, x + 41, y + 37, TFT_WHITE);

  // 2. Incident White Light Beam from Left
  tft.drawLine(x - 6, y + 26, x + 15, y + 22, TFT_WHITE);
  tft.drawLine(x - 6, y + 27, x + 15, y + 23, TFT_WHITE);

  // 3. Emerging Dispersed Spectrum Rays to the Right (5 spectral bands)
  int ox = x + 28;
  int oy = y + 23;
  tft.drawLine(ox, oy, x + 60, y + 6,  0x07FF);    // 465 nm Blue/Cyan
  tft.drawLine(ox, oy, x + 64, y + 14, 0x27E0);    // 500 nm Cyan
  tft.drawLine(ox, oy, x + 66, y + 22, TFT_GREEN);  // 525 nm Green
  tft.drawLine(ox, oy, x + 64, y + 30, TFT_YELLOW); // 590 nm Yellow
  tft.drawLine(ox, oy, x + 60, y + 38, TFT_RED);    // 625 nm Red

  // 4. Agri Seedling Sprout Emblem on right of prism base
  tft.fillCircle(x + 36, y + 30, 4, TFT_GREEN);
  tft.drawCircle(x + 36, y + 30, 4, TFT_YELLOW);
  tft.drawFastVLine(x + 36, y + 32, 6, TFT_GREEN);
  tft.fillCircle(x + 40, y + 25, 3, TFT_YELLOW);
}

// ============================================================
// Page 0: System Dashboard (Large Text & Zero-Tofu Guaranteed)
// ============================================================
void drawDashboardPage() {
  tft.fillScreen(TFT_BLACK);

  // 1. Top Header Banner Box
  tft.fillRect(0, 0, 320, 56, 0x0842);

  // Draw Embedded Optical Prism & Spectrum Logo
  drawSpectrometerLogo(10, 8);

  // Header Titles
  if (fontLoaded) {
    tft.loadFont("THSarabunPSK30", SD);
    tft.setTextColor(TFT_YELLOW, 0x0842);
    tft.drawString("สเปกโทรโฟโตมิเตอร์ NPK", 80, 8);

    tft.loadFont("THSarabunPSK20", SD);
    tft.setTextColor(0x07FF, 0x0842);
    tft.drawString("หน่วยวิจัย AI4D มรภ.รำไพพรรณี", 80, 34);
    tft.unloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_YELLOW, 0x0842);
    tft.drawString("NPK SPECTROMETER", 80, 10);

    tft.setTextSize(1);
    tft.setTextColor(0x07FF, 0x0842);
    tft.drawString("AI4D AgriPhysics - RBRU Research", 80, 34);
  }

  // Page Indicator Badge
  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("[1/4]", 285, 10);

  // Double Divider Lines
  tft.drawFastHLine(0, 56, 320, TFT_MAGENTA);
  tft.drawFastHLine(0, 58, 320, 0x07FF);

  // 2. Card 1: Hardware & Processing Core (Left Box)
  tft.fillRoundRect(6, 64, 150, 134, 4, 0x0842);
  tft.drawRoundRect(6, 64, 150, 134, 4, 0x07FF);
  tft.fillRoundRect(7, 65, 148, 22, 3, 0x10E4);

  // Card 1 Header (Large TextSize 2 or Sarabun font)
  if (fontLoaded) {
    tft.loadFont("THSarabunPSK20", SD);
    tft.setTextColor(TFT_WHITE, 0x10E4);
    tft.drawString("ระบบประมวลผล", 32, 68);
    tft.unloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_WHITE, 0x10E4);
    tft.drawString("PROCESSOR", 18, 68);
  }

  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("SAMD51 120MHz", 14, 94);
  tft.drawString("Cortex-M4F FPU", 14, 108);

  tft.setTextColor(TFT_LIGHTGREY, 0x0842);
  tft.drawString("Flash: 512K (19%)", 14, 122);
  tft.drawString("SRAM: 192KB OK", 14, 136);

  tft.drawFastHLine(14, 152, 134, 0x2104);

  // Model Selection in Large Font (TextSize 2)
  tft.setTextSize(2);
  if (currentModel == MODEL_TINYML) {
    tft.setTextColor(TFT_GREEN, 0x0842);
    tft.drawString("[AI TinyML]", 12, 164);
  } else if (currentModel == MODEL_POLY) {
    tft.setTextColor(TFT_YELLOW, 0x0842);
    tft.drawString("[PL Poly]", 18, 164);
  } else {
    tft.setTextColor(0x07FF, 0x0842);
    tft.drawString("[SC StdCurv]", 10, 164);
  }

  // 3. Card 2: Sensors & Peripherals (Right Box)
  tft.fillRoundRect(164, 64, 150, 134, 4, 0x0842);
  tft.drawRoundRect(164, 64, 150, 134, 4, TFT_MAGENTA);
  tft.fillRoundRect(165, 65, 148, 22, 3, 0x2084);

  // Card 2 Header
  if (fontLoaded) {
    tft.loadFont("THSarabunPSK20", SD);
    tft.setTextColor(TFT_WHITE, 0x2084);
    tft.drawString("อุปกรณ์/เซนเซอร์", 185, 68);
    tft.unloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_WHITE, 0x2084);
    tft.drawString("SENSORS/SD", 175, 68);
  }

  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("TCS34725: ", 172, 94);
  if (hasTCS) {
    tft.setTextColor(TFT_GREEN, 0x0842);
    tft.drawString("[ONLINE]", 238, 94);
  } else {
    tft.setTextColor(TFT_RED, 0x0842);
    tft.drawString("[OFFLINE]", 238, 94);
  }

  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("SD Card: ", 172, 110);
  if (hasSD) {
    tft.setTextColor(TFT_GREEN, 0x0842);
    tft.drawString("[REC OK]", 232, 110);
  } else {
    tft.setTextColor(TFT_DARKGREY, 0x0842);
    tft.drawString("[NO CARD]", 232, 110);
  }

  tft.setTextColor(TFT_LIGHTGREY, 0x0842);
  tft.drawString("LED: 5-Band Optics", 172, 126);
  tft.drawString("File: NPK,SPEC.csv", 172, 140);

  tft.drawFastHLine(172, 152, 134, 0x2104);

  // Large Clock (TextSize 2)
  char timeBuf[16];
  sprintf(timeBuf, "%02d:%02d:%02d", clockHour, clockMin, clockSec);
  tft.setTextSize(2);
  tft.setTextColor(0x07FF, 0x0842); // Bright cyan
  tft.drawString(timeBuf, 195, 164);

  // 4. Footer Bar
  tft.drawFastHLine(0, 204, 320, TFT_DARKGREY);
  tft.drawFastHLine(0, 206, 320, 0x2104);

  if (fontLoaded) {
    tft.loadFont("THSarabunPSK20", SD);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("จอยสติ๊ก [< / >] สลับหน้า  |  [UP] สลับโหมด AI  |  A/B/C เปิด/ปิดไฟ", 15, 214);
    tft.unloadFont();
  } else {
    tft.setTextSize(1);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("[< / >] Pages  |  [UP] Model Mode  |  A/B/C: LEDs", 14, 216);
  }
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
  if (currentModel == MODEL_TINYML) {
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString("[AI]", 262, 36);
  } else if (currentModel == MODEL_POLY) {
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("[PL]", 262, 36);
  } else {
    tft.setTextColor(0x07FF, TFT_BLACK); // Cyan for Standard Curve
    tft.drawString("[SC]", 262, 36);
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
// Page 3: Calibration & Standard Curve Wizard
// ============================================================
void drawActiveCalibrationScreen() {
  if (activeCalibNutrient == CALIB_N) {
    drawStandardCurvePlot(tft, curveN, "NITROGEN (N) [465nm]", 0x07FF); // Cyan/Blue
  } else if (activeCalibNutrient == CALIB_P) {
    drawStandardCurvePlot(tft, curveP, "PHOSPHORUS (P) [525nm]", TFT_GREEN);
  } else {
    drawStandardCurvePlot(tft, curveK, "POTASSIUM (K) [625nm]", TFT_RED);
  }
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
// Log Calibration Curve to SD Card
// ============================================================
void logCalibToSD(const char* nutName, const StandardCurve &sc) {
  if (!hasSD) return;
  myFile = SD.open("CALIB_LOG.csv", FILE_APPEND);
  if (myFile) {
    char timeStr[12];
    sprintf(timeStr, "%02d:%02d:%02d", clockHour, clockMin, clockSec);

    uint16_t wl = (strcmp(nutName, "N") == 0) ? 465 : (strcmp(nutName, "P") == 0 ? 525 : 625);

    myFile.print(timeStr); myFile.print(",");
    myFile.print(nutName); myFile.print(",");
    myFile.print(wl); myFile.print(",");
    myFile.print(sc.slope_m, 5); myFile.print(",");
    myFile.print(sc.intercept_c, 4); myFile.print(",");
    myFile.print(sc.r_squared, 4); myFile.print(",");
    myFile.print(sc.s_yx, 4); myFile.print(",");
    myFile.print(sc.lod, 2); myFile.print(",");
    myFile.println(sc.loq, 2);
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
      updateLedOutput();
    } else if (currentScreen == PAGE_CALIBRATE) {
      // Step-by-Step Multi-Point Calibration Wizard
      StandardCurve* targetCurve = (activeCalibNutrient == CALIB_N) ? &curveN :
                                   ((activeCalibNutrient == CALIB_P) ? &curveP : &curveK);

      // Measure current sample absorbance
      SpectrumScanResult sweepRes;
      executeAutoWavelengthScan(strip, tcs, calibState, sweepRes, hasTCS);
      updateLedOutput();

      int bandIdx = (activeCalibNutrient == CALIB_N) ? 0 :
                    ((activeCalibNutrient == CALIB_P) ? 2 : 4);

      // Record absorbance for current step
      targetCurve->absorbances[targetCurve->currentStep] = sweepRes.absorbance[bandIdx];
      targetCurve->currentStep = (targetCurve->currentStep + 1) % NUM_STD_POINTS;

      // Fit OLS line once all points are populated
      fitStandardCurve(*targetCurve);
      saveCalibrationToSD();

      const char* nName = (activeCalibNutrient == CALIB_N) ? "N" :
                          ((activeCalibNutrient == CALIB_P) ? "P" : "K");
      logCalibToSD(nName, *targetCurve);

      drawActiveCalibrationScreen();
    }
    delay(150);
  }

  // 1.3 Analytical Model Toggle (Joystick Up in NPK Screen)
  if (btnJoyUp == LOW && lastBtnJoyUp == HIGH) {
    if (currentScreen == PAGE_NPK_METER) {
      currentModel = (ModelMode)((currentModel + 1) % 3);
      drawModelModeBadge();
    }
    delay(150);
  }

  // 1.4 Top Buttons A, B, C Handling (Context Sensitive)
  if (btnA == LOW && lastBtnA == HIGH) {
    if (currentScreen == PAGE_CALIBRATE) {
      activeCalibNutrient = CALIB_K; // Select Potassium
      drawActiveCalibrationScreen();
    } else {
      ledRedState = !ledRedState;
      updateLedOutput();
    }
    delay(150);
  }
  if (btnB == LOW && lastBtnB == HIGH) {
    if (currentScreen == PAGE_CALIBRATE) {
      activeCalibNutrient = CALIB_P; // Select Phosphorus
      drawActiveCalibrationScreen();
    } else {
      ledGreenState = !ledGreenState;
      updateLedOutput();
    }
    delay(150);
  }
  if (btnC == LOW && lastBtnC == HIGH) {
    if (currentScreen == PAGE_CALIBRATE) {
      activeCalibNutrient = CALIB_N; // Select Nitrogen
      drawActiveCalibrationScreen();
    } else {
      ledBlueState = !ledBlueState;
      updateLedOutput();
    }
    delay(150);
  }

  // 1.5 Joystick Press (Context Sensitive)
  if (btnJoyPress == LOW && lastBtnJoyPress == HIGH) {
    if (currentScreen == PAGE_CALIBRATE) {
      // Capture & Save Zero Blanking on all 5 channels
      tft.setTextColor(TFT_YELLOW, TFT_BLACK);
      tft.drawString("MEASURING REFERENCE BLANK...", 16, 180);
      captureBlankReference(strip, tcs, calibState, hasTCS);
      updateLedOutput();
      drawActiveCalibrationScreen();
    } else {
      // Toggle White LED in other screens
      bool allOn = (ledRedState && ledGreenState && ledBlueState);
      if (allOn) {
        ledRedState = false; ledGreenState = false; ledBlueState = false;
      } else {
        ledRedState = true;  ledGreenState = true;  ledBlueState = true;
      }
      updateLedOutput();
    }
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
        drawActiveCalibrationScreen();
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

    if (currentModel == MODEL_TINYML) {
      // 1. TinyML Edge AI Deep Neural Network
      float c_ratio = (rgb > 0.0f) ? ((float)c / rgb) : 1.0f;
      float lux_norm = (float)lux / 1000.0f;
      float abs_est = (c > 0) ? -log10f(constrain((rgb / (float)c), 0.01f, 0.99f)) : 0.0f;

      float raw_inputs[TINYML_INPUT_DIM] = { bb, gg, rr, c_ratio, lux_norm, abs_est };
      float ml_outputs[TINYML_OUTPUT_DIM];

      tinyml_predict(raw_inputs, ml_outputs);

      valN = ml_outputs[0];
      valP = ml_outputs[1];
      valK = ml_outputs[2];
    } else if (currentModel == MODEL_POLY) {
      // 2. Classical Polynomial Equations
      valN = calcN_Poly(bb);
      valP = calcP_Poly(gg);
      valK = calcK_Poly(rr);
    } else {
      // 3. In-Situ Standard Curve Calibration (C = (A - c) / m)
      float I_b_corr = max(1.0f, (float)b - calibState.darkCurrent[0]);
      float I_g_corr = max(1.0f, (float)g - calibState.darkCurrent[2]);
      float I_r_corr = max(1.0f, (float)r - calibState.darkCurrent[4]);

      float I_b_blank = max(1.0f, calibState.blankIntensity[0] - calibState.darkCurrent[0]);
      float I_g_blank = max(1.0f, calibState.blankIntensity[2] - calibState.darkCurrent[2]);
      float I_r_blank = max(1.0f, calibState.blankIntensity[4] - calibState.darkCurrent[4]);

      float A_blue  = -log10f(constrain(I_b_corr / I_b_blank, 0.001f, 1.50f));
      float A_green = -log10f(constrain(I_g_corr / I_g_blank, 0.001f, 1.50f));
      float A_red   = -log10f(constrain(I_r_corr / I_r_blank, 0.001f, 1.50f));

      valN = calculateConcentration_SC(A_blue, curveN);
      valP = calculateConcentration_SC(A_green, curveP);
      valK = calculateConcentration_SC(A_red, curveK);
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
        const char* mStr = (currentModel == MODEL_TINYML) ? "TinyML" :
                           ((currentModel == MODEL_POLY) ? "Poly" : "StdCurve");
        myFile.println(mStr);
        myFile.close();
      }
    }
  }
}
