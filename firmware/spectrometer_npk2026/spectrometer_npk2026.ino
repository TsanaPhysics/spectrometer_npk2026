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
#include "Liquid_Engine.h"
#include "WiFi_Server_Engine.h"
#include "npk_calibration_matrices.h"
#include "phosphorus_q1_models.h"
#include "soil_ph_model.h"

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
// State Machine & Screen Definitions (8 Separated Specialized Screens)
// ============================================================
enum AppScreen {
  PAGE_DASHBOARD = 0, // 1/8 Overview Dashboard
  PAGE_NITROGEN  = 1, // 2/8 Dedicated Nitrogen Assay (Indophenol Blue 465/525nm + 3-Tier)
  PAGE_PHOSPHORUS= 2, // 3/8 Dedicated Phosphorus Assay (Molybdenum Blue 625nm + Q1 Poly)
  PAGE_POTASSIUM = 3, // 4/8 Dedicated Potassium Assay (Turbidimetry 625nm)
  PAGE_SOIL_PH   = 4, // 5/8 Dedicated Soil pH Assay (Ratiometric Green/Red 525/625nm)
  PAGE_NPK_METER = 5, // 6/8 NPK & pH Summary Overview Meter
  PAGE_SPECTRUM  = 6, // 7/8 5-Band Real-Time Spectral Scan
  PAGE_CALIBRATE = 7, // 8/8 Multi-Point Field In-Situ Standard Curve Wizard
  NUM_PAGES      = 8
};

enum ModelMode {
  MODEL_TINYML  = 0, // [AI] Deep Neural Network (Green)
  MODEL_POLY    = 1, // [PL] Classical Polynomial (Yellow)
  MODEL_STDCURV = 2  // [SC] In-Situ Standard Curve (Cyan)
};

enum CalibNutrient {
  CALIB_N = 0, // Nitrogen (465 nm Blue)
  CALIB_P = 1, // Phosphorus (625 nm Red / Molybdenum Blue)
  CALIB_K = 2  // Potassium (625 nm Red)
};

AppScreen currentScreen = PAGE_DASHBOARD; // Default to Dashboard view [1/8]
ModelMode currentModel  = MODEL_TINYML;
CalibNutrient activeCalibNutrient = CALIB_N;
bool screenChanged = true;

// Calibration & Spectrum Data Objects
CalibrationState calibState;
StandardCurve curveN;
StandardCurve curveP;
StandardCurve curveK;
SpectrumScanResult currentSpectrum;
LiquidScanResult currentLiquidResult = {
  1.3330f, 0.9982f, 0.0f, 100.0f,
  {0.002f, 0.001f, 0.003f, 0.001f, 0.002f},
  525, 0.003f, "CLEAR", false, 0
};

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

int clockHour  = 12;
int clockMin   = 40;
int clockSec   = 0;
int clockYear  = 2026;
int clockMonth = 9;
int clockDay   = 15;
char dateBuf[16] = "15/09/2026";

void initSystemDateTime() {
  // Parse __TIME__ ("HH:MM:SS")
  const char* tStr = __TIME__;
  clockHour = (tStr[0] - '0') * 10 + (tStr[1] - '0');
  clockMin  = (tStr[3] - '0') * 10 + (tStr[4] - '0');
  clockSec  = (tStr[6] - '0') * 10 + (tStr[7] - '0');

  // Parse __DATE__ ("Mmm dd yyyy" e.g. "Sep 15 2026")
  const char* dStr = __DATE__;
  char sMonth[5] = {0};
  int d = 15, y = 2026;
  if (sscanf(dStr, "%3s %d %d", sMonth, &d, &y) >= 2) {
    clockDay = d;
    clockYear = y;
    const char* months[] = {"Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"};
    for (int m = 0; m < 12; m++) {
      if (strncmp(sMonth, months[m], 3) == 0) {
        clockMonth = m + 1;
        break;
      }
    }
  }
  sprintf(dateBuf, "%02d/%02d/%04d", clockDay, clockMonth, clockYear);
}

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

WiFiServerEngine wifiEngine;
float currentN = 45.2f, currentP = 22.8f, currentK = 128.5f, currentPH = 6.25f;
float currentA_red = 0.0f, currentA_green = 0.0f, currentA_blue = 0.0f;

// Safe Font Loader Management
bool fontLoaded30 = false;
bool fontLoaded20 = false;
static bool isFontCurrentlyLoaded = false;

void safeUnloadFont() {
  if (isFontCurrentlyLoaded) {
    tft.unloadFont();
    isFontCurrentlyLoaded = false;
  }
}

void safeLoadFont30() {
  safeUnloadFont();
  if (fontLoaded30) {
    tft.loadFont("THSarabunPSK30", SD);
    isFontCurrentlyLoaded = true;
  } else if (fontLoaded20) {
    tft.loadFont("THSarabunPSK20", SD);
    isFontCurrentlyLoaded = true;
  }
}

void safeLoadFont20() {
  safeUnloadFont();
  if (fontLoaded20) {
    tft.loadFont("THSarabunPSK20", SD);
    isFontCurrentlyLoaded = true;
  } else if (fontLoaded30) {
    tft.loadFont("THSarabunPSK30", SD);
    isFontCurrentlyLoaded = true;
  }
}

// Function Prototypes
void updateLedOutput();
void setAutoOpticsForScreen(AppScreen screen);
void drawMulticolorBadge(int x, int y, uint16_t bg, uint8_t size = 1);
void drawSplashScreen();
const char* getThaiDateStr();
void drawLedStatusTag();
void drawModelModeBadge();
void drawDashboardModelBadge();
void drawDashboardPage();
void drawNitrogenPage();
void drawPhosphorusPage();
void drawPotassiumPage();
void drawSoilPhPage();
void drawNpkStaticLayout();
void drawActiveCalibrationScreen();
void logSpectrumToSD();
void logCalibToSD(const char* nutName, const StandardCurve &sc);
void logLiquidToSD();

// ============================================================
// Format Thai Date: e.g. "16 ก.ย. 2569"
// ============================================================
const char* getThaiDateStr() {
  static char thaiDateStr[32];
  const char* thaiMonths[] = {
    "", "ม.ค.", "ก.พ.", "มี.ค.", "เม.ย.", "พ.ค.", "มิ.ย.",
    "ก.ค.", "ส.ค.", "ก.ย.", "ต.ค.", "พ.ย.", "ธ.ค."
  };
  const char* mStr = (clockMonth >= 1 && clockMonth <= 12) ? thaiMonths[clockMonth] : "ก.ย.";
  int beYear = (clockYear < 2500) ? (clockYear + 543) : clockYear;
  sprintf(thaiDateStr, "%d %s %d", clockDay, mStr, beYear);
  return thaiDateStr;
}

// ============================================================
// Futuristic Minimalist Splash Screen: SpecJC +AI Analyzer
// Developers: ผศ.ดร.ชีวะ ทัศนา, ผศ.ดร.จิรภัทร จันทมาลี
// Affiliation: ภายใต้หน่วย LEQs SciRBRU
// ============================================================
void drawSplashScreen() {
  tft.fillScreen(TFT_BLACK);

  // 1. Futuristic Corner Tech Brackets (Cyan 0x07FF)
  tft.drawFastHLine(8, 8, 24, 0x07FF);
  tft.drawFastVLine(8, 8, 24, 0x07FF);
  tft.drawFastHLine(288, 8, 24, 0x07FF);
  tft.drawFastVLine(311, 8, 24, 0x07FF);
  tft.drawFastHLine(8, 231, 24, 0x07FF);
  tft.drawFastVLine(8, 208, 24, 0x07FF);
  tft.drawFastHLine(288, 231, 24, 0x07FF);
  tft.drawFastVLine(311, 208, 24, 0x07FF);

  // 2. High-Tech Optical Prism & Spectral Dispersion Graphic (Center: x=135, y=14)
  int px = 135, py = 14;
  // Triangular Glass Prism with Dual Bevel
  tft.fillTriangle(px + 25, py + 2, px + 4, py + 38, px + 46, py + 38, 0x10E4);
  tft.drawTriangle(px + 25, py + 2, px + 4, py + 38, px + 46, py + 38, 0x07FF);
  tft.drawTriangle(px + 25, py + 4, px + 6, py + 36, px + 44, py + 36, TFT_WHITE);

  // Incident Coherent White Light Beam
  tft.drawFastHLine(px - 45, py + 24, 50, TFT_WHITE);
  tft.drawFastHLine(px - 45, py + 25, 50, 0xCE79);

  // Dispersed 5-Band Spectral Light Rays (Blue, Cyan, Green, Yellow, Red)
  uint16_t specCols[5] = {0x001F, 0x07FF, TFT_GREEN, TFT_YELLOW, TFT_RED};
  for (int i = 0; i < 5; i++) {
    tft.drawLine(px + 28, py + 18 + (i * 3), px + 85, py + 6 + (i * 9), specCols[i]);
    tft.drawLine(px + 28, py + 19 + (i * 3), px + 85, py + 7 + (i * 9), specCols[i]);
  }

  // 3. Brand Logo: SpecJC +AI Analyzer (Size 2 Bold Multicolor)
  drawMulticolorBadge(54, 64, TFT_BLACK, 2);

  // Double Gradient Divider Lines
  tft.drawFastHLine(25, 94, 270, TFT_MAGENTA);
  tft.drawFastHLine(25, 96, 270, 0x07FF);

  // 4. Developers & Affiliation Information
  if (fontLoaded) {
    safeLoadFont20();
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("ผศ.ดร.ชีวะ ทัศนา   ผศ.ดร.จิรภัทร จันทมาลี", 24, 106);

    tft.setTextColor(TFT_WHITE, TFT_BLACK);
    tft.drawString("ผู้พัฒนาระบบ SpecJC +AI", 90, 130);

    tft.setTextColor(0x07FF, TFT_BLACK);
    tft.drawString("ภายใต้หน่วย LEQs SciRBRU", 82, 152);
    safeUnloadFont();
  } else {
    tft.setTextSize(1);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("Asst. Prof. Dr. Chewa Thassana & Dr. Jirapat Janthamalee", 14, 110);
    tft.setTextColor(TFT_WHITE, TFT_BLACK);
    tft.drawString("Developers of SpecJC +AI Analyzer", 60, 130);
    tft.setTextColor(0x07FF, TFT_BLACK);
    tft.drawString("Under LEQs Research Unit, SciRBRU", 62, 150);
  }

  // 5. High-Tech Animated Loading Progress Bar
  tft.drawRoundRect(28, 180, 264, 14, 3, 0x2104);
  tft.drawRoundRect(27, 179, 266, 16, 4, TFT_DARKGREY);

  tft.setTextSize(1);
  tft.setTextColor(0x07FF, TFT_BLACK);
  tft.drawString("SYSTEM CORE INITIALIZING...", 30, 202);

  for (int w = 2; w <= 260; w += 8) {
    tft.fillRoundRect(30, 182, w, 10, 2, 0x07FF);
    delay(40); // Smooth animated boot effect
  }
  delay(400); // User appreciation pause
}

// ============================================================
// Setup Routine
// ============================================================
void setup() {
  Serial.begin(115200);

  // 0. Initialize Real Time Clock from compiler timestamp
  initSystemDateTime();

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

  // 3. Initialize LCD Display & Backlight IMMEDIATELY
  pinMode(LCD_BACKLIGHT, OUTPUT);
  digitalWrite(LCD_BACKLIGHT, HIGH);
  tft.begin();
  tft.setRotation(3);
  tft.fillScreen(TFT_BLACK);

  // 4. Initialize SD Card & Detect Fonts (non-blocking)
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

    // Initialize LIQUID_LOG.csv
    myFile = SD.open("LIQUID_LOG.csv", FILE_APPEND);
    if (myFile) {
      if (myFile.size() == 0) {
        myFile.println("Time,n_Index,Density_g_cm3,Brix_deg,Transmittance_pct,A_465nm,A_500nm,A_525nm,A_590nm,A_625nm,Peak_nm,Clarity");
      }
      myFile.close();
    }

    // Check for Thai fonts on SD card safely
    if (SD.exists("/THSarabunPSK30.vlw")) {
      fontLoaded30 = true;
      Serial.println("Thai font THSarabunPSK30 found!");
    }
    if (SD.exists("/THSarabunPSK20.vlw")) {
      fontLoaded20 = true;
      Serial.println("Thai font THSarabunPSK20 found!");
    }

    // Load saved blank & standard curves if available
    if (loadCalibrationFromSD()) {
      Serial.println("Loaded saved full calibration profile from SD card!");
    }
  } else {
    Serial.println("SD card initialization failed or not inserted!");
    hasSD = false;
  }
  fontLoaded = (fontLoaded30 || fontLoaded20);

  // 5. Draw Futuristic SpecJC +AI Analyzer Boot Splash Screen with credits
  drawSplashScreen();

  // 6. Initialize Baseline & Standard Curves
  initCalibration();

  // 7. Initialize Color Sensor
  if (tcs.begin()) {
    Serial.println("Found TCS34725 sensor");
    hasTCS = true;
  } else {
    Serial.println("No TCS34725 found ... check connections");
    hasTCS = false;
  }

  // Initial spectrum scan baseline
  currentSpectrum.scanComplete = true;
  currentSpectrum.highAbsWarning = false;
  currentSpectrum.peakWavelength = 525;
  currentSpectrum.peakAbsorbance = 0.45f;
  for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
    currentSpectrum.absorbance[i] = 0.20f + (0.08f * i);
  }

  // 8. Initialize Wi-Fi & Embedded REST API Server (Standalone/Non-blocking)
  wifiEngine.init();

  // 9. Immediately Render First Screen & Set Auto-Optics
  drawDashboardPage();
  setAutoOpticsForScreen(PAGE_DASHBOARD);
  screenChanged = false;

  // 8. Initialize Wi-Fi & Embedded REST API Server (Standalone/Non-blocking)
  wifiEngine.init();

  // 9. Immediately Render First Screen & Set Auto-Optics
  drawDashboardPage();
  setAutoOpticsForScreen(PAGE_DASHBOARD);
  screenChanged = false;

  lastMeasureTime = millis();
  lastSecondTime  = millis();
}

// ============================================================
// Render Bold Multicolor "SpecJC +AI Analyzer" Brand Badge
// Color Scheme: Spec (Cyan), JC (Red), +AI (Yellow), Analyzer (Green)
// ============================================================
void drawMulticolorBadge(int x, int y, uint16_t bg, uint8_t size) {
  tft.setTextSize(size);
  struct Seg {
    const char* str;
    uint16_t col;
  };
  const Seg segs[] = {
    {"Spec",     0x07FF},       // Vibrant Cyan
    {"JC",       TFT_RED},      // Vivid Red
    {" +AI ",    TFT_YELLOW},   // Warm Yellow
    {"Analyzer", TFT_GREEN}     // Bright Green
  };

  int curX = x;
  int charW = 6 * size;
  for (int i = 0; i < 4; i++) {
    tft.setTextColor(segs[i].col, bg);
    tft.drawString(segs[i].str, curX, y);
    tft.drawString(segs[i].str, curX + 1, y); // 1px horizontal offset for bold
    if (size >= 2) {
      tft.drawString(segs[i].str, curX, y + 1);
      tft.drawString(segs[i].str, curX + 1, y + 1);
    }
    curX += strlen(segs[i].str) * charW;
  }
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
void drawDashboardModelBadge() {
  tft.fillRect(8, 160, 144, 26, 0x0842);
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
}

void drawDashboardPage() {
  tft.fillScreen(TFT_BLACK);

  // 1. Top Header Banner Box
  tft.fillRect(0, 0, 320, 56, 0x0842);

  // Draw Embedded Optical Prism & Spectrum Logo
  drawSpectrometerLogo(10, 8);

  // Header Titles (Pure Thai font for Sarabun, ASCII for English)
  if (fontLoaded) {
    safeLoadFont30();
    tft.setTextColor(TFT_YELLOW, 0x0842);
    tft.drawString("เครื่องสเปกโทรโฟโตมิเตอร์", 64, 6);
    safeUnloadFont();

    // SpecJC +AI Analyzer (Size 2 Bold Multicolor Brand)
    drawMulticolorBadge(54, 32, 0x0842, 2);
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_YELLOW, 0x0842);
    tft.drawString("SPECTROMETER", 68, 8);

    drawMulticolorBadge(54, 32, 0x0842, 2);
  }

  // Page Indicator Badge
  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("[1/8]", 285, 10);

  // Double Divider Lines
  tft.drawFastHLine(0, 56, 320, TFT_MAGENTA);
  tft.drawFastHLine(0, 58, 320, 0x07FF);

  // 2. Card 1: Hardware & Processing Core (Left Box)
  tft.fillRoundRect(6, 64, 150, 134, 4, 0x0842);
  tft.drawRoundRect(6, 64, 150, 134, 4, 0x07FF);
  tft.fillRoundRect(7, 65, 148, 22, 3, 0x10E4);

  // Card 1 Header (Large TextSize 2 or Sarabun font)
  if (fontLoaded) {
    safeLoadFont20();
    tft.setTextColor(TFT_WHITE, 0x10E4);
    tft.drawString("ระบบประมวลผล", 32, 68);
    safeUnloadFont();
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
  drawDashboardModelBadge();

  // 3. Card 2: Sensors & Peripherals (Right Box)
  tft.fillRoundRect(164, 64, 150, 134, 4, 0x0842);
  tft.drawRoundRect(164, 64, 150, 134, 4, TFT_MAGENTA);
  tft.fillRoundRect(165, 65, 148, 22, 3, 0x2084);

  // Card 2 Header
  if (fontLoaded) {
    safeLoadFont20();
    tft.setTextColor(TFT_WHITE, 0x2084);
    tft.drawString("อุปกรณ์และเซนเซอร์", 175, 68);
    safeUnloadFont();
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
  tft.drawString(timeBuf, 191, 155);

  // Thai Date Display beneath Time (e.g. "16 ก.ย. 2569")
  if (fontLoaded) {
    safeLoadFont20();
    tft.setTextColor(TFT_YELLOW, 0x0842);
    tft.drawString(getThaiDateStr(), 182, 174);
    safeUnloadFont();
  } else {
    tft.setTextSize(1);
    tft.setTextColor(TFT_YELLOW, 0x0842);
    tft.drawString(getThaiDateStr(), 188, 177);
  }

  // 4. Footer Bar
  tft.drawFastHLine(0, 204, 320, TFT_DARKGREY);
  tft.drawFastHLine(0, 206, 320, 0x2104);

  tft.setTextSize(1);
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("[< / >] Pages  |  [UP] Model Mode  |  A/B/C: LEDs", 14, 216);
}



// ============================================================
// Page 1: Dedicated Nitrogen Assay (465/525 nm, 3-Tier)
// ============================================================
void drawNitrogenPage() {
  tft.fillScreen(TFT_BLACK);

  // Top Banner
  tft.fillRect(0, 0, 320, 48, 0x0842);
  drawSpectrometerLogo(8, 4);

  if (fontLoaded) {
    safeLoadFont30();
    tft.setTextColor(0x07FF, 0x0842);
    tft.drawString("วิเคราะห์ธาตุไนโตรเจน", 75, 8);
    safeUnloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(0x07FF, 0x0842);
    tft.drawString("NITROGEN ASSAY", 75, 12);
  }

  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("[2/8]", 285, 12);

  tft.drawFastHLine(0, 48, 320, 0x07FF);
  tft.drawFastHLine(0, 50, 320, TFT_MAGENTA);

  // Main Measurement Card
  tft.fillRoundRect(8, 56, 304, 140, 6, 0x0842);
  tft.drawRoundRect(8, 56, 304, 140, 6, 0x07FF);

  tft.setTextSize(1);
  tft.setTextColor(TFT_LIGHTGREY, 0x0842);
  tft.drawString("REAGENT: Indophenol Blue Complex", 18, 64);
  tft.drawString("OPTICAL BAND: 465nm (Blue) / 525nm (Green)", 18, 76);

  // Large Number Display
  char valStr[16];
  sprintf(valStr, "%6.2f", currentN);
  tft.setTextSize(4);
  tft.setTextColor(0x07FF, 0x0842);
  tft.drawString(valStr, 20, 96);

  tft.setTextSize(2);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("mg/kg", 170, 110);

  // Large Bold Pink N
  tft.setTextSize(4);
  tft.setTextColor(TFT_MAGENTA, 0x0842); // ชมพู Pink/Magenta
  tft.drawString("N", 248, 96);
  tft.drawString("N", 249, 96); // Bold offset

  // Tier Status & Diagnostic Bar
  tft.drawRect(18, 142, 280, 10, TFT_DARKGREY);
  int barW = (int)constrain((currentN / 100.0f) * 278.0f, 2.0f, 278.0f);
  tft.fillRect(19, 143, barW, 8, 0x07FF);

  if (fontLoaded) {
    safeLoadFont20();
    if (currentN < 20.0f) {
      tft.setTextColor(TFT_YELLOW, 0x0842);
      tft.drawString("สถานะ ไนโตรเจนต่ำ ควรเสริมปุ๋ยเร่งต้นใบ", 18, 158);
      tft.drawString("คำแนะนำ เพิ่มปุ๋ยไนโตรเจนเพื่อส่งเสริมการเจริญเติบโต", 18, 174);
    } else if (currentN <= 60.0f) {
      tft.setTextColor(TFT_GREEN, 0x0842);
      tft.drawString("สถานะ ไนโตรเจนระดับเหมาะสม", 18, 158);
      tft.drawString("คำแนะนำ ปริมาณธาตุอาหารสมบูรณ์ พืชเจริญเติบโตได้ดี", 18, 174);
    } else {
      tft.setTextColor(TFT_RED, 0x0842);
      tft.drawString("สถานะ ไนโตรเจนสูงเกินเกณฑ์", 18, 158);
      tft.drawString("คำแนะนำ ชะลอการใส่ปุ๋ยไนโตรเจนเพื่อป้องกันการบ้าใบ", 18, 174);
    }
    safeUnloadFont();
  } else {
    tft.setTextSize(1);
    if (currentN < 20.0f) {
      tft.setTextColor(TFT_YELLOW, 0x0842);
      tft.drawString("STATUS: LOW N (Tier 1: High Sensitivity 465nm)", 18, 160);
      tft.drawString("REC: Add Nitrogen fertilizer (Urea 46-0-0)", 18, 175);
    } else if (currentN <= 60.0f) {
      tft.setTextColor(TFT_GREEN, 0x0842);
      tft.drawString("STATUS: OPTIMAL N (Tier 2: Agronomic Range)", 18, 160);
      tft.drawString("REC: Optimal N level for vegetative growth", 18, 175);
    } else {
      tft.setTextColor(TFT_RED, 0x0842);
      tft.drawString("STATUS: HIGH N (Tier 3: Green 525nm)", 18, 160);
      tft.drawString("REC: Reduce N to prevent excessive vegetative shoot", 18, 175);
    }
  }

  // Footer Help
  tft.drawFastHLine(0, 204, 320, TFT_DARKGREY);
  tft.setTextSize(1);
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("[< / >] Prev/Next Mode  |  [DOWN] Recalculate Assay", 10, 214);
}

// ============================================================
// Page 2: Dedicated Phosphorus Assay (625 nm, Q1 Poly)
// ============================================================
void drawPhosphorusPage() {
  tft.fillScreen(TFT_BLACK);

  // Top Banner
  tft.fillRect(0, 0, 320, 48, 0x0842);
  drawSpectrometerLogo(8, 4);

  if (fontLoaded) {
    safeLoadFont30();
    tft.setTextColor(TFT_GREEN, 0x0842);
    tft.drawString("วิเคราะห์ธาตุฟอสฟอรัส", 75, 8);
    safeUnloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_GREEN, 0x0842);
    tft.drawString("PHOSPHORUS ASSAY", 75, 12);
  }

  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("[3/8]", 285, 12);

  tft.drawFastHLine(0, 48, 320, TFT_GREEN);
  tft.drawFastHLine(0, 50, 320, TFT_MAGENTA);

  // Main Measurement Card
  tft.fillRoundRect(8, 56, 304, 140, 6, 0x0842);
  tft.drawRoundRect(8, 56, 304, 140, 6, TFT_GREEN);

  tft.setTextSize(1);
  tft.setTextColor(TFT_LIGHTGREY, 0x0842);
  tft.drawString("REAGENT: Molybdenum Blue Complex (625nm Red)", 18, 64);
  tft.drawString("LINEAR RANGE: 1.0 - 6.0 mg/L | Guard: A > 0.500", 18, 76);

  // Large Number Display
  char valStr[16];
  sprintf(valStr, "%6.2f", currentP);
  tft.setTextSize(4);
  if (currentA_red > 0.500f) {
    tft.setTextColor(TFT_RED, 0x0842); // Red alert if saturated
  } else {
    tft.setTextColor(TFT_GREEN, 0x0842);
  }
  tft.drawString(valStr, 20, 96);

  tft.setTextSize(2);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("mg/kg", 170, 96);

  // Absorbance Telemetry Tag
  tft.setTextSize(1);
  char aRedBuf[18];
  sprintf(aRedBuf, "A625: %0.3f", currentA_red);
  if (currentA_red > 0.500f) {
    tft.setTextColor(TFT_RED, 0x0842);
    tft.drawString(aRedBuf, 170, 118);
    tft.drawString("[SATURATED]", 170, 128);
  } else {
    tft.setTextColor(0x07FF, 0x0842);
    tft.drawString(aRedBuf, 170, 118);
    tft.drawString("[LINEAR OK]", 170, 128);
  }

  // Large Bold Cyan P (0x07FF)
  tft.setTextSize(4);
  tft.setTextColor(0x07FF, 0x0842); // Bright Cyan
  tft.drawString("P", 252, 96);
  tft.drawString("P", 253, 96); // Bold offset

  // Progress / Range Bar (0 - 50 mg/kg)
  tft.drawRect(18, 142, 280, 10, TFT_DARKGREY);
  int barW = (int)constrain((currentP / 50.0f) * 278.0f, 2.0f, 278.0f);
  tft.fillRect(19, 143, barW, 8, (currentA_red > 0.500f) ? TFT_RED : TFT_GREEN);

  if (fontLoaded) {
    safeLoadFont20();
    if (currentA_red > 0.500f) {
      tft.setTextColor(TFT_RED, 0x0842);
      tft.drawString("สถานะ สัญญาณแสงอิ่มตัว (A > 0.500)!", 18, 158);
      tft.drawString("คำเตือน กรุณาเจือจางตัวอย่าง 1:5 ก่อนวัดซ้ำ", 18, 174);
    } else if (currentP < 15.0f) {
      tft.setTextColor(TFT_YELLOW, 0x0842);
      tft.drawString("สถานะ ฟอสฟอรัสต่ำกว่าเกณฑ์มาตรฐาน", 18, 158);
      tft.drawString("คำแนะนำ ใส่ปุ๋ยฟอสเฟตบำรุงรากและเสริมการสร้างตาดอก", 18, 174);
    } else if (currentP <= 35.0f) {
      tft.setTextColor(TFT_GREEN, 0x0842);
      tft.drawString("สถานะ ฟอสฟอรัสระดับเหมาะสม", 18, 158);
      tft.drawString("คำแนะนำ ธาตุอาหารพร้อมใช้ ช่วยการเจริญของระบบราก", 18, 174);
    } else {
      tft.setTextColor(0x07FF, 0x0842);
      tft.drawString("สถานะ ฟอสฟอรัสสะสมปริมาณสูง", 18, 158);
      tft.drawString("คำแนะนำ งดใส่ปุ๋ยฟอสฟอรัสเพื่อป้องกันการตรึงจุลธาตุ", 18, 174);
    }
    safeUnloadFont();
  } else {
    tft.setTextSize(1);
    if (currentA_red > 0.500f) {
      tft.setTextColor(TFT_RED, 0x0842);
      tft.drawString("STATUS: SATURATION GUARD! (A_red > 0.500)", 18, 160);
      tft.drawString("ALERT: Dilute sample 1:5 or 1:10 and re-test", 18, 175);
    } else if (currentP < 15.0f) {
      tft.setTextColor(TFT_YELLOW, 0x0842);
      tft.drawString("STATUS: LOW P (Bray II < 15 mg/kg)", 18, 160);
      tft.drawString("REC: Add phosphate fertilizer 18-46-0 for roots", 18, 175);
    } else if (currentP <= 35.0f) {
      tft.setTextColor(TFT_GREEN, 0x0842);
      tft.drawString("STATUS: SUFFICIENT P (15 - 35 mg/kg)", 18, 160);
      tft.drawString("REC: Optimal available P for root and flower development", 18, 175);
    } else {
      tft.setTextColor(0x07FF, 0x0842);
      tft.drawString("STATUS: HIGH ACCUMULATION (> 35 mg/kg)", 18, 160);
      tft.drawString("REC: Suspend P fertilizer to avoid Zn/Fe micronutrient tie-up", 18, 175);
    }
  }

  // Footer Help
  tft.drawFastHLine(0, 204, 320, TFT_DARKGREY);
  tft.setTextSize(1);
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("[< / >] Prev/Next Mode  |  [DOWN] Recalculate Assay", 10, 214);
}

// ============================================================
// Page 3: Dedicated Potassium Assay (Turbidimetry 625 nm)
// ============================================================
void drawPotassiumPage() {
  tft.fillScreen(TFT_BLACK);

  // Top Banner
  tft.fillRect(0, 0, 320, 48, 0x0842);
  drawSpectrometerLogo(8, 4);

  if (fontLoaded) {
    safeLoadFont30();
    tft.setTextColor(TFT_RED, 0x0842);
    tft.drawString("วิเคราะห์ธาตุโพแทสเซียม", 75, 8);
    safeUnloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_RED, 0x0842);
    tft.drawString("POTASSIUM ASSAY", 75, 12);
  }

  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("[4/8]", 285, 12);

  tft.drawFastHLine(0, 48, 320, TFT_RED);
  tft.drawFastHLine(0, 50, 320, TFT_MAGENTA);

  // Main Measurement Card
  tft.fillRoundRect(8, 56, 304, 140, 6, 0x0842);
  tft.drawRoundRect(8, 56, 304, 140, 6, TFT_RED);

  tft.setTextSize(1);
  tft.setTextColor(TFT_LIGHTGREY, 0x0842);
  tft.drawString("METHOD: Sodium Tetraphenylborate Turbidimetry", 18, 64);
  tft.drawString("OPTICS: 625nm Red Scattering / Baseline Comp.", 18, 76);

  // Large Number Display
  char valStr[16];
  sprintf(valStr, "%6.2f", currentK);
  tft.setTextSize(4);
  tft.setTextColor(TFT_RED, 0x0842);
  tft.drawString(valStr, 20, 96);

  tft.setTextSize(2);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("mg/kg", 170, 110);

  // Large Bold Red K
  tft.setTextSize(4);
  tft.setTextColor(TFT_RED, 0x0842); // แดง Red
  tft.drawString("K", 248, 96);
  tft.drawString("K", 249, 96); // Bold offset

  // Progress Bar (0 - 250 mg/kg)
  tft.drawRect(18, 142, 280, 10, TFT_DARKGREY);
  int barW = (int)constrain((currentK / 250.0f) * 278.0f, 2.0f, 278.0f);
  tft.fillRect(19, 143, barW, 8, TFT_RED);

  if (fontLoaded) {
    safeLoadFont20();
    if (currentK < 80.0f) {
      tft.setTextColor(TFT_YELLOW, 0x0842);
      tft.drawString("สถานะ โพแทสเซียมต่ำกว่าเกณฑ์", 18, 158);
      tft.drawString("คำแนะนำ เสริมปุ๋ยโพแทสเซียมเพื่อเพิ่มความแข็งแรง", 18, 174);
    } else if (currentK <= 160.0f) {
      tft.setTextColor(TFT_GREEN, 0x0842);
      tft.drawString("สถานะ โพแทสเซียมระดับเหมาะสม", 18, 158);
      tft.drawString("คำแนะนำ ช่วยพัฒนาคุณภาพผลผลิตและเพิ่มความหวาน", 18, 174);
    } else {
      tft.setTextColor(0x07FF, 0x0842);
      tft.drawString("สถานะ โพแทสเซียมสะสมปริมาณสูง", 18, 158);
      tft.drawString("คำแนะนำ ชะลอใส่ปุ๋ยโพแทสเซียม ป้องกันยับยั้งแคลเซียม", 18, 174);
    }
    safeUnloadFont();
  } else {
    tft.setTextSize(1);
    if (currentK < 80.0f) {
      tft.setTextColor(TFT_YELLOW, 0x0842);
      tft.drawString("STATUS: LOW POTASSIUM (< 80 mg/kg)", 18, 160);
      tft.drawString("REC: Add Potassium Chloride 0-0-60", 18, 175);
    } else if (currentK <= 160.0f) {
      tft.setTextColor(TFT_GREEN, 0x0842);
      tft.drawString("STATUS: OPTIMAL FOR FRUITING (80 - 160 mg/kg)", 18, 160);
      tft.drawString("REC: Adequate K for fruit filling and sweetness", 18, 175);
    } else {
      tft.setTextColor(0x07FF, 0x0842);
      tft.drawString("STATUS: HIGH CONCENTRATION (> 160 mg/kg)", 18, 160);
      tft.drawString("REC: Avoid excess K to prevent Ca/Mg inhibition", 18, 175);
    }
  }

  // Footer Help
  tft.drawFastHLine(0, 204, 320, TFT_DARKGREY);
  tft.setTextSize(1);
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("[< / >] Prev/Next Mode  |  [DOWN] Recalculate Assay", 10, 214);
}

// ============================================================
// Page 4: Dedicated Soil pH Assay (Ratiometric Green/Red)
// ============================================================
void drawSoilPhPage() {
  tft.fillScreen(TFT_BLACK);

  // Top Banner
  tft.fillRect(0, 0, 320, 48, 0x0842);
  drawSpectrometerLogo(8, 4);

  if (fontLoaded) {
    safeLoadFont30();
    tft.setTextColor(TFT_YELLOW, 0x0842);
    tft.drawString("วิเคราะห์ค่ากรด-ด่างดิน", 72, 8);
    safeUnloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_YELLOW, 0x0842);
    tft.drawString("SOIL pH ASSAY", 75, 12);
  }

  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, 0x0842);
  tft.drawString("[5/8]", 285, 12);

  tft.drawFastHLine(0, 48, 320, TFT_YELLOW);
  tft.drawFastHLine(0, 50, 320, TFT_MAGENTA);

  // Main Measurement Card
  tft.fillRoundRect(8, 56, 304, 140, 6, 0x0842);
  tft.drawRoundRect(8, 56, 304, 140, 6, TFT_YELLOW);

  tft.setTextSize(1);
  tft.setTextColor(TFT_LIGHTGREY, 0x0842);
  tft.drawString("INDICATOR: Universal / Bromothymol Blue Dye", 18, 64);
  tft.drawString("MODEL: Henderson-Hasselbalch Ratio (A525/A625)", 18, 76);

  // Large Number Display
  char valStr[16];
  sprintf(valStr, "%5.2f", currentPH);
  tft.setTextSize(4);

  SoilPhClass phClass = classify_soil_ph(currentPH);
  uint16_t phColor = (phClass == PH_OPTIMAL_DURIAN) ? TFT_GREEN :
                     ((phClass == PH_STRONGLY_ACIDIC) ? TFT_RED : TFT_YELLOW);

  tft.setTextColor(phColor, 0x0842);
  tft.drawString(valStr, 25, 96);

  // Enlarge & Bold Colorful "pH Level" Display
  tft.setTextSize(3);
  tft.setTextColor(0x07FF, 0x0842); // Vibrant Cyan
  tft.drawString("pH", 158, 100);
  tft.drawString("pH", 159, 100);   // Bold horizontal
  tft.drawString("pH", 158, 101);   // Bold vertical

  tft.setTextColor(TFT_YELLOW, 0x0842); // Bright Yellow
  tft.drawString("Level", 202, 100);
  tft.drawString("Level", 203, 100); // Bold horizontal
  tft.drawString("Level", 202, 101); // Bold vertical

  // pH Scale Visual Bar (3.5 - 8.5)
  tft.drawRect(18, 142, 280, 10, TFT_DARKGREY);
  float normPh = (currentPH - 3.5f) / (8.5f - 3.5f);
  int barW = (int)constrain(normPh * 278.0f, 2.0f, 278.0f);
  tft.fillRect(19, 143, barW, 8, phColor);

  if (fontLoaded) {
    safeLoadFont20();
    if (phClass == PH_STRONGLY_ACIDIC) {
      tft.setTextColor(TFT_RED, 0x0842);
      tft.drawString("การวินิจฉัย ดินเป็นกรดรุนแรง (pH < 5.0)", 18, 158);
      tft.drawString("คำแนะนำ ปรับสภาพดินด้วยปูนโดโลไมต์หรือปูนขาว", 18, 174);
    } else if (phClass == PH_MODERATELY_ACIDIC) {
      tft.setTextColor(TFT_YELLOW, 0x0842);
      tft.drawString("การวินิจฉัย ดินเป็นกรดปานกลาง (pH 5.0 - 5.5)", 18, 158);
      tft.drawString("คำแนะนำ เสริมสารปรับสภาพดินเพื่อยกระดับ pH", 18, 174);
    } else if (phClass == PH_OPTIMAL_DURIAN) {
      tft.setTextColor(TFT_GREEN, 0x0842);
      tft.drawString("การวินิจฉัย ดินเหมาะสมสมบูรณ์แบบสำหรับทุเรียน", 18, 158);
      tft.drawString("คำแนะนำ รักษาระดับดิน พืชดูดซึมธาตุอาหารได้สูงสุด", 18, 174);
    } else {
      tft.setTextColor(0x07FF, 0x0842);
      tft.drawString("การวินิจฉัย ดินมีสภาพเป็นด่าง (pH > 6.5)", 18, 158);
      tft.drawString("คำแนะนำ เติมยิปซัมเกษตรหรืออินทรียวัตถุเพื่อปรับลด pH", 18, 174);
    }
    safeUnloadFont();
  } else {
    tft.setTextSize(1);
    tft.setTextColor(phColor, 0x0842);
    char classBuf[64];
    sprintf(classBuf, "DIAGNOSIS: %s", get_soil_ph_desc(phClass));
    tft.drawString(classBuf, 18, 160);

    if (phClass == PH_STRONGLY_ACIDIC) {
      tft.drawString("REC: Strongly acidic. Apply dolomite 100-200 kg/rai", 18, 175);
    } else if (phClass == PH_MODERATELY_ACIDIC) {
      tft.drawString("REC: Moderately acidic. Apply dolomite 50 kg/rai", 18, 175);
    } else if (phClass == PH_OPTIMAL_DURIAN) {
      tft.drawString("REC: Optimal pH range. N-P-K nutrient uptake maximized", 18, 175);
    } else {
      tft.drawString("REC: Alkaline soil. Add agricultural gypsum or compost", 18, 175);
    }
  }

  // Footer Help
  tft.drawFastHLine(0, 204, 320, TFT_DARKGREY);
  tft.setTextSize(1);
  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString("[< / >] Prev/Next Mode  |  [DOWN] Calibrate Buffer", 10, 214);
}

// ============================================================
// Page 5: Soil N-P-K & pH Summary Overview
// ============================================================
void drawNpkStaticLayout() {
  tft.fillScreen(TFT_BLACK);

  // Title 1: ปริมาณธาตุอาหารหลักในดิน (Yellow)
  if (fontLoaded) {
    safeLoadFont30();
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("สรุปธาตุอาหารหลักในดิน", 35, 8);
    safeUnloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("Soil NPK & pH Meter", 35, 10);
  }

  // Title 2: SpecJC +AI Analyzer 2026 (White)
  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("SpecJC +AI Analyzer 2026", 15, 36);

  // Page Indicator Badge
  tft.setTextSize(1);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("[6/8]", 285, 10);

  // Upper Double Separator Line (Magenta + Cyan)
  tft.drawFastHLine(5, 52, 310, TFT_MAGENTA);
  tft.drawFastHLine(5, 54, 310, 0x07FF);

  // Row 1: ไนโตรเจน N
  if (fontLoaded) {
    safeLoadFont20();
    tft.setTextColor(0x07FF, TFT_BLACK);
    tft.drawString("ไนโตรเจน  N :", 8, 62);
    safeUnloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(0x07FF, TFT_BLACK);
    tft.drawString("Nitrogen  N :", 8, 62);
  }
  tft.setTextSize(2);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("mg/kg", 245, 62);

  // Row 2: ฟอสฟอรัส P
  if (fontLoaded) {
    safeLoadFont20();
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString("ฟอสฟอรัส  P :", 8, 96);
    safeUnloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_GREEN, TFT_BLACK);
    tft.drawString("Phosphor  P :", 8, 96);
  }
  tft.setTextSize(2);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("mg/kg", 245, 96);

  // Row 3: โพแทสเซียม K
  if (fontLoaded) {
    safeLoadFont20();
    tft.setTextColor(TFT_RED, TFT_BLACK);
    tft.drawString("โพแทสเซียม K :", 8, 130);
    safeUnloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_RED, TFT_BLACK);
    tft.drawString("Potassium K :", 8, 130);
  }
  tft.setTextSize(2);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("mg/kg", 245, 130);

  // Row 4: ความเป็นกรด-ด่างดิน Soil pH
  if (fontLoaded) {
    safeLoadFont20();
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("กรด-ด่างดิน   :", 8, 164);
    safeUnloadFont();
  } else {
    tft.setTextSize(2);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("Soil pH     :", 8, 164);
  }
  tft.setTextSize(2);
  tft.setTextColor(TFT_WHITE, TFT_BLACK);
  tft.drawString("pH", 245, 164);

  // Lower Double Separator Line (LightGrey + Magenta)
  tft.drawFastHLine(5, 192, 310, TFT_LIGHTGREY);
  tft.drawFastHLine(5, 194, 310, TFT_MAGENTA);

  // Footer Left: Live Time & Thai Date (Time above, Thai Date below)
  char initTimeBuf[12];
  sprintf(initTimeBuf, "%02d:%02d:%02d", clockHour, clockMin, clockSec);
  tft.setTextSize(1);
  tft.setTextColor(0x07FF, TFT_BLACK);
  tft.drawString(initTimeBuf, 10, 202);

  tft.setTextColor(TFT_YELLOW, TFT_BLACK);
  tft.drawString(getThaiDateStr(), 10, 218);

  // Footer Middle: ชีวะ ทัศนา | JC_AI_SciRBRU (Multicolor Bold)
  if (fontLoaded) {
    safeLoadFont20();
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("ชีวะ ทัศนา", 118, 200);
    safeUnloadFont();
  } else {
    tft.setTextSize(1);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("Chewa Thassana", 112, 202);
  }
  drawMulticolorBadge(105, 218, TFT_BLACK);

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
// Automatic Wavelength & Optics Controller (Auto-Optics)
// Automatically selects optimal narrowband LED for each assay
// ============================================================
void setAutoOpticsForScreen(AppScreen screen) {
  // If running Broadband ML or Polynomial Models (which rely on normalized chromaticity: rr, gg, bb = r,g,b / (r+g+b)):
  // All RGB channels must be illuminated simultaneously to provide a full visible white spectrum.
  if (currentModel == MODEL_POLY || currentModel == MODEL_TINYML) {
    if (screen == PAGE_DASHBOARD || screen == PAGE_SPECTRUM) {
      ledRedState   = false;
      ledGreenState = false;
      ledBlueState  = false;
    } else {
      ledRedState   = true;
      ledGreenState = true;
      ledBlueState  = true;
    }
    updateLedOutput();
    return;
  }

  // Dedicated Narrowband Optic Illumination for Analytical Standard Curve (MODEL_STDCURV):
  switch (screen) {
    case PAGE_DASHBOARD:
      // Standby / Off to preserve battery and reduce thermal drift
      ledRedState   = false;
      ledGreenState = false;
      ledBlueState  = false;
      break;

    case PAGE_NITROGEN:
      // Nitrogen Multi-Tier Assay:
      // - Tier 1 & 2 (0-10 mg/L): 465 nm Blue LED (High Sensitivity)
      // - Tier 3 (10-100 mg/L): 525 nm Green LED (Dynamic Range Extension, prevents optical saturation)
      // Both Blue and Green LEDs are activated to allow seamless multi-tier autorun.
      ledRedState   = false;
      ledGreenState = true;
      ledBlueState  = true;
      break;

    case PAGE_PHOSPHORUS:
      // Phosphorus Assay: 625 nm Red LED (Molybdenum Blue Complex secondary absorption band)
      // (Primary peak at 880 nm, secondary at 710 nm; in visible range 625 nm provides highest dA/dC = 0.0753 AU/(mg/L))
      ledRedState   = true;
      ledGreenState = false;
      ledBlueState  = false;
      break;

    case PAGE_POTASSIUM:
      // Potassium Assay: 625 nm Red LED (Sodium Tetraphenylborate turbidimetry / humic acid color bypass)
      ledRedState   = true;
      ledGreenState = false;
      ledBlueState  = false;
      break;

    case PAGE_SOIL_PH:
      // Soil pH: Ratiometric Dual-Band (Green 525nm + Red 625nm, Henderson-Hasselbalch log10(A_g/A_r))
      ledRedState   = true;
      ledGreenState = true;
      ledBlueState  = false;
      break;

    case PAGE_NPK_METER:
      // Full Soil NPK Meter Overview: Balanced RGB illumination
      ledRedState   = true;
      ledGreenState = true;
      ledBlueState  = true;
      break;

    case PAGE_SPECTRUM:
      // Spectrum Sweep: Off until user presses [DOWN] for automated multi-band sweep
      ledRedState   = false;
      ledGreenState = false;
      ledBlueState  = false;
      break;

    case PAGE_CALIBRATE:
      // Calibration Wizard: Auto-select active calibration nutrient channel
      if (activeCalibNutrient == CALIB_N) {
        ledRedState   = false;
        ledGreenState = true;
        ledBlueState  = true;
      } else {
        ledRedState   = true;
        ledGreenState = false;
        ledBlueState  = false;
      }
      break;
  }
  updateLedOutput();
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
// ============================================================
// Log Liquid Optics Metrology to SD Card
// ============================================================
void logLiquidToSD() {
  if (!hasSD) return;
  myFile = SD.open("LIQUID_LOG.csv", FILE_APPEND);
  if (myFile) {
    char timeStr[12];
    sprintf(timeStr, "%02d:%02d:%02d", clockHour, clockMin, clockSec);

    myFile.print(timeStr); myFile.print(",");
    myFile.print(currentLiquidResult.refractiveIndex_n, 4); myFile.print(",");
    myFile.print(currentLiquidResult.density_g_cm3, 4); myFile.print(",");
    myFile.print(currentLiquidResult.brix_deg, 2); myFile.print(",");
    myFile.print(currentLiquidResult.transmittance_pct, 1); myFile.print(",");
    for (int i = 0; i < NUM_SPECTRAL_BANDS; i++) {
      myFile.print(currentLiquidResult.absorbance[i], 3);
      myFile.print(",");
    }
    myFile.print(currentLiquidResult.peakWavelength); myFile.print(",");
    myFile.println(currentLiquidResult.clarity);
    myFile.close();
  }
}

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
                    ((activeCalibNutrient == CALIB_P) ? 4 : 4); // Both P (Molybdenum Blue) and K absorb at Red (band 4: 625nm), N absorbs at Blue (band 0: 465nm)

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

  // 1.3 Analytical Model Toggle (Joystick Up in Dashboard or NPK Screen)
  if (btnJoyUp == LOW && lastBtnJoyUp == HIGH) {
    currentModel = (ModelMode)((currentModel + 1) % 3);
    setAutoOpticsForScreen(currentScreen);
    if (currentScreen == PAGE_NPK_METER) {
      drawModelModeBadge();
    } else if (currentScreen == PAGE_DASHBOARD) {
      drawDashboardModelBadge();
    }
    delay(150);
  }

  // 1.4 Top Buttons A, B, C Handling (Context Sensitive)
  if (btnA == LOW && lastBtnA == HIGH) {
    if (currentScreen == PAGE_CALIBRATE) {
      activeCalibNutrient = CALIB_K; // Select Potassium (625nm)
      setAutoOpticsForScreen(PAGE_CALIBRATE);
      drawActiveCalibrationScreen();
    } else {
      ledRedState = !ledRedState;
      updateLedOutput();
    }
    delay(150);
  }
  if (btnB == LOW && lastBtnB == HIGH) {
    if (currentScreen == PAGE_CALIBRATE) {
      activeCalibNutrient = CALIB_P; // Select Phosphorus (625nm)
      setAutoOpticsForScreen(PAGE_CALIBRATE);
      drawActiveCalibrationScreen();
    } else {
      ledGreenState = !ledGreenState;
      updateLedOutput();
    }
    delay(150);
  }
  if (btnC == LOW && lastBtnC == HIGH) {
    if (currentScreen == PAGE_CALIBRATE) {
      activeCalibNutrient = CALIB_N; // Select Nitrogen (465nm)
      setAutoOpticsForScreen(PAGE_CALIBRATE);
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
      tft.drawString("MEASURING WATER BLANK...", 16, 180);
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

  // 2. Handle Screen Redraw & Optical Wavelength Switching on Page Transition
  if (screenChanged) {
    screenChanged = false;
    setAutoOpticsForScreen(currentScreen);
    switch (currentScreen) {
      case PAGE_DASHBOARD:
        drawDashboardPage();
        break;
      case PAGE_NITROGEN:
        drawNitrogenPage();
        break;
      case PAGE_PHOSPHORUS:
        drawPhosphorusPage();
        break;
      case PAGE_POTASSIUM:
        drawPotassiumPage();
        break;
      case PAGE_SOIL_PH:
        drawSoilPhPage();
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
    if (clockHour >= 24) {
      clockHour = 0;
      clockDay++;
      sprintf(dateBuf, "%02d/%02d/%04d", clockDay, clockMonth, clockYear);
    }

    if (currentScreen == PAGE_DASHBOARD) {
      char timeBuf[16];
      sprintf(timeBuf, "%02d:%02d:%02d", clockHour, clockMin, clockSec);
      tft.setTextSize(2);
      tft.setTextColor(0x07FF, 0x0842); // Bright cyan on Card 2 dark background
      tft.drawString(timeBuf, 191, 155);

      if (fontLoaded) {
        safeLoadFont20();
        tft.setTextColor(TFT_YELLOW, 0x0842);
        tft.drawString(getThaiDateStr(), 182, 174);
        safeUnloadFont();
      } else {
        tft.setTextSize(1);
        tft.setTextColor(TFT_YELLOW, 0x0842);
        tft.drawString(getThaiDateStr(), 188, 177);
      }
    } else if (currentScreen == PAGE_NPK_METER) {
      char timeBuf[12];
      sprintf(timeBuf, "%02d:%02d:%02d", clockHour, clockMin, clockSec);
      tft.setTextSize(1);
      tft.setTextColor(0x07FF, TFT_BLACK);
      tft.drawString(timeBuf, 10, 202);

      tft.setTextColor(TFT_YELLOW, TFT_BLACK);
      tft.drawString(getThaiDateStr(), 10, 218);
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

    // Universal Optical Corrections & Absorbances (Dark current & Blank normalization)
    float I_b_corr = max(1.0f, (float)b - calibState.darkCurrent[0]);
    float I_g_corr = max(1.0f, (float)g - calibState.darkCurrent[2]);
    float I_r_corr = max(1.0f, (float)r - calibState.darkCurrent[4]);

    float I_b_blank = max(1.0f, calibState.blankIntensity[0] - calibState.darkCurrent[0]);
    float I_g_blank = max(1.0f, calibState.blankIntensity[2] - calibState.darkCurrent[2]);
    float I_r_blank = max(1.0f, calibState.blankIntensity[4] - calibState.darkCurrent[4]);

    float A_blue  = -log10f(constrain(I_b_corr / I_b_blank, 0.0001f, 1.50f));
    float A_green = -log10f(constrain(I_g_corr / I_g_blank, 0.0001f, 1.50f));
    float A_red   = -log10f(constrain(I_r_corr / I_r_blank, 0.0001f, 1.50f));

    currentA_blue  = A_blue;
    currentA_green = A_green;
    currentA_red   = A_red;

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
      // 3. 2026 SOTA Multi-Wavelength Optical Standard Curve Calibration Engine
      // Nitrogen (Paper 2): Use in-situ curve if calibrated, otherwise auto 3-tier (0.1-100 mg/L)
      if (curveN.isFitted) {
        valN = calculateConcentration_SC(A_blue, curveN);
      } else {
        valN = predict_nitrogen_autorun(A_blue, A_green);
      }

      // Phosphorus (Paper 1): 625 nm Red Channel Molybdenum Blue complex secondary slope
      if (curveP.isFitted) {
        valP = calculateConcentration_SC(A_red, curveP);
      } else {
        valP = predict_phosphorus_autorun(A_red);
      }

      // Potassium: Red channel standard curve or polynomial
      if (curveK.isFitted) {
        valK = calculateConcentration_SC(A_red, curveK);
      } else {
        valK = calcK_Poly(rr);
      }
    }

    // Soil pH Optical Ratiometric Model (Henderson-Hasselbalch A525/A625)
    float valPH = predict_soil_ph_optical(A_red, A_green, A_blue);

    currentN  = valN;
    currentP  = valP;
    currentK  = valK;
    currentPH = valPH;

    // Update Screen Display Depending on Current Active Page
    char valBuf[16];
    if (currentScreen == PAGE_NPK_METER) {
      tft.setTextSize(2);

      sprintf(valBuf, "%6.2f", valN);
      tft.setTextColor(0x07FF, TFT_BLACK);
      tft.drawString(valBuf, 150, 62);

      sprintf(valBuf, "%6.2f", valP);
      tft.setTextColor((currentA_red > 0.500f) ? TFT_RED : TFT_GREEN, TFT_BLACK);
      tft.drawString(valBuf, 150, 96);

      sprintf(valBuf, "%6.2f", valK);
      tft.setTextColor(TFT_RED, TFT_BLACK);
      tft.drawString(valBuf, 150, 130);

      sprintf(valBuf, "%6.2f", valPH);
      tft.setTextColor(TFT_YELLOW, TFT_BLACK);
      tft.drawString(valBuf, 150, 164);
    } else if (currentScreen == PAGE_NITROGEN) {
      sprintf(valBuf, "%6.2f", valN);
      tft.setTextSize(4);
      tft.setTextColor(0x07FF, 0x0842);
      tft.drawString(valBuf, 20, 96);
    } else if (currentScreen == PAGE_PHOSPHORUS) {
      sprintf(valBuf, "%6.2f", valP);
      tft.setTextSize(4);
      if (currentA_red > 0.500f) {
        tft.setTextColor(TFT_RED, 0x0842); // Red alert if saturated
      } else {
        tft.setTextColor(TFT_GREEN, 0x0842);
      }
      tft.drawString(valBuf, 20, 96);

      // Realtime A625 telemetry badge update
      tft.setTextSize(1);
      char aRedLive[18];
      sprintf(aRedLive, "A625: %0.3f", currentA_red);
      if (currentA_red > 0.500f) {
        tft.setTextColor(TFT_RED, 0x0842);
        tft.drawString(aRedLive, 170, 118);
        tft.drawString("[SATURATED]", 170, 128);
      } else {
        tft.setTextColor(0x07FF, 0x0842);
        tft.drawString(aRedLive, 170, 118);
        tft.drawString("[LINEAR OK]", 170, 128);
      }
    } else if (currentScreen == PAGE_POTASSIUM) {
      sprintf(valBuf, "%6.2f", valK);
      tft.setTextSize(4);
      tft.setTextColor(TFT_RED, 0x0842);
      tft.drawString(valBuf, 20, 96);
    } else if (currentScreen == PAGE_SOIL_PH) {
      sprintf(valBuf, "%5.2f", valPH);
      tft.setTextSize(4);
      SoilPhClass phCls = classify_soil_ph(valPH);
      uint16_t phCol = (phCls == PH_OPTIMAL_DURIAN) ? TFT_GREEN :
                       ((phCls == PH_STRONGLY_ACIDIC) ? TFT_RED : TFT_YELLOW);
      tft.setTextColor(phCol, 0x0842);
      tft.drawString(valBuf, 25, 96);
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

    // Save NPK & Soil pH data to SD Card
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
        myFile.print(valPH, 2); myFile.print(",");
        const char* mStr = (currentModel == MODEL_TINYML) ? "TinyML" :
                           ((currentModel == MODEL_POLY) ? "Poly" : "StdCurve");
        myFile.println(mStr);
        myFile.close();
      }
    }
  }

  // 5. Handle Wi-Fi REST API Clients & Remote Commands
  SpectrometerTelemetry telem;
  telem.n = currentN;
  telem.p = currentP;
  telem.k = currentK;
  telem.soil_ph = currentPH;
  telem.ref_n = currentLiquidResult.refractiveIndex_n;
  telem.density = currentLiquidResult.density_g_cm3;
  telem.brix = currentLiquidResult.brix_deg;
  telem.transmittance = currentLiquidResult.transmittance_pct;
  strncpy(telem.clarity, currentLiquidResult.clarity, sizeof(telem.clarity));
  for (int i = 0; i < 5; i++) telem.absorbance[i] = currentSpectrum.absorbance[i];
  telem.currentPage = (int)currentScreen + 1;
  telem.isSoil = true;

  bool triggerScanSoil = false;
  bool triggerScanLiquid = false;
  bool triggerCalib = false;
  wifiEngine.handleClient(telem, triggerScanSoil, triggerScanLiquid, triggerCalib);

  if (triggerScanSoil) {
    executeAutoWavelengthScan(strip, tcs, calibState, currentSpectrum, hasTCS);
    for (int i = 0; i < 5; i++) telem.absorbance[i] = currentSpectrum.absorbance[i];
    wifiEngine.logMeasurement(telem);
  } else if (triggerScanLiquid) {
    analyzeLiquidOptics(strip, tcs, calibState, currentLiquidResult, hasTCS);
    telem.ref_n = currentLiquidResult.refractiveIndex_n;
    telem.density = currentLiquidResult.density_g_cm3;
    telem.brix = currentLiquidResult.brix_deg;
    telem.transmittance = currentLiquidResult.transmittance_pct;
    strncpy(telem.clarity, currentLiquidResult.clarity, sizeof(telem.clarity));
    telem.isSoil = false;
    wifiEngine.logMeasurement(telem);
    logLiquidToSD();
  } else if (triggerCalib) {
    captureBlankReference(strip, tcs, calibState, hasTCS);
    saveCalibrationToSD();
  }
}
