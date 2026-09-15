#ifndef WIFI_SERVER_ENGINE_H
#define WIFI_SERVER_ENGINE_H

#include <Arduino.h>
#include <Seeed_FS.h>
#include "SD/Seeed_SD.h"

// Set ENABLE_WIFI_SERVER to 1 only if RTL8720DN co-processor firmware is updated
#ifndef ENABLE_WIFI_SERVER
#define ENABLE_WIFI_SERVER 0
#endif

#if ENABLE_WIFI_SERVER
#include "rpcWiFi.h"
#include <WiFiClient.h>
#include <WiFiServer.h>
#else
#include <IPAddress.h>
#endif

// Default Wi-Fi credentials (Station mode)
#ifndef WIFI_SSID
#define WIFI_SSID "NPK_LAB_WIFI"
#define WIFI_PASS "AgriPhysics2026"
#endif

// Fallback SoftAP mode credentials
#define AP_SSID   "NPK-Spectrometer-AP"
#define AP_PASS   "12345678"

#define JSON_LOG_FILE "DATA_LOG.json"

struct SpectrometerTelemetry {
  float n;
  float p;
  float k;
  float soil_ph;
  float ref_n;
  float density;
  float brix;
  float transmittance;
  char clarity[16];
  float absorbance[5];
  int currentPage;
  bool isSoil;
};

class WiFiServerEngine {
private:
#if ENABLE_WIFI_SERVER
  WiFiServer server;
  bool isApMode;
  IPAddress ipAddr;
  unsigned long lastConnectAttempt;
#endif
  uint32_t recordCounter;

public:
#if ENABLE_WIFI_SERVER
  WiFiServerEngine() : server(80), isApMode(false), lastConnectAttempt(0), recordCounter(0) {}
#else
  WiFiServerEngine() : recordCounter(0) {}
#endif

  void init() {
#if ENABLE_WIFI_SERVER
    Serial.println(F("[WiFi] Initializing RTL8720DN Wi-Fi Subsystem..."));
    WiFi.mode(WIFI_STA);
    WiFi.disconnect();
    delay(100);

    // Attempt non-blocking connect
    Serial.print(F("[WiFi] Connecting to Station SSID: "));
    Serial.println(WIFI_SSID);
    WiFi.begin(WIFI_SSID, WIFI_PASS);

    // Wait briefly (up to 3 seconds) for quick connect
    unsigned long startMs = millis();
    while (WiFi.status() != WL_CONNECTED && millis() - startMs < 3000) {
      delay(200);
      Serial.print(F("."));
    }
    Serial.println();

    if (WiFi.status() == WL_CONNECTED) {
      isApMode = false;
      ipAddr = WiFi.localIP();
      Serial.print(F("[WiFi] Connected! IP Address: "));
      Serial.println(ipAddr);
    } else {
      // Fallback to SoftAP mode
      Serial.println(F("[WiFi] STA connection timeout. Starting SoftAP Mode..."));
      WiFi.mode(WIFI_AP);
      WiFi.softAP(AP_SSID, AP_PASS);
      delay(200);
      isApMode = true;
      ipAddr = WiFi.softAPIP();
      Serial.print(F("[WiFi] SoftAP Started! SSID: "));
      Serial.print(AP_SSID);
      Serial.print(F(" | IP: "));
      Serial.println(ipAddr);
    }

    server.begin();
    Serial.println(F("[WiFi] HTTP REST JSON Server listening on port 80"));
#else
    Serial.println(F("[WiFi] Standalone Mode (WiFi disabled for zero latency)"));
#endif
    initJsonLogFile();
  }

  bool isConnected() const {
#if ENABLE_WIFI_SERVER
    return isApMode || (WiFi.status() == WL_CONNECTED);
#else
    return false;
#endif
  }

  bool getIsApMode() const { 
#if ENABLE_WIFI_SERVER
    return isApMode; 
#else
    return false;
#endif
  }

  IPAddress getIP() const { 
#if ENABLE_WIFI_SERVER
    return ipAddr; 
#else
    return IPAddress(0, 0, 0, 0);
#endif
  }

  int getRSSI() const {
#if ENABLE_WIFI_SERVER
    return isApMode ? 0 : WiFi.RSSI();
#else
    return 0;
#endif
  }

  void initJsonLogFile() {
    if (SD.begin(SDCARD_SS_PIN, SDCARD_SPI)) {
      if (!SD.exists(JSON_LOG_FILE)) {
        File f = SD.open(JSON_LOG_FILE, FILE_WRITE);
        if (f) {
          f.println(F("["));
          f.println(F("]"));
          f.close();
          Serial.println(F("[JSON DB] Created initial DATA_LOG.json"));
        }
      }
    }
  }

  void logMeasurement(const SpectrometerTelemetry& t) {
    recordCounter++;
    Serial.print(F("[JSON DB] Logging measurement #"));
    Serial.println(recordCounter);

    File f = SD.open(JSON_LOG_FILE, FILE_WRITE);
    if (f) {
      if (f.size() > 3) {
        f.seek(f.size() - 2);
        f.println(F(","));
      } else {
        f.println(F("["));
      }

      f.print(F("  {\n    \"id\": \"REC-"));
      f.print(millis() / 1000);
      f.println(F("\","));
      
      f.print(F("    \"type\": \""));
      f.print(t.isSoil ? F("SOIL_NPK") : F("LIQUID_OPTICS"));
      f.println(F("\","));

      if (t.isSoil) {
        f.print(F("    \"n_mg_kg\": ")); f.print(t.n, 1); f.println(F(","));
        f.print(F("    \"p_mg_kg\": ")); f.print(t.p, 1); f.println(F(","));
        f.print(F("    \"k_mg_kg\": ")); f.print(t.k, 1); f.println(F(","));
      } else {
        f.print(F("    \"n_refractive\": ")); f.print(t.ref_n, 4); f.println(F(","));
        f.print(F("    \"density_g_cm3\": ")); f.print(t.density, 3); f.println(F(","));
        f.print(F("    \"brix_deg\": ")); f.print(t.brix, 1); f.println(F(","));
        f.print(F("    \"transmittance_pct\": ")); f.print(t.transmittance, 1); f.println(F(","));
        f.print(F("    \"clarity\": \"")); f.print(t.clarity); f.println(F("\","));
      }

      f.print(F("    \"absorbance\": ["));
      f.print(t.absorbance[0], 3); f.print(F(", "));
      f.print(t.absorbance[1], 3); f.print(F(", "));
      f.print(t.absorbance[2], 3); f.print(F(", "));
      f.print(t.absorbance[3], 3); f.print(F(", "));
      f.print(t.absorbance[4], 3);
      f.println(F("]\n  }"));

      f.println(F("]"));
      f.close();
      Serial.println(F("[JSON DB] Record saved to DATA_LOG.json"));
    }
  }

  // Handle incoming HTTP REST clients (only active when ENABLE_WIFI_SERVER == 1)
  void handleClient(const SpectrometerTelemetry& t, bool& triggerScanSoil, bool& triggerScanLiquid, bool& triggerCalib) {
#if ENABLE_WIFI_SERVER
    WiFiClient client = server.available();
    if (!client) return;

    String req = "";
    while (client.connected() && client.available()) {
      char c = client.read();
      req += c;
      if (req.endsWith("\r\n\r\n")) break;
    }

    auto sendCorsHeaders = [&client](int code = 200) {
      if (code == 200) client.println(F("HTTP/1.1 200 OK"));
      else if (code == 204) client.println(F("HTTP/1.1 204 No Content"));
      else client.println(F("HTTP/1.1 404 Not Found"));

      client.println(F("Content-Type: application/json; charset=utf-8"));
      client.println(F("Access-Control-Allow-Origin: *"));
      client.println(F("Access-Control-Allow-Methods: GET, POST, OPTIONS"));
      client.println(F("Access-Control-Allow-Headers: Content-Type"));
      client.println(F("Connection: close"));
      client.println();
    };

    if (req.startsWith("OPTIONS")) {
      sendCorsHeaders(204);
      client.stop();
      return;
    }

    if (req.indexOf("GET /api/status") >= 0) {
      sendCorsHeaders(200);
      client.print(F("{\"status\":\"ONLINE\",\"device\":\"Wio Terminal ATSAMD51\",\"mode\":\""));
      client.print(isApMode ? F("AP") : F("STA"));
      client.print(F("\",\"ip\":\""));
      client.print(ipAddr);
      client.print(F("\",\"rssi\":"));
      client.print(getRSSI());
      client.print(F(",\"page\":"));
      client.print(t.currentPage);
      client.print(F(",\"records\":"));
      client.print(recordCounter);
      client.println(F("}"));
    }
    else if (req.indexOf("GET /api/latest") >= 0) {
      sendCorsHeaders(200);
      client.print(F("{"));
      client.print(F("\"type\":\"")); client.print(t.isSoil ? F("SOIL_NPK") : F("LIQUID_OPTICS")); client.print(F("\","));
      client.print(F("\"n\":")); client.print(t.n, 1); client.print(F(","));
      client.print(F("\"p\":")); client.print(t.p, 1); client.print(F(","));
      client.print(F("\"k\":")); client.print(t.k, 1); client.print(F(","));
      client.print(F("\"soil_ph\":")); client.print(t.soil_ph, 2); client.print(F(","));
      client.print(F("\"refractive_n\":")); client.print(t.ref_n, 4); client.print(F(","));
      client.print(F("\"density\":")); client.print(t.density, 3); client.print(F(","));
      client.print(F("\"brix\":")); client.print(t.brix, 1); client.print(F(","));
      client.print(F("\"transmittance\":")); client.print(t.transmittance, 1); client.print(F(","));
      client.print(F("\"clarity\":\"")); client.print(t.clarity); client.print(F("\","));
      client.print(F("\"absorbance\":["));
      for (int i = 0; i < 5; i++) {
        client.print(t.absorbance[i], 3);
        if (i < 4) client.print(F(","));
      }
      client.println(F("]}"));
    }
    else if (req.indexOf("GET /api/history") >= 0) {
      sendCorsHeaders(200);
      if (SD.exists(JSON_LOG_FILE)) {
        File f = SD.open(JSON_LOG_FILE, FILE_READ);
        if (f) {
          while (f.available()) {
            client.write(f.read());
          }
          f.close();
        } else {
          client.println(F("[]"));
        }
      } else {
        client.println(F("[]"));
      }
    }
    else if (req.indexOf("POST /api/scan-soil") >= 0 || req.indexOf("POST /api/scan?type=soil") >= 0) {
      triggerScanSoil = true;
      sendCorsHeaders(200);
      client.println(F("{\"status\":\"OK\",\"message\":\"Soil NPK Scan Triggered\"}"));
    }
    else if (req.indexOf("POST /api/scan-liquid") >= 0 || req.indexOf("POST /api/scan?type=liquid") >= 0) {
      triggerScanLiquid = true;
      sendCorsHeaders(200);
      client.println(F("{\"status\":\"OK\",\"message\":\"Liquid Optics Scan Triggered\"}"));
    }
    else if (req.indexOf("POST /api/calibrate") >= 0) {
      triggerCalib = true;
      sendCorsHeaders(200);
      client.println(F("{\"status\":\"OK\",\"message\":\"Blank Reference Calibrated\"}"));
    }
    else {
      sendCorsHeaders(200);
      client.println(F("{\"message\":\"NPK Spectrometer 2026 REST API Server\",\"version\":\"1.0.2\"}"));
    }

    client.stop();
#else
    // Standalone mode: do nothing
    (void)t;
    (void)triggerScanSoil;
    (void)triggerScanLiquid;
    (void)triggerCalib;
#endif
  }
};

#endif // WIFI_SERVER_ENGINE_H
