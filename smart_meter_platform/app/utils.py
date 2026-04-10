import random
import string
import json
import os
from datetime import datetime
from typing import List, Dict, Optional
from app.models import MeterReading, TamperReason

def generate_hex_string(length: int) -> str:
    """Generates a random hex string of a given length."""
    return ''.join(random.choices(string.hexdigits.lower(), k=length))

def generate_mock_reading(node_id: str, force_tamper: bool = False) -> MeterReading:
    """Generates a single mock meter reading."""
    is_tamper = force_tamper or random.random() < 0.15
    tamper_reasons: list[TamperReason] = [
        'Abnormal Voltage', 'Overcurrent', 'Light Tamper', 
        'Switch Tampering', 'Magnetic Interference', 'Physical Access'
    ]
    
    return MeterReading(
        node_id=node_id,
        timestamp=datetime.utcnow().isoformat() + "Z",
        voltage=220 + random.uniform(25, 50) if is_tamper else 220 + random.uniform(-5, 5),
        current=15 + random.uniform(5, 20) if is_tamper else 5 + random.uniform(0, 5),
        light=random.uniform(0, 200) if is_tamper else random.uniform(800, 1000),
        event_type='TAMPER' if is_tamper else 'NORMAL',
        tamper_reason=random.choice(tamper_reasons) if is_tamper else None,
        confidence=random.uniform(75, 100) if is_tamper else random.uniform(50, 80),
        ciphertext=generate_hex_string(32), 
        hmac=generate_hex_string(64), 
        verified=random.random() > 0.1
    )

def load_sensor_logs(filepath: str) -> List[Dict]:
    """Load sensor data from JSON file."""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                data = json.load(f)
                result = data if isinstance(data, list) else []
                return result
        else:
            print(f"Warning: {filepath} not found. Returning empty list.")
            return []
    except json.JSONDecodeError as e:
        print(f"Error reading JSON: {e}")
        return []
    except Exception as e:
        print(f"Error loading sensor logs: {e}")
        return []

def classify_tamper_reason(voltage: float, current: float, light: float) -> Optional[TamperReason]:
    """
    ENHANCED: Intelligent tamper reason classification based on sensor values
    """
    # Priority-based classification (check most specific first)
    
    # 1. Physical Access (Light spike - highest priority)
    if light > 500:
        return 'Physical Access'
    
    # 2. Magnetic Interference (low current + normal voltage)
    if current < 3 and 210 <= voltage <= 230:
        return 'Magnetic Interference'
    
    # 3. Voltage Abnormality
    if voltage > 250 or voltage < 200:
        return 'Abnormal Voltage'
    
    # 4. Overcurrent / Bypass
    if current > 15:
        return 'Overcurrent'
    
    # 5. Light Tamper (moderate light anomaly)
    if light < 500:
        return 'Light Tamper'
    
    # 6. Default for any other anomaly
    return 'Switch Tampering'

def convert_json_to_meter_reading(json_data: Dict) -> MeterReading:
    """
    ENHANCED: Convert JSON data format to MeterReading with intelligent classification
    """
    voltage = float(json_data.get('voltage', 220))
    current = float(json_data.get('current', 5))
    light = float(json_data.get('lightIntensity', 900))
    
    # Determine event type
    event_type = 'TAMPER' if json_data.get('tamperFlag', 0) == 1 else 'NORMAL'
    
    # Classify tamper reason if anomaly detected
    tamper_reason = None
    if event_type == 'TAMPER':
        tamper_reason = classify_tamper_reason(voltage, current, light)
    
    # Calculate realistic confidence based on sensor deviation
    if event_type == 'TAMPER':
        # Higher confidence for more extreme deviations
        voltage_dev = abs(voltage - 220) / 220
        current_dev = abs(current - 5) / 5 if current > 5 else 0
        light_dev = abs(light - 900) / 900 if light < 900 else 0
        
        max_dev = max(voltage_dev, current_dev, light_dev)
        confidence = min(95, 60 + max_dev * 100)
    else:
        confidence = random.uniform(85, 95)
    
    return MeterReading(
        node_id=json_data.get('node_id', 'UNKNOWN'),
        timestamp=json_data.get('timestamp', datetime.utcnow().isoformat() + "Z"),
        voltage=voltage,
        current=current,
        light=light,
        event_type=event_type,
        tamper_reason=tamper_reason,
        confidence=round(confidence, 1),
        ciphertext=generate_hex_string(32),
        hmac=generate_hex_string(64),
        verified=True,
        health_score=100  # Will be updated by AI model
    )

def calculate_alert_severity(confidence: float, alert_type: str) -> str:
    """
    Calculate severity level based on confidence and alert type
    """
    critical_types = [
        'CRITICAL_TAMPER_EVENT',
        'MULTI_SENSOR_PHYSICAL_TAMPER',
        'METER_COVER_OPEN',
        'MAGNETIC_BYPASS_ATTEMPT'
    ]
    
    high_types = [
        'CURRENT_BYPASS_OR_LINE_HOOK',
        'VOLTAGE_MANIPULATION',
        'THERMAL_TAMPER_OR_OVERHEAT'
    ]
    
    if alert_type in critical_types or confidence > 90:
        return 'high'
    elif alert_type in high_types or confidence > 75:
        return 'medium'
    else:
        return 'low'
