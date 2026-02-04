# ⚡ VoltGuard  
### Real-Time Tamper Detection & Secure Smart Meter Intelligence

VoltGuard is a hardware-rooted, cryptographically secure, AI-powered smart metering system designed to detect electricity tampering in real time, reduce AT&C losses, and enhance grid reliability through secure telemetry and intelligent anomaly detection.


## 👥 Team

- Arnab Ranjan Sikdar 
- Akshat Panicker (And as the author writing this I dedicate it to Serii <3 )
- Raagmanas Madhukar 
- Siddharth Gaur

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

States:
- **NORMAL** – Operating within threshold
- **TAMPERING** – Anomaly detected and logged with timestamp

---

### 2️⃣ Edge / Gateway Layer
- Digital signature verification
- Rejects unauthenticated data
- Secure transport enforcement
- Real-time telemetry forwarding

---

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

Future scope:
- Adaptive model retraining
- Cloud-integrated intelligence
- PID-AI hybrid auto-tuning

---

## ⚙ PID-Based Physical Stabilization

VoltGuard integrates control theory for grid stability:

\[
u(t) = K_p e(t) + K_i \int e(t)dt + K_d \frac{de(t)}{dt}
\]

Where:
- \( e(t) \) = voltage deviation
- \( K_p, K_i, K_d \) = tuned control gains

This enables:
- Voltage stabilization
- Predictive corrective action
- Hybrid AI-assisted regulation (future roadmap)

---

## 🌐 Flask Dashboard

Built using **Flask**, the dashboard provides:

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

Unauthenticated devices are automatically rejected.

---

## 📦 Project Structure

```bash
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

## 🚀 Running the Dashboard

### 1️⃣ Clone the repository

```bash
git clone https://github.com/YOUR_USERNAME/VoltGuard.git
cd VoltGuard
```

### 2️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 3️⃣ Run the server

```bash
python run.py
```

Open in browser:

```
http://127.0.0.1:5000
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

---

## 📜 License

Specify your license here (MIT / Proprietary / etc.)

---

## ⚡ VoltGuard  
Secure. Intelligent. Tamper-Resistant.
