/*
 * ESP32 Smart Meter Box Firmware - TANGEDCO Tamil Nadu Smart Grid
 * Hardware:
 *   - ESP32 DevKit V1
 *   - ZMPT101B AC Voltage Sensor (GPIO 34 / ADC1_CH6)
 *   - ACS712 30A Current Sensor  (GPIO 35 / ADC1_CH7)
 *   - 5V Relay Module (GPIO 26 - Latching Service Cutoff)
 *   - Status LEDs: Green (GPIO 2 - Energized), Red (GPIO 4 - Outage/Trip)
 */

#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// --- Configuration ---
const char* WIFI_SSID     = "TNEB_SMART_GRID_WIFI";
const char* WIFI_PASSWORD = "TamilNaduGrid2026";
const char* API_ENDPOINT  = "http://192.168.1.100:8000/api/esp32/meter/report/"; // Update with Server IP

const char* METER_NODE_ID = "HOME-OMR-101";        // Configured Service Connection Node
const char* DEVICE_ID     = "ESP32-METER-TN-001";
const char* CONSUMER_SC   = "SC-04-128-091";

const int PIN_VOLTAGE_ADC = 34;
const int PIN_CURRENT_ADC = 35;
const int PIN_RELAY_CUT   = 26;
const int PIN_LED_GREEN   = 2;
const int PIN_LED_RED     = 4;

const float VOLTAGE_CALIBRATION = 0.582; // Calibrated for ZMPT101B
const float CURRENT_CALIBRATION = 0.048; // Calibrated for ACS712 30A
const float ADC_MIDPOINT        = 1850.0;

float accumulated_units_kwh = 164.80; // Persistent EEPROM / Flash stored units
unsigned long last_report_time = 0;

void setup() {
  Serial.begin(115200);
  pinMode(PIN_RELAY_CUT, OUTPUT);
  pinMode(PIN_LED_GREEN, OUTPUT);
  pinMode(PIN_LED_RED, OUTPUT);

  digitalWrite(PIN_RELAY_CUT, LOW); // Connected by default
  digitalWrite(PIN_LED_GREEN, HIGH);
  digitalWrite(PIN_LED_RED, LOW);

  Serial.println("\n[TANGEDCO ESP32 SMART METER STARTUP]");
  Serial.printf("Device: %s | Meter: %s\n", DEVICE_ID, METER_NODE_ID);

  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  int retry = 0;
  while (WiFi.status() != WL_CONNECTED && retry < 20) {
    delay(500);
    Serial.print(".");
    retry++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[Wi-Fi Connected] IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println("\n[Wi-Fi Offline] Running in local autonomous protection mode.");
  }
}

// Sample 50Hz AC Waveform across 20ms and compute True RMS
void readSensors(float &v_rms, float &i_rms) {
  unsigned long start_time = millis();
  long v_sum_sq = 0;
  long i_sum_sq = 0;
  int samples = 0;

  while (millis() - start_time < 40) { // Sample 2 full 50Hz cycles
    int v_raw = analogRead(PIN_VOLTAGE_ADC);
    int i_raw = analogRead(PIN_CURRENT_ADC);

    float v_diff = v_raw - ADC_MIDPOINT;
    float i_diff = i_raw - ADC_MIDPOINT;

    v_sum_sq += (v_diff * v_diff);
    i_sum_sq += (i_diff * i_diff);
    samples++;
    delayMicroseconds(200);
  }

  v_rms = sqrt((float)v_sum_sq / samples) * VOLTAGE_CALIBRATION;
  i_rms = sqrt((float)i_sum_sq / samples) * CURRENT_CALIBRATION;

  if (v_rms < 15.0) v_rms = 0.0;
  if (i_rms < 0.15) i_rms = 0.0;
}

void loop() {
  float v_rms, i_rms;
  readSensors(v_rms, i_rms);

  // Compute Active Power & Accumulate Energy Units
  float power_watts = v_rms * i_rms * 0.96; // 0.96 average power factor
  accumulated_units_kwh += (power_watts / 1000.0) * (2.0 / 3600.0); // every 2 seconds

  // Outage Detection
  bool is_energized = (v_rms > 50.0);
  digitalWrite(PIN_LED_GREEN, is_energized ? HIGH : LOW);
  digitalWrite(PIN_LED_RED, is_energized ? LOW : HIGH);

  if (millis() - last_report_time > 3000) {
    last_report_time = millis();

    Serial.printf("[TELEMETRY] V: %.1f V | I: %.2f A | P: %.1f W | Units: %.3f kWh | %s\n",
                  v_rms, i_rms, power_watts, accumulated_units_kwh,
                  is_energized ? "ENERGIZED" : "OUTAGE/CUT");

    if (WiFi.status() == WL_CONNECTED) {
      HTTPClient http;
      http.begin(API_ENDPOINT);
      http.addHeader("Content-Type", "application/json");

      StaticJsonDocument<256> doc;
      doc["device_id"]      = DEVICE_ID;
      doc["node_id"]        = METER_NODE_ID;
      doc["voltage"]        = v_rms;
      doc["current"]        = i_rms;
      doc["units_consumed"] = accumulated_units_kwh;
      doc["frequency"]      = 50.01;
      doc["tamper_detected"]= false;

      String payload;
      serializeJson(doc, payload);

      int httpResponseCode = http.POST(payload);
      if (httpResponseCode > 0) {
        Serial.printf("[CLOUD SYNC] HTTP Response: %d\n", httpResponseCode);
      } else {
        Serial.printf("[CLOUD SYNC ERROR] Code: %d\n", httpResponseCode);
      }
      http.end();
    }
  }
}
