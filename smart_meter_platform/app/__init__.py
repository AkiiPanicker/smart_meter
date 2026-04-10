import threading
import time
import os
import logging
from flask import Flask
from flask_cors import CORS
from app.utils import load_sensor_logs, convert_json_to_meter_reading
from app.models import AIPrediction, MeterReading
from app.ai_model import AlertClassifier
from app.pid_controller import simulation 

# Configure logging
logging.basicConfig(level=logging.INFO)

# Global in-memory database
db = {
    "meter_readings": {},
    "predictions": [],
    "json_data": [],
    "last_processed_index": 0,
    "last_file_size": 0,
    "alert_stats": {  # NEW: Track alert statistics
        'total_processed': 0,
        'by_type': {},
        'by_node': {}
    }
}
predictive_model = None

def get_data_path():
    """Returns the absolute path to sensor_logs.json in the project root."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_dir, 'sensor_logs.json')

def create_app():
    global predictive_model
    app = Flask(__name__, template_folder='../templates', static_folder='../static')
    CORS(app)
    
    from . import routes
    app.register_blueprint(routes.bp)

    with app.app_context():
        # Setup Paths
        data_path = get_data_path()
        model_path = os.path.join(app.root_path, 'lstm_multiclass_classifier.h5')

        # Use enhanced AlertClassifier
        predictive_model = AlertClassifier(model_path=model_path, data_path=data_path)
        
        # Initial load
        reload_json_data()
        initialize_data()

    thread = threading.Thread(target=background_update, args=(app,), daemon=True)
    thread.start()
    
    return app

def reload_json_data():
    """Reloads sensor data from the JSON file."""
    data_path = get_data_path()
    try:
        if os.path.exists(data_path):
            file_size = os.path.getsize(data_path)
            # Reload if file changed OR if memory is empty
            if file_size != db["last_file_size"] or not db["json_data"]:
                data = load_sensor_logs(data_path)
                if data:
                    db["json_data"] = data
                    db["last_file_size"] = file_size
                    print(f"DISK: Loaded {len(db['json_data'])} entries from log file.")
                    return True
    except Exception as e:
        print(f"Error reloading data: {e}")
    return False

def initialize_data():
    """
    ENHANCED: Processes loaded JSON data with intelligent alert classification
    """
    if not db["json_data"]:
        return

    try:
        sorted_data = sorted(db["json_data"], key=lambda x: x.get('timestamp', ''))
        
        # 1. Update Latest State (For Dashboard Cards)
        node_latest = {}
        for entry in sorted_data:
            nid = entry.get('node_id')
            if nid:
                node_latest[nid] = entry
        
        for nid, entry in node_latest.items():
            reading = convert_json_to_meter_reading(entry)
            db["meter_readings"][nid] = reading
        
        # 2. ENHANCED HISTORICAL ALERTS PROCESSING
        db["predictions"] = []
        db["alert_stats"]['by_type'] = {}
        db["alert_stats"]['by_node'] = {}
        
        # Group data by node for context-aware processing
        by_node = {}
        for entry in sorted_data:
            nid = entry.get('node_id', 'UNKNOWN')
            if nid not in by_node:
                by_node[nid] = []
            by_node[nid].append(entry)
        
        # Process each node's history
        for node_id, entries in by_node.items():
            # Process in chronological windows
            for i in range(len(entries)):
                entry = entries[i]
                
                # Get context window (last N readings)
                start_idx = max(0, i - predictive_model.TIME_STEPS + 1)
                context_entries = entries[start_idx:i+1]
                context_readings = [convert_json_to_meter_reading(e) for e in context_entries]
                
                # Only process if we have anomaly indicator OR sufficient history
                has_tamper_flag = entry.get('tamperFlag') == 1
                has_history = len(context_readings) >= predictive_model.TIME_STEPS
                
                if has_tamper_flag or (has_history and i % 20 == 0):  # Sample every 20th for efficiency
                    result = predictive_model.get_health_score_and_prediction(
                        node_id, 
                        context_readings
                    )
                    
                    if result.get('prediction'):
                        pred = result['prediction']
                        # Override timestamp with actual data timestamp
                        pred.timestamp = entry.get('timestamp')
                        
                        db["predictions"].append(pred)
                        
                        # Update stats
                        alert_type = result.get('alert_type', 'UNKNOWN')
                        db["alert_stats"]['by_type'][alert_type] = \
                            db["alert_stats"]['by_type'].get(alert_type, 0) + 1
                        
                        if node_id not in db["alert_stats"]['by_node']:
                            db["alert_stats"]['by_node'][node_id] = 0
                        db["alert_stats"]['by_node'][node_id] += 1
        
        # Sort by timestamp (newest first) and limit
        db["predictions"].sort(key=lambda x: x.timestamp, reverse=True)
        db["predictions"] = db["predictions"][:100]  # Keep last 100
        
        db["last_processed_index"] = len(db["json_data"])
        db["alert_stats"]['total_processed'] = len(db["predictions"])
        
        print(f"✅ Initialized {len(db['predictions'])} alerts across {len(node_latest)} nodes")
        print(f"   Alert distribution: {db['alert_stats']['by_type']}")
        
    except Exception as e:
        print(f"INIT ERROR: {e}")
        import traceback
        traceback.print_exc()

def update_predictions_and_health(node_id):
    """
    ENHANCED: Updates AI prediction with multi-class classification
    """
    if not predictive_model or not db["json_data"]:
        return

    time_steps = predictive_model.TIME_STEPS
    node_history = [x for x in db["json_data"] if x.get('node_id') == node_id]
    
    if not node_history:
        return

    recent_items = node_history[-time_steps:]
    recent_readings = [convert_json_to_meter_reading(item) for item in recent_items]

    # Set Default
    if node_id in db["meter_readings"]:
        db["meter_readings"][node_id].health_score = 100

    if len(recent_readings) >= time_steps:
        result = predictive_model.get_health_score_and_prediction(node_id, recent_readings)
        
        # Update health score
        if node_id in db["meter_readings"]:
            db["meter_readings"][node_id].health_score = result["health_score"]

        # Add new prediction if exists
        if result["prediction"]:
            db["predictions"].insert(0, result["prediction"])
            db["predictions"] = db["predictions"][:100]  # Keep last 100
            
            # Trigger PID disturbance for critical alerts
            alert_type = result.get("alert_type", "")
            if alert_type in ['CRITICAL_TAMPER_EVENT', 'MULTI_SENSOR_PHYSICAL_TAMPER', 
                             'METER_COVER_OPEN', 'MAGNETIC_BYPASS_ATTEMPT']:
                simulation.trigger_disturbance()
                print(f"🚨 Critical alert triggered PID disturbance: {alert_type}")

def background_update(app):
    """Real-time data watcher loop with intelligent update batching"""
    update_counter = 0
    while True:
        time.sleep(1) 
        update_counter += 1
        
        with app.app_context():
            simulation.step()
            
            # Check for new data
            if reload_json_data():
                # Full re-initialization on data change
                initialize_data()
            elif update_counter % 10 == 0:
                # Periodic health score updates for active nodes (every 10 seconds)
                for node_id in list(db["meter_readings"].keys())[:3]:  # Update top 3
                    update_predictions_and_health(node_id)
