import random
from dataclasses import dataclass, field
from datetime import datetime
from typing import Literal, List, Optional

# Extended Event Types
EventType = Literal[
    'NORMAL',
    'TAMPER',
    'NORMAL_OPERATION',
    'LOAD_ANOMALY',
    'METER_COVER_OPEN',
    'MAGNETIC_BYPASS_ATTEMPT',
    'THERMAL_TAMPER_OR_OVERHEAT',
    'CURRENT_BYPASS_OR_LINE_HOOK',
    'VOLTAGE_MANIPULATION',
    'MULTI_SENSOR_PHYSICAL_TAMPER',
    'CRITICAL_TAMPER_EVENT',
    'SENSOR_FAULT_OR_DRIFT',
    'Physical Access Detected',  # Dashboard labels
    'Magnetic Tamper',
    'Thermal Alert',
    'Current Bypass / Hooking',
    'Voltage Manipulation / Supply Instability',
    'Multi-Sensor Physical Tamper',
    'Critical Tamper Event',
    'Sensor Fault / Drift',
    'Load Anomaly',
    'Normal'
]

TamperReason = Literal[
    'Abnormal Voltage',
    'Overcurrent', 
    'Light Tamper',
    'Switch Tampering',
    'Magnetic Interference',
    'Physical Access',
    'Current Bypass',
    'Multi-Sensor Alert',
    'Thermal Anomaly',
    'Sensor Drift',
    None
]

Severity = Literal['low', 'medium', 'high']

@dataclass
class MeterReading:
    node_id: str
    timestamp: str
    voltage: float
    current: float
    light: float
    event_type: EventType
    tamper_reason: Optional[TamperReason] = None
    confidence: float = 0.0
    ciphertext: str = ""
    hmac: str = ""
    verified: bool = True
    health_score: int = 100

@dataclass
class AIPrediction:
    timestamp: str
    node_id: str
    event_type: EventType
    confidence: float
    explanation: str
    severity: Severity
