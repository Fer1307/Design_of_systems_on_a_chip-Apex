# mBot Line Follower 🤖

An autonomous line-following robot built on a **distributed architecture**: a Raspberry Pi handles computer vision and decision-making, while a MegaPi (ATmega2560) running FreeRTOS handles real-time motor control. The two boards communicate over UART using single-byte commands.

## 👤 Team Apex
* **Team Information:** Luis Fernando Salazar Hernández - A01738527, Magdaleno Pérez Olmos - A01739632, Fatima Valeria Huerta Cabrera - A01739997
* **Institution:** Tecnológico de Monterrey, Campus Puebla
* **Course:** Diseño de Sistemas en Chip (Gpo 501)
---

## 🎯 Project Overview

The robot follows a black line on a light background and autonomously avoids obstacles. The design deliberately splits the workload across two processors to keep each one doing what it does best:

* **Raspberry Pi → Perception & Decision.** Captures video from a USB camera, isolates the line with OpenCV, computes the lateral error relative to the camera center, and sends a direction command (`F`, `L`, `R`, `S`) over serial.
* **MegaPi → Real-Time Control & Actuation.** Receives the command over UART (configured via raw AVR registers, **not** `Serial.begin()`), and drives the four DC motors. A sensor on pin 61 (A7/PF7) triggers an ADC interrupt that launches an automatic ~180° evasion maneuver.

Everything on the MegaPi runs concurrently under FreeRTOS.

---

## ⚙️ System Architecture

```text
┌─────────────────────────┐         UART          ┌──────────────────────────┐
│      Raspberry Pi        │   (F / L / R / S)     │     MegaPi (ATmega2560)   │
│                          │ ────────────────────► │                           │
│  USB Camera              │      1 byte @ 9600    │  FreeRTOS                 │
│  OpenCV pipeline         │                       │   ├─ tareaSerial (prio 2) │
│   ├─ grayscale           │                       │   └─ tareaRobot  (prio 1) │
│   ├─ gaussian blur       │                       │  ADC ISR (sensor pin 61)  │
│   ├─ threshold (INV)     │                       │  MeMegaPiDCMotor ×4       │
│   ├─ ROI mask            │                       │                           │
│   └─ centroid → error    │                       │                           │
└─────────────────────────┘                       └──────────────────────────┘
        PERCEPTION                                          CONTROL
```

---

## 📂 Repository Structure

```text
mbot-line-follower/
├── src/
│   ├── raspberry/
│   │   └── line_follower.py        # OpenCV vision pipeline + serial command sender
│   └── megapi/
│       └── firmware.ino            # FreeRTOS firmware: AVR UART, ADC ISR, motor control
│
├── hardware/
│   ├── mbot_line_follower_wiring.kicad_sch   # Wiring schematic (KiCad)
│   └── chassis/                    # 3D-modeled enclosure (CAD / STL)
│
└── docs/
    ├── presentation/               # Final presentation slides
    └── images/                     # Photos, renders, and debug captures
```

---

## 🧠 Vision Pipeline (Raspberry Pi)

| Stage | Function | Purpose |
|-------|----------|---------|
| Grayscale | `cv2.cvtColor` | Collapse 3 color channels into one intensity channel |
| Smoothing | `cv2.GaussianBlur` | Remove high-frequency floor noise |
| Threshold | `cv2.threshold` (`THRESH_BINARY_INV`) | Isolate the dark line over the light background |
| ROI mask | `cv2.fillPoly` + `cv2.bitwise_and` | Evaluate only the lower strip where the line is |
| Centroid | `cv2.moments` (`m10/m00`) | Locate the line center on the X axis |
| Decision | error vs. `DEAD_ZONE` | Map lateral error → `F` / `L` / `R` |

---

## 🔧 Firmware Highlights (MegaPi)

* **Low-level UART** configured directly through `UBRR0`, `UCSR0B`, and `UCSR0C` registers.
* **Two concurrent FreeRTOS tasks:** `tareaSerial` reads incoming commands; `tareaRobot` executes movement and the evasion routine.
* **ADC interrupt** (`ISR(ADC_vect)`) reads the obstacle sensor and notifies `tareaRobot` via `vTaskNotifyGiveFromISR()`, avoiding any polling.
* **Obstacle evasion:** on detection, the robot stops, performs a ~180° turn, advances, and resumes.
* **Motor trim:** mechanical calibration of +3 on the right side to keep the robot tracking straight.

> Arduino abstractions are minimized by design — only the `MeMegaPiDCMotor` library is used, for motor control.

---

## 🛠️ Hardware

* Makeblock MegaPi (ATmega2560)
* Raspberry Pi + USB webcam
* 4× DC motors (MeMegaPiDCMotor)
* Analog obstacle sensor on pin 61 (A7/PF7)
* USB serial link (Raspberry Pi ↔ MegaPi)
* Custom 3D-printed chassis housing the camera, Raspberry Pi, and sensor

---

## 🚀 Running the System

1. Wire the boards per `hardware/mbot_line_follower_wiring.kicad_sch` and confirm the serial device (default `/dev/ttyUSB0`).
2. Flash `src/megapi/firmware.ino` to the MegaPi.
3. On the Raspberry Pi:
   ```bash
   python3 src/raspberry/line_follower.py
   ```
4. Place the robot on the track and power the motors via the mBot battery switch.
