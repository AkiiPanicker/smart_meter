⚡ VoltGuard
Real-Time Tamper Detection & Secure Smart Meter Intelligence

VoltGuard is a hardware-rooted, cryptographically secure smart metering platform designed to detect electricity tampering in real time, stabilize electrical measurements using PID control, and securely stream telemetry to an AI-powered monitoring dashboard.

The system combines:
* Multi-modal physical and electrical tamper sensing
* Embedded cryptographic telemetry (AES-128 + HMAC-SHA256)
* RTC-based tamper logging with persistent counter
* On-device status display (Green = Normal, Red = Tamper)
* UART-to-JSON telemetry bridge
* Flask-based monitoring dashboard
* Grid-level anomaly classification

This project represents a full-stack integration of hardware security, embedded control systems, and backend intelligence.


👥 Team

* Arnab Ranjan Sikdar
Complete hardware architecture, circuit design, PCB integration, firmware logic, cryptographic implementation (AES-128 + HMAC-SHA256), and full hardware–software bridging.

* Akshat Panicker
Primary author of this repository and core software contributor.
(And as the primary author of this file, I dedicate this to my serii <3)

* Raagmanas Madhukar

* Siddharth Gaur


🏗 System Overview

VoltGuard consists of two major layers:

1️⃣ Smart Meter Hardware Layer
Sensing Subsystem
* Voltage sensing (resistive divider + filtering)
* Current sensing (CT / Hall sensor)
* Magnetic tamper detection
* Light-based enclosure tamper detection
* Temperature monitoring
* Embedded Processing (Cortex-M0+)
* ADC acquisition
* Signal conditioning
* PID-based measurement stabilization
* Electrical + physical tamper logic
* RTC timestamping
* Tamper counter storage
* AES-128 encryption
* HMAC-SHA256 integrity signing
* Secure packet builder
* Display Logic
* NORMAL Mode
  * Green screen
* Live voltage/current values
* Last tamper timestamp
* Tamper count
* TAMPER Mode
  * Red screen - “TAMPER DETECTED”
  * Increment tamper count
  * Update latest timestamp

2️⃣ Software & Dashboard Layer
* UART telemetry ingestion
* JSON log generation
* Flask backend
* AI-based anomaly classification
* Threat visualization dashboard


⚙ Hardware Setup (TI Code Composer Studio)
Firmware is pre-configured. No code editing required.

🔌 Step 1 – Open Firmware in CCS
Launch TI Code Composer Studio (CCS).
Go to:
File → Open Folder
Select:
VoltGuard/firmware/
Ensure the project appears in Project Explorer.

⚡ Step 2 – Flash the MCU
Expand the project.
Right-click: main_project
Select: Flash
The firmware will be programmed onto the microcontroller.
Ensure the device exits debug mode and runs normally after flashing.

🖥 UART Verification
Connect the device via USB.
Open Device Manager.
Locate the COM port labeled: Texas Instruments (Usually COM6, but may vary.)
Open a serial console (located in the view tab) inside the TI CCS software.
Configure:
  * Baud Rate: 115200
  * Keep everything else as it is
You should see real-time telemetry output.

🖥 Software Setup (Python Backend)
Requirements: Python 3.12

📦 Install Dependencies
From the project root:
pip install -r requirements.txt

▶️ Correct Startup Order
⚠ Always start UART bridge before launching Flask.

1️⃣ Start UART Bridge
python smart_meter_platform/uart_to_logsJSON.py

Inside that file, verify:
SERIAL_PORT = "COM6"   # Change if needed
BAUD_RATE = 115200

Adjust the COM port if different on your system.

2️⃣ Start Flask Dashboard
python smart_meter_platform/run.py

Open browser:
http://127.0.0.1:5000


🔁 Complete Internal Workflow
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


🧠 Internal Notes

Always close serial monitor before running uart_to_logsJSON.py.

If UART shows no output:
* Check COM port
* Ensure baud rate is 115200
* Ensure MCU is not halted in debug mode

If dashboard shows no updates:
* Confirm JSON logs are being generated
* Check terminal output of UART bridge

⚡ VoltGuard
Hardware-first. Security-driven. Grid-aware.
