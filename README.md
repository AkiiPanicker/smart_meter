# ⚡ VoltGuard

**Real-Time Tamper Detection & Secure Smart Meter Intelligence**

VoltGuard is a hardware-rooted, cryptographically secure smart metering platform designed to detect electricity tampering in real time, stabilize electrical measurements using PID control, and securely stream telemetry to an AI-powered monitoring dashboard.

The system combines:

- Multi-modal physical and electrical tamper sensing
- Embedded cryptographic telemetry (AES-128 + HMAC-SHA256)
- RTC-based tamper logging with persistent counter
- On-device status display (Green = Normal, Red = Tamper)
- UART-to-JSON telemetry bridge
- Flask-based monitoring dashboard
- Grid-level anomaly classification

This project represents a full-stack integration of hardware security, embedded control systems, and backend intelligence.

---

## 📉 Problem Statement

Electricity theft and transmission inefficiencies result in massive annual revenue losses and grid instability. Traditional metering systems lack:

- Secure device identity
- End-to-end encrypted telemetry
- Real-time anomaly detection
- Tamper-proof firmware validation
- Predictive grid stabilization

VoltGuard addresses these weaknesses using a multi-layered secure architecture combining hardware security, control theory, and AI-driven intelligence.

---

## 🏗 System Architecture

VoltGuard follows a layered secure design:

### 1️⃣ Meter Node (Hardware Layer)

- Multi-modal tamper sensing
- Voltage & current monitoring
- Secure boot chain
- AES-128 encrypted telemetry
- HMAC-SHA256 integrity signing
- Hardware-rooted cryptographic identity

**States:**

| State | Description |
|-------|-------------|
| `NORMAL` | Operating within threshold |
| `TAMPERING` | Anomaly detected and logged with timestamp |

### 2️⃣ Edge / Gateway Layer

- Digital signature verification
- Rejects unauthenticated data
- Secure transport enforcement
- Real-time telemetry forwarding

### 3️⃣ Backend Intelligence Layer

- Real-time telemetry monitoring
- AI-driven tamper classification
- Confidence & severity scoring
- Historical event logging
- Operational visibility dashboard

---

## 🧠 AI Model

The AI subsystem performs:

- Load anomaly detection
- Tamper classification
- Pattern recognition in voltage/current deviations
- Confidence-based alert scoring
- Predictive instability detection

**Future Scope:**
- Adaptive model retraining
- Cloud-integrated intelligence
- PID-AI hybrid auto-tuning

---

## ⚙ PID-Based Physical Stabilization

VoltGuard integrates control theory for grid stability:

```
u(t) = Kp * e(t) + Ki * ∫ e(t) dt + Kd * (de(t)/dt)

Where:
  e(t) = voltage deviation
  Kp   = proportional gain
  Ki   = integral gain
  Kd   = derivative gain
```

This enables:

- Voltage stabilization
- Predictive corrective action
- Hybrid AI-assisted regulation (future roadmap)

---

## 🌐 Flask Dashboard

Built using Flask, the dashboard provides:

- Real-time meter telemetry
- Statistical anomaly visualization
- Tamper alerts
- Historical logs
- Fleet-scale monitoring
- Grid-level observability

---

## 🔐 Security Model

VoltGuard enforces:

- Hardware-rooted identity
- Secure boot attestation
- Firmware authenticity verification
- AES transport encryption
- HMAC integrity verification
- Mutual authentication

> Unauthenticated devices are automatically rejected.

---

## ⚙ Hardware Setup (TI Code Composer Studio)

Firmware is pre-configured. No code editing required.

### 🔌 Step 1 - Open Firmware in CCS

1. Launch TI Code Composer Studio (CCS)
2. Go to: **File → Open Folder**
3. Select: `VoltGuard/firmware/`
4. Ensure the project appears in Project Explorer

### ⚡ Step 2 - Flash the MCU

1. Expand the project
2. Right-click: `main_project`
3. Select: **Flash**
4. The firmware will be programmed onto the microcontroller
5. Ensure the device exits debug mode and runs normally after flashing

### 🖥 UART Verification

1. Connect the device via USB
2. Open Device Manager and locate the COM port labeled **Texas Instruments** - note the port number (e.g. `COM6`)
3. Open a serial console (inside CCS or external) and configure it with the COM port you located above:

```
Port:      COM6  (use the Texas Instruments port from Device Manager)
Baud Rate: 115200
(Keep other settings default)
```

You should see real-time telemetry output.

---

## 🖥 Software Setup (Python Backend)

**Requirements:** Python 3.12

### 📦 Install Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

### ▶️ Correct Startup Order

> ⚠️ Always start the UART bridge **before** launching Flask.

**1️⃣ Start UART Bridge**

```bash
python smart_meter_platform/uart_to_logsJSON.py
```

Inside that file, verify:

```python
SERIAL_PORT = "COM6"   # Change if needed
BAUD_RATE = 115200
```

Adjust the COM port if different on your system.

**2️⃣ Start Flask Dashboard**

```bash
python smart_meter_platform/run.py
```

Open browser: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔁 Complete Internal Workflow

```
Open CCS
    ↓
Open firmware folder
    ↓
Right-click main_project → Flash
    ↓
Verify UART @ 115200
    ↓
Run uart_to_logsJSON.py
    ↓
Run run.py
    ↓
Open Dashboard
```

---

## 📦 Project Structure

```
VoltGuard/
│
├── smart_meter_platform/
│   ├── app/
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── pid_controller.py
│   │   ├── ai_model.py
│   │   └── utils.py
│   │
│   ├── templates/
│   ├── static/
│   └── run.py
│
├── firmware/
├── hardware/
└── README.md
```

---

## 📊 Impact

VoltGuard enables:

- Reduction in tampering events
- Improved revenue reali# ⚡ VoltGuard

**Real-Time Tamper Detection & Secure Smart Meter Intelligence**

VoltGuard is a hardware-rooted, cryptographically secure smart metering platform designed to detect electricity tampering in real time, stabilize electrical measurements using PID control, and securely stream telemetry to an AI-powered monitoring dashboard.

The system combines:

- Multi-modal physical and electrical tamper sensing
- Embedded cryptographic telemetry (AES-128 + HMAC-SHA256)
- RTC-based tamper logging with persistent counter
- On-device status display (Green = Normal, Red = Tamper)
- UART-to-JSON telemetry bridge
- Flask-based monitoring dashboard
- Grid-level anomaly classification

This project represents a full-stack integration of hardware security, embedded control systems, and backend intelligence.

---

## 📉 Problem Statement

Electricity theft and transmission inefficiencies result in massive annual revenue losses and grid instability. Traditional metering systems lack:

- Secure device identity
- End-to-end encrypted telemetry
- Real-time anomaly detection
- Tamper-proof firmware validation
- Predictive grid stabilization

VoltGuard addresses these weaknesses using a multi-layered secure architecture combining hardware security, control theory, and AI-driven intelligence.

---

## 🏗 System Architecture

VoltGuard follows a layered secure design:

### 1️⃣ Meter Node (Hardware Layer)

- Multi-modal tamper sensing
- Voltage & current monitoring
- Secure boot chain
- AES-128 encrypted telemetry
- HMAC-SHA256 integrity signing
- Hardware-rooted cryptographic identity

**States:**

| State | Description |
|-------|-------------|
| `NORMAL` | Operating within threshold |
| `TAMPERING` | Anomaly detected and logged with timestamp |

### 2️⃣ Edge / Gateway Layer

- Digital signature verification
- Rejects unauthenticated data
- Secure transport enforcement
- Real-time telemetry forwarding

### 3️⃣ Backend Intelligence Layer

- Real-time telemetry monitoring
- AI-driven tamper classification
- Confidence & severity scoring
- Historical event logging
- Operational visibility dashboard

---

## 🧠 AI Model

The AI subsystem performs:

- Load anomaly detection
- Tamper classification
- Pattern recognition in voltage/current deviations
- Confidence-based alert scoring
- Predictive instability detection

**Future Scope:**
- Adaptive model retraining
- Cloud-integrated intelligence
- PID-AI hybrid auto-tuning

---

## ⚙ PID-Based Physical Stabilization

VoltGuard integrates control theory for grid stability:

```
u(t) = Kp * e(t) + Ki * ∫ e(t) dt + Kd * (de(t)/dt)

Where:
  e(t) = voltage deviation
  Kp   = proportional gain
  Ki   = integral gain
  Kd   = derivative gain
```

This enables:

- Voltage stabilization
- Predictive corrective action
- Hybrid AI-assisted regulation (future roadmap)

---

## 🌐 Flask Dashboard

Built using Flask, the dashboard provides:

- Real-time meter telemetry
- Statistical anomaly visualization
- Tamper alerts
- Historical logs
- Fleet-scale monitoring
- Grid-level observability

---

## 🔐 Security Model

VoltGuard enforces:

- Hardware-rooted identity
- Secure boot attestation
- Firmware authenticity verification
- AES transport encryption
- HMAC integrity verification
- Mutual authentication

> Unauthenticated devices are automatically rejected.

---

## ⚙ Hardware Setup (TI Code Composer Studio)

Firmware is pre-configured. No code editing required.

### 🔌 Step 1 - Open Firmware in CCS

1. Launch TI Code Composer Studio (CCS)
2. Go to: **File → Open Folder**
3. Select: `VoltGuard/firmware/`
4. Ensure the project appears in Project Explorer

### ⚡ Step 2 - Flash the MCU

1. Expand the project
2. Right-click: `main_project`
3. Select: **Flash**
4. The firmware will be programmed onto the microcontroller
5. Ensure the device exits debug mode and runs normally after flashing

### 🖥 UART Verification

1. Connect the device via USB
2. Open Device Manager and locate the COM port labeled **Texas Instruments** - note the port number (e.g. `COM6`)
3. Open a serial console (inside CCS or external) and configure it with the COM port you located above:

```
Port:      COM6  (use the Texas Instruments port from Device Manager)
Baud Rate: 115200
(Keep other settings default)
```

You should see real-time telemetry output.

---

## 🖥 Software Setup (Python Backend)

**Requirements:** Python 3.12

### 📦 Install Dependencies

From the project root:

```bash
pip install -r requirements.txt
```

### ▶️ Correct Startup Order

> ⚠️ Always start the UART bridge **before** launching Flask.

**1️⃣ Start UART Bridge**

```bash
python smart_meter_platform/uart_to_logsJSON.py
```

Inside that file, verify:

```python
SERIAL_PORT = "COM6"   # Change if needed
BAUD_RATE = 115200
```

Adjust the COM port if different on your system.

**2️⃣ Start Flask Dashboard**

```bash
python smart_meter_platform/run.py
```

Open browser: [http://127.0.0.1:5000](http://127.0.0.1:5000)

---

## 🔁 Complete Internal Workflow

```
Open CCS
    ↓
Open firmware folder
    ↓
Right-click main_project → Flash
    ↓
Verify UART @ 115200
    ↓
Run uart_to_logsJSON.py
    ↓
Run run.py
    ↓
Open Dashboard
```

---

## 📦 Project Structure

```
VoltGuard/
│
├── smart_meter_platform/
│   ├── app/
│   │   ├── models.py
│   │   ├── routes.py
│   │   ├── pid_controller.py
│   │   ├── ai_model.py
│   │   └── utils.py
│   │
│   ├── templates/
│   ├── static/
│   └── run.py
│
├── firmware/
├── hardware/
└── README.md
```

---

## 📊 Impact

VoltGuard enables:

- Reduction in tampering events
- Improved revenue realization
- Reduced grid instability
- Transparent audit trails
- Scalable deployment architecture

---

## 🛣 Deployment Vision

- Pilot deployments with live tamper dashboard validation
- Scalable expansion model
- Transition from hardware-centric to grid intelligence platform
- PID-AI hybrid adaptive grid control

---

## 🔮 Future Scope

- Cloud-based telemetry pipeline
- Remote firmware updates
- Smart Grid 2.0 interoperability
- EV & solar load balancing
- Nationwide smart meter integration

---zation
- Reduced grid instability
- Transparent audit trails
- Scalable deployment architecture

---

## 🛣 Deployment Vision

- Pilot deployments with live tamper dashboard validation
- Scalable expansion model
- Transition from hardware-centric to grid intelligence platform
- PID-AI hybrid adaptive grid control

---

## 🔮 Future Scope

- Cloud-based telemetry pipeline
- Remote firmware updates
- Smart Grid 2.0 interoperability
- EV & solar load balancing
- Nationwide smart meter integration

---

*⚡ VoltGuard - Hardware-first. Security-driven. Grid-aware.*
