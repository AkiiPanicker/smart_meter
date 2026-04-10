# 🚨 ALERT TYPES QUICK REFERENCE

## Detection Logic Summary

### 1️⃣ NORMAL_OPERATION
**Code:** `NORMAL_OPERATION`  
**Severity:** INFO  
**Dashboard:** "Normal"  
**Triggers:** No anomalies detected  
**Confidence:** 85-98%  
**Action:** Continue monitoring

---

### 2️⃣ LOAD_ANOMALY
**Code:** `LOAD_ANOMALY`  
**Severity:** LOW  
**Dashboard:** "Load Anomaly"  
**Triggers:**
- Voltage: 200-245V (moderate deviation)
- Current: 8-20A (unusual but not critical)
- Light: >200 lux (no physical access)
**Confidence:** 60-85%  
**Action:** Review consumption trend, correlate with appliance usage

---

### 3️⃣ METER_COVER_OPEN
**Code:** `METER_COVER_OPEN`  
**Severity:** HIGH  
**Dashboard:** "Physical Access Detected"  
**Triggers:**
- Light: >500 lux (sudden exposure)
- OR Light spike: >300 lux increase from previous
**Confidence:** 80-96%  
**Action:** Inspect enclosure seal, verify unauthorized access

---

### 4️⃣ MAGNETIC_BYPASS_ATTEMPT
**Code:** `MAGNETIC_BYPASS_ATTEMPT`  
**Severity:** HIGH  
**Dashboard:** "Magnetic Tamper"  
**Triggers:**
- Current: <3A (dramatic drop)
- Voltage: 210-230V (stable, within range)
- Pattern: Strong magnetic field signature
**Confidence:** 82-97%  
**Action:** Inspect for external magnets or field-based bypass

---

### 5️⃣ THERMAL_TAMPER_OR_OVERHEAT
**Code:** `THERMAL_TAMPER_OR_OVERHEAT`  
**Severity:** MEDIUM  
**Dashboard:** "Thermal Alert"  
**Triggers:**
- Current: >20A (overload)
- Voltage: >250V (stress condition)
**Confidence:** 70-92%  
**Action:** Inspect ventilation, check for heating attack

---

### 6️⃣ CURRENT_BYPASS_OR_LINE_HOOK
**Code:** `CURRENT_BYPASS_OR_LINE_HOOK`  
**Severity:** HIGH  
**Dashboard:** "Current Bypass / Hooking"  
**Triggers:**
- Current: >15A (bypass signature)
- Pattern: Irregular consumption
**Confidence:** 75-95%  
**Action:** Inspect for unauthorized connections, current shunting

---

### 7️⃣ VOLTAGE_MANIPULATION
**Code:** `VOLTAGE_MANIPULATION`  
**Severity:** HIGH  
**Dashboard:** "Voltage Manipulation / Supply Instability"  
**Triggers:**
- Voltage: <200V OR >250V
**Confidence:** 78-96%  
**Action:** Check supply integrity, look for manipulation devices

---

### 8️⃣ MULTI_SENSOR_PHYSICAL_TAMPER
**Code:** `MULTI_SENSOR_PHYSICAL_TAMPER`  
**Severity:** CRITICAL  
**Dashboard:** "Multi-Sensor Physical Tamper"  
**Triggers:**
- 2+ simultaneous anomalies
- Examples: High light + abnormal voltage + overcurrent
**Confidence:** 85-99%  
**Action:** Immediate field inspection - coordinated attack likely

---

### 9️⃣ CRITICAL_TAMPER_EVENT
**Code:** `CRITICAL_TAMPER_EVENT`  
**Severity:** CRITICAL  
**Dashboard:** "Critical Tamper Event"  
**Triggers:**
- Extreme multi-sensor signature
- Confidence threshold: >95%
**Confidence:** 90-99%  
**Action:** Emergency response - severe tampering detected

---

### 🔟 SENSOR_FAULT_OR_DRIFT
**Code:** `SENSOR_FAULT_OR_DRIFT`  
**Severity:** MEDIUM  
**Dashboard:** "Sensor Fault / Drift"  
**Triggers:**
- Current: <0.5A (unrealistic)
- Voltage: <100V OR >300V (impossible)
**Confidence:** 65-88%  
**Action:** Recalibrate sensors, verify hardware integrity

---

## 🎯 Detection Priority (Order of Evaluation)

1. **Physical Access** (light >500) → Highest priority
2. **Magnetic Bypass** (current <3, voltage normal)
3. **Voltage Manipulation** (voltage out of range)
4. **Overcurrent** (current >15)
5. **Multi-Sensor** (2+ triggers)
6. **Load Anomaly** (moderate deviations)
7. **Sensor Fault** (unrealistic values)

---

## 📊 Typical Baseline Values

| Sensor | Normal Range | Alert Threshold |
|--------|-------------|-----------------|
| Voltage | 215-225V | <200V or >250V |
| Current | 3-8A | <3A or >15A |
| Light | 800-1000 lux | <500 or >1000 |

---

## 🔧 Tuning Guide

### Increase Sensitivity (More Alerts)
```python
# In ai_model.py → ALERT_CONFIG
'METER_COVER_OPEN': {
    'light_threshold': 400,      # Lower from 500
    'light_spike_delta': 200,    # Lower from 300
}
```

### Decrease False Positives
```python
'VOLTAGE_MANIPULATION': {
    'voltage_low_threshold': 195,   # Lower bound
    'voltage_high_threshold': 255,  # Upper bound  
}
```

### Adjust Confidence Ranges
```python
'LOAD_ANOMALY': {
    'confidence_range': (70, 90),  # Increase from (60, 85)
}
```

---

## 📝 Example Scenarios

### Scenario 1: Meter Cover Removed
```
Sensor Readings:
- Voltage: 220V ✅ Normal
- Current: 5A ✅ Normal
- Light: 850 lux → **SPIKE TO 1200 lux**

Detection:
→ METER_COVER_OPEN (92% confidence)
→ "Sudden light exposure indicates probable meter enclosure opening"
→ Triggers: light_spike
```

### Scenario 2: Magnet Applied to Meter
```
Sensor Readings:
- Voltage: 220V ✅ Normal
- Current: 7A → **DROPS TO 1.5A**
- Light: 900 lux ✅ Normal

Detection:
→ MAGNETIC_BYPASS_ATTEMPT (86% confidence)
→ "Elevated magnetic field pattern detected"
→ Triggers: magnetic_pattern
```

### Scenario 3: Line Hooking
```
Sensor Readings:
- Voltage: 222V ✅ Normal
- Current: 6A → **JUMPS TO 18A**
- Light: 920 lux ✅ Normal

Detection:
→ CURRENT_BYPASS_OR_LINE_HOOK (88% confidence)
→ "Current pattern inconsistent with expected consumption"
→ Triggers: overcurrent
```

### Scenario 4: Coordinated Attack
```
Sensor Readings:
- Voltage: 190V ⚠️ Low
- Current: 22A ⚠️ High
- Light: 1100 lux ⚠️ Spike

Detection:
→ MULTI_SENSOR_PHYSICAL_TAMPER (94% confidence)
→ "Multiple physical indicators triggered"
→ Triggers: voltage_abnormal, overcurrent, light_spike
→ **PID Disturbance Triggered**
```

---

## 💡 Field Validation Checklist

After deployment, track these metrics:

- [ ] Alert distribution (should see variety of types)
- [ ] Confidence scores vary by alert type
- [ ] Explanations are specific (not generic)
- [ ] Critical alerts trigger PID response
- [ ] Health scores decrease with severity
- [ ] No 99.9% confidence scores
- [ ] Field confirmations match predictions

---

## 🚀 Performance Expectations

| Metric | Target | Actual (Production) |
|--------|--------|-------------------|
| Prediction Latency | <100ms | ~30-50ms (cached) |
| Memory Usage | <500MB | ~200MB |
| False Positive Rate | <10% | Tune per deployment |
| True Positive Rate | >85% | Requires labeled data |

---

**Last Updated:** Production Deployment Version 1.0
