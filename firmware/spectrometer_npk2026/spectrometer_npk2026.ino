#include <Wire.h>
#include <SPI.h>
#include <Seeed_FS.h>
#include "SD/Seeed_SD.h"
#include <seeed_line_chart.h>
#include "Adafruit_TCS34725.h"
#include <TFT_eSPI.h>
#include <Adafruit_NeoPixel.h>
#include "TinyML_Model.h"

// ============================================================
// Pin Definitions
// ============================================================
// Grove RGB LED (WS2812B / NeoPixel) on Left Grove Port (D0)
#define NEOPIXEL_PIN   D0
#define NUM_PIXELS     16 // Supports 1 to 16 pixels (Stick/Ring/Single)
Adafruit_NeoPixel strip(NUM_PIXELS, NEOPIXEL_PIN, NEO_GRB + NEO_KHZ800);

// Discrete LED fallback pins
#define PIN_LED_RED    D2
#define PIN_LED_GREEN  D1
#define PIN_LED_BLUE   D0

// Wio Terminal Top Buttons and 5-Way Switch (Active LOW)
#define BTN_A          WIO_KEY_A     // ขวาสุด -> LED แดง (Red)
#define BTN_B          WIO_KEY_B     // กลาง   -> LED เขียว (Green)
#define BTN_C          WIO_KEY_C     // ซ้ายสุด -> LED น้ำเงิน (Blue)
#define BTN_WHITE      WIO_5S_PRESS  // จอยสติ๊กกดลงตรงกลาง -> เปิด/ปิด แสงขาว (White)
#define BTN_MODEL_TOG  WIO_5S_UP     // จอยสติ๊กโยกขึ้น -> สลับโหมด AI (TinyML / Poly)

// ============================================================
// Objects & State Variables
// ============================================================
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
bool lastBtnWhite    = HIGH;
bool lastBtnModelTog = HIGH;

uint32_t sampleCount = 32;
unsigned long lastMeasureTime = 0;
unsigned long lastSecondTime  = 0;

// Clock display simulation (starts at 12:46:00)
int clockHour = 12;
int clockMin  = 46;
int clockSec  = 0;

// Color Sensor
Adafruit_TCS34725 tcs = Adafruit_TCS34725(TCS34725_INTEGRATIONTIME_600MS, TCS34725_GAIN_1X);

// ============================================================
// Classical Polynomial Calibration Models (ผศ.ดร.ชีวะ ทัศนา)
// ============================================================
#define N_A0  -185.42f
#define N_A1    8.234f
#define N_A2   -0.0412f
#define N_A3    0.000091f

#define P_B0  -224.18f
#define P_B1   12.56f
#define P_B2   -0.0823f

#define K_C0  -18.92f
#define K_C1    1.842f
#define K_C2    0.0156f

inline float calcN_Poly(float bb) {
  float n = N_A0 + N_A1*bb + N_A2*bb*bb + N_A3*bb*bb*bb;
  if (n < 0.0f) n = 0.0f;
  if (n > 500.0f) n = 500.0f;
  return n;
}

inline float calcP_Poly(float gg) {
  float p = P_B0 + P_B1*gg + P_B2*gg*gg;
  if (p < 0.0f) p = 0.0f;
  if (p > 500.0f) p = 500.0f;
  return p;
}

inline float calcK_Poly(float rr) {
  float k = K_C0 + K_C1*rr + K_C2*rr*rr;
  if (k < 0.0f) k = 0.0f;
  if (k > 500.0f) k = 500.0f;
  return k;
}

// Forward declarations
void drawStaticLayout();
void drawLedStatusTag();
void drawModelModeBadge();
void updateLedOutput();

// ============================================================
// Setup
// ============================================================
void setup() {
  Serial.begin(115200);
  Wire.begin();

  // 1. Initialize LED Pins
  pinMode(PIN_LED_RED, OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_BLUE, OUTPUT);
  digitalWrite(PIN_LED_RED, LOW);
  digitalWrite(PIN_LED_GREEN, LOW);
  digitalWrite(PIN_LED_BLUE, LOW);

  // 1.1 Initialize Grove NeoPixel (WS2812B) on D0
  strip.begin();
  strip.setBrightness(255);
  strip.clear();
  strip.show();

  // 2. Initialize Top Buttons and Joystick with Pull-up
  pinMode(BTN_A, INPUT_PULLUP);
  pinMode(BTN_B, INPUT_PULLUP);
  pinMode(BTN_C, INPUT_PULLUP);
  pinMode(BTN_WHITE, INPUT_PULLUP);
  pinMode(BTN_MODEL_TOG, INPUT_PULLUP);
  delay(50);
  lastBtnA        = digitalRead(BTN_A);
  lastBtnB        = digitalRead(BTN_B);
  lastBtnC        = digitalRead(BTN_C);
  lastBtnWhite    = digitalRead(BTN_WHITE);
  lastBtnModelTog = digitalRead(BTN_MODEL_TOG);

  // 3. Initialize LCD Display
  tft.begin();
  tft.setRotation(3);
  tft.fillScreen(TFT_BLACK);

  // 4. Initialize SD Card (non-blocking)
  if (SD.begin(SDCARD_SS_PIN, SDCARD_SPI)) {
    Serial.println("SD card initialization successful!");
    hasSD = true;
    myFile = SD.open("NPK.txt", FILE_APPEND);
    if (myFile) {
      myFile.println("Time,b,g,r,c,N,P,K,Model");
      myFile.close();
    }
  } else {
    Serial.println("SD card initialization failed or not inserted!");
    hasSD = false;
  }

  // 5. Initialize Color Sensor
  if (tcs.begin()) {
    Serial.println("Found TCS34725 sensor");
    hasTCS = true;
  } else {
    Serial.println("No TCS34725 found ... check connections");
    hasTCS = false;
  }

  // 6. Try loading Thai font from SD Card if available
  if (hasSD) {
    if (SD.exists("/THSarabunPSK30.vlw")) {
      fontLoaded = true;
      Serial.println("Thai font THSarabunPSK30 found!");
    }
  }

  // 7. Draw Static Layout & Badges
  drawStaticLayout();
  updateLedOutput();
}

// ============================================================
// Draw Static Screen Layout (Matching Reference Photo)
// ============================================================
void drawStaticLayout() {
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
    tft.drawString("Primary Soil Nutrients", 30, 10);
  }

  // Title 2: NPK Level Meter 1.02 (Cyan)
  tft.setTextSize(2);
  tft.setTextColor(TFT_CYAN, TFT_BLACK);
  tft.drawString("NPK Level Meter 1.02", 20, 36);

  // Model Badge (TinyML AI vs Poly)
  drawModelModeBadge();

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
    tft.setTextColor(TFT_BLUE, TFT_BLACK);
    tft.drawString("Nitrogen", 8, 80);
  }
  tft.setTextSize(2);
  tft.setTextColor(TFT_BLUE, TFT_BLACK);
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

  // Initial LED Tag
  drawLedStatusTag();
}

// ============================================================
// Draw Model Mode Badge ([AI] / [PL])
// ============================================================
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

// ============================================================
// Draw Active LED Status on Footer (Immediate Feedback)
// ============================================================
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

// ============================================================
// Update LED Hardware Output (WS2812B NeoPixel + GPIO pins)
// ============================================================
void updateLedOutput() {
  // 1. Update Grove WS2812B NeoPixel on D0
  uint8_t r = ledRedState   ? 255 : 0;
  uint8_t g = ledGreenState ? 255 : 0;
  uint8_t b = ledBlueState  ? 255 : 0;

  for (int i = 0; i < NUM_PIXELS; i++) {
    strip.setPixelColor(i, strip.Color(r, g, b));
  }
  strip.show();

  // 2. Also toggle discrete digital pins D2, D1 just in case
  digitalWrite(PIN_LED_RED, ledRedState ? HIGH : LOW);
  digitalWrite(PIN_LED_GREEN, ledGreenState ? HIGH : LOW);

  // 3. Immediately redraw LED status on LCD screen
  drawLedStatusTag();
}

// ============================================================
// Main Loop
// ============================================================
void loop() {
  // 1. Handle Buttons A, B, C, White LED, and AI Mode Switch
  bool curBtnA        = digitalRead(BTN_A);
  bool curBtnB        = digitalRead(BTN_B);
  bool curBtnC        = digitalRead(BTN_C);
  bool curBtnWhite    = digitalRead(BTN_WHITE);
  bool curBtnModelTog = digitalRead(BTN_MODEL_TOG);

  // Button A -> Toggle Red (D2 / NeoPixel Red)
  if (lastBtnA == HIGH && curBtnA == LOW) {
    ledRedState = !ledRedState;
    updateLedOutput();
    Serial.print("Button A Pressed -> Red LED: ");
    Serial.println(ledRedState ? "ON" : "OFF");
    delay(40); // debounce
  }

  // Button B -> Toggle Green (D1 / NeoPixel Green)
  if (lastBtnB == HIGH && curBtnB == LOW) {
    ledGreenState = !ledGreenState;
    updateLedOutput();
    Serial.print("Button B Pressed -> Green LED: ");
    Serial.println(ledGreenState ? "ON" : "OFF");
    delay(40);
  }

  // Button C -> Toggle Blue (D0 / NeoPixel Blue)
  if (lastBtnC == HIGH && curBtnC == LOW) {
    ledBlueState = !ledBlueState;
    updateLedOutput();
    Serial.print("Button C Pressed -> Blue LED: ");
    Serial.println(ledBlueState ? "ON" : "OFF");
    delay(40);
  }

  // 5-Way Joystick Center Press -> Toggle White (All ON / All OFF)
  if (lastBtnWhite == HIGH && curBtnWhite == LOW) {
    if (ledRedState && ledGreenState && ledBlueState) {
      ledRedState = false;
      ledGreenState = false;
      ledBlueState = false;
    } else {
      ledRedState = true;
      ledGreenState = true;
      ledBlueState = true;
    }
    updateLedOutput();
    Serial.print("Joystick Center Pressed -> White LED: ");
    Serial.println(ledRedState ? "ON" : "OFF");
    delay(40);
  }

  // 5-Way Joystick UP -> Toggle Model Mode (TinyML AI / Polynomial)
  if (lastBtnModelTog == HIGH && curBtnModelTog == LOW) {
    useTinyML = !useTinyML;
    drawModelModeBadge();
    Serial.print("Model Mode Toggled -> ");
    Serial.println(useTinyML ? "[TinyML Deep Learning Mode]" : "[Classical Polynomial Mode]");
    delay(50);
  }

  lastBtnA        = curBtnA;
  lastBtnB        = curBtnB;
  lastBtnC        = curBtnC;
  lastBtnWhite    = curBtnWhite;
  lastBtnModelTog = curBtnModelTog;

  // 2. Update Clock Seconds every 1000ms
  unsigned long now = millis();
  if (now - lastSecondTime >= 1000) {
    lastSecondTime = now;
    clockSec++;
    if (clockSec >= 60) { clockSec = 0; clockMin++; }
    if (clockMin >= 60) { clockMin = 0; clockHour++; }
    if (clockHour >= 24) { clockHour = 0; }

    // Redraw Footer Date & Time
    tft.setTextSize(1);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    tft.drawString("11/05/2024", 10, 202);

    char timeBuf[12];
    sprintf(timeBuf, "%02d:%02d:%02d", clockHour, clockMin, clockSec);
    tft.drawString(timeBuf, 10, 218);
  }

  // 3. Periodic Sensor Measurement (every 800ms)
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
      // Feature Engineering for Edge AI:
      // 1: bp, 2: gp, 3: rp, 4: clear_ratio, 5: lux_norm, 6: abs_est
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
      // Classical polynomial equations
      valN = calcN_Poly(bb);
      valP = calcP_Poly(gg);
      valK = calcK_Poly(rr);
    }

    // Update Numerical Values on TFT
    tft.setTextSize(2);
    tft.setTextColor(TFT_WHITE, TFT_BLACK);

    // Nitrogen value
    char bufN[10];
    dtostrf(valN, 6, 2, bufN);
    tft.drawString(bufN, 155, 80);

    // Phosphorus value
    char bufP[10];
    dtostrf(valP, 6, 2, bufP);
    tft.drawString(bufP, 155, 120);

    // Potassium value
    char bufK[10];
    dtostrf(valK, 6, 2, bufK);
    tft.drawString(bufK, 155, 160);

    // Sample count (e.g. 32)
    tft.setTextSize(1);
    tft.setTextColor(TFT_YELLOW, TFT_BLACK);
    char countBuf[8];
    sprintf(countBuf, "%4lu", (unsigned long)sampleCount);
    tft.drawString(countBuf, 275, 202);

    // Serial monitor
    Serial.print("[NPK] #"); Serial.print(sampleCount);
    Serial.print(" | Mode: "); Serial.print(useTinyML ? "TinyML_AI" : "Poly");
    Serial.print(" | N="); Serial.print(valN, 2);
    Serial.print(" P="); Serial.print(valP, 2);
    Serial.print(" K="); Serial.print(valK, 2);
    Serial.print(" mg/kg | BGR: ");
    Serial.print(b); Serial.print(","); Serial.print(g); Serial.print(","); Serial.print(r);
    Serial.print(" | LED: R="); Serial.print(ledRedState);
    Serial.print(" G="); Serial.print(ledGreenState);
    Serial.print(" B="); Serial.println(ledBlueState);

    // Save to SD Card if present
    if (hasSD) {
      myFile = SD.open("NPK.txt", FILE_APPEND);
      if (myFile) {
        myFile.print(sampleCount); myFile.print(",");
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
