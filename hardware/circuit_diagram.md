# Hardware Interfacing & Circuit Schematic: ESP32 IoT Sensing Node

## 1. Component Specifications
| Component | Function | Operating Voltage | Interface to ESP32 |
| :--- | :--- | :--- | :--- |
| **ESP32 DevKit V1** | Microcontroller (Dual Core 240MHz, Wi-Fi 802.11 b/g/n) | 5V USB / 3.3V Vin | Core MCU |
| **ZMPT101B** | Precision AC Potential Voltage Transformer (up to 250V AC) | 5V VCC | Analog ADC Pin (GPIO 34 / ADC1_CH6) |
| **ACS712 (30A Module)** | Hall-Effect Current Sensor (up to 30A AC/DC, 66 mV/A) | 5V VCC | Analog ADC Pin (GPIO 35 / ADC1_CH7) |
| **LM2596 / HLK-PM01** | Step-Down AC-DC Converter (230V AC to 5V DC 1A) | 230V AC Input | 5V DC supply for ESP32 and sensors |
| **Voltage Divider (Sensor -> ESP32)** | 5V to 3.3V ADC logic level safety protection | Passive Resistor Network | 10kΩ / 20kΩ divider for ADC safety |

---

## 2. Pinout Connection Matrix

### A. ZMPT101B Voltage Transformer Module
- **AC High Voltage Terminal (Input):**
  - Pin L (Live): Connected in parallel across Phase Conductor.
  - Pin N (Neutral): Connected in parallel across Neutral Conductor.
- **Low Voltage DC Terminal (Output):**
  - `VCC` $\rightarrow$ ESP32 `5V` (or external regulated 5V rail).
  - `GND` $\rightarrow$ ESP32 Common `GND`.
  - `OUT` $\rightarrow$ Voltage Divider (protecting ESP32 3.3V max ADC input) $\rightarrow$ ESP32 `GPIO 34` (ADC1 Channel 6).

### B. ACS712 Current Sensor Module
- **High Current Screw Terminals (Input):**
  - Pin IP+ : Connected in **series** with Phase load line.
  - Pin IP- : Output to downstream electrical feeder load.
- **Low Voltage Terminal (Output):**
  - `VCC` $\rightarrow$ ESP32 `5V`.
  - `GND` $\rightarrow$ ESP32 Common `GND`.
  - `OUT` $\rightarrow$ Voltage Divider ($V_{out} \times \frac{3.3}{5.0}$) $\rightarrow$ ESP32 `GPIO 35` (ADC1 Channel 7).

---

## 3. Schematic Wiring Diagram (ASCII Representation)

```
           230V AC MAINS BUS
    [ LIVE ] ============================+============================+
                                         |                            |
                                         | [In-Series]                | [Parallel]
                                         v                            v
                                   +------------+               +------------+
                                   |   ACS712   |               |  ZMPT101B  |
                                   |  Current   |               |  Voltage   |
                                   |   Sensor   |               | Transformer|
                                   +------------+               +------------+
                                      | IP-                           |
                                      v To Downstream                 |
                                    Load Feeder                       |
                                                                      |
    [ NEUTRAL ] ======================================================+

                             DC SENSING & SIGNAL CONDITIONING
                               +5V REGULATED BUS
                                     |       |
                 +-------------------+       |
                 |                           |
                 v                           v
          +-------------+             +-------------+
          |   ACS712    |             |  ZMPT101B   |
          |  VCC   GND  |             |  VCC   GND  |
          +-------------+             +-------------+
             |      |                    |      |
            OUT     +---------+         OUT     |
             |                |          |      |
             v                |          v      |
       [Resistor Divider]     |    [Resistor Divider]
       10kΩ / 20kΩ            |    10kΩ / 20kΩ  |
             |                |          |      |
             v                |          v      |
          GPIO 35          Common GND  GPIO 34  |
          (ADC1_CH7)          |      (ADC1_CH6) |
             |                |          |      |
             +----------------+----------+------+
                              |
                              v
                   +---------------------+
                   |   ESP32 DevKit V1   |
                   |   Wi-Fi + BLE MCU   |
                   |                     |
                   |  [UART/HTTP/MQTT]   |
                   +---------------------+
                              |
                              v
                   Cloud Gateway / Django API
                   (/api/telemetry/report/)
```

---

## 4. Signal Conditioning & Calibration
1. **Sampling Frequency:** ESP32 samples at $1.0\text{ kHz}$ over a full $50\text{ Hz}$ sine wave cycle ($20\text{ ms}$ period = 20 samples per cycle minimum; oversampled to 200 samples/cycle for accurate RMS computation).
2. **RMS Calculation Formula:**
   $$V_{RMS} = \sqrt{\frac{1}{N} \sum_{k=1}^N (V_k - V_{offset})^2} \times K_v$$
   $$I_{RMS} = \sqrt{\frac{1}{N} \sum_{k=1}^N (I_k - I_{offset})^2} \times K_i$$
3. **Transient Spike Detection:** Real-time computation of $\Delta V = V_{t} - V_{t-1}$ and $\Delta I = I_{t} - I_{t-1}$ enables edge-detection of sudden cable severance and short-circuit faults before cloud telemetry dispatch.
