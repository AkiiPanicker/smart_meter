from flask import Blueprint, jsonify, render_template, request
from . import db, initialize_data
from app.pid_controller import simulation
from app.utils import convert_json_to_meter_reading

# Import analytics (create this file in your app/)
try:
    from app.analytics import AnalyticsEngine, RealtimeMonitor, generate_executive_summary
    ANALYTICS_ENABLED = True
except:
    ANALYTICS_ENABLED = False
    print("⚠️  Analytics module not found - advanced features disabled")

bp = Blueprint('api', __name__)

# Existing routes
@bp.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@bp.route('/api/status', methods=['GET'])
def get_status():
    readings = list(db["meter_readings"].values())
    if not readings:
        return jsonify({
            "total_nodes": 0, "tampered_nodes": 0, "avg_confidence": 0, "verified_ratio": 0,
        })
    tampered_nodes = sum(1 for r in readings if r.event_type == 'TAMPER')
    avg_confidence = sum(r.confidence for r in readings) / len(readings) if readings else 0
    verified_ratio = (sum(1 for r in readings if r.verified) / len(readings)) * 100 if readings else 0
    
    return jsonify({
        "total_nodes": len(readings), 
        "tampered_nodes": tampered_nodes,
        "avg_confidence": round(avg_confidence, 1), 
        "verified_ratio": round(verified_ratio, 1),
    })

@bp.route('/api/readings', methods=['GET'])
def get_readings():
    readings_list = [reading.__dict__ for reading in db["meter_readings"].values()]
    readings_list.sort(key=lambda x: x['node_id'])
    return jsonify(readings_list)

@bp.route('/api/logs', methods=['GET'])
def get_logs():
    raw_data = db["json_data"]
    recent = raw_data[-200:][::-1]
    formatted = [convert_json_to_meter_reading(x).__dict__ for x in recent]
    return jsonify(formatted)

@bp.route('/api/predictions', methods=['GET'])
def get_predictions():
    predictions_list = [pred.__dict__ for pred in db["predictions"]]
    return jsonify(predictions_list)

@bp.route('/api/pid_data', methods=['GET'])
def get_pid_data():
    return jsonify(simulation.get_history())

@bp.route('/api/simulate', methods=['POST'])
def simulate_new_data():
    initialize_data()
    return jsonify({"message": "OK"}), 200


# ============================================================================
# NEW ENHANCED ANALYTICS ENDPOINTS
# ============================================================================

@bp.route('/api/analytics/summary', methods=['GET'])
def get_executive_summary():
    """
    Executive dashboard summary
    GET /api/analytics/summary
    """
    if not ANALYTICS_ENABLED:
        return jsonify({"error": "Analytics not enabled"}), 501
    
    summary = generate_executive_summary(db)
    return jsonify(summary)


@bp.route('/api/analytics/distribution', methods=['GET'])
def get_alert_distribution():
    """
    Alert distribution analysis
    GET /api/analytics/distribution
    """
    if not ANALYTICS_ENABLED:
        return jsonify({"error": "Analytics not enabled"}), 501
    
    engine = AnalyticsEngine(db)
    analysis = engine.get_alert_distribution_analysis()
    return jsonify(analysis)


@bp.route('/api/analytics/node-health', methods=['GET'])
def get_node_health_analysis():
    """
    Per-node health trends and recommendations
    GET /api/analytics/node-health
    """
    if not ANALYTICS_ENABLED:
        return jsonify({"error": "Analytics not enabled"}), 501
    
    engine = AnalyticsEngine(db)
    analysis = engine.get_node_health_trends()
    return jsonify(analysis)


@bp.route('/api/analytics/temporal', methods=['GET'])
def get_temporal_patterns():
    """
    Time-based tampering pattern detection
    GET /api/analytics/temporal
    """
    if not ANALYTICS_ENABLED:
        return jsonify({"error": "Analytics not enabled"}), 501
    
    engine = AnalyticsEngine(db)
    patterns = engine.get_temporal_patterns()
    return jsonify(patterns)


@bp.route('/api/analytics/recommendations', methods=['GET'])
def get_config_recommendations():
    """
    Configuration tuning recommendations
    GET /api/analytics/recommendations
    """
    if not ANALYTICS_ENABLED:
        return jsonify({"error": "Analytics not enabled"}), 501
    
    engine = AnalyticsEngine(db)
    recommendations = engine.get_configuration_recommendations()
    return jsonify(recommendations)


@bp.route('/api/analytics/stats', methods=['GET'])
def get_system_stats():
    """
    Comprehensive system statistics
    GET /api/analytics/stats
    """
    stats = {
        'data': {
            'total_records': len(db.get('json_data', [])),
            'total_nodes': len(db.get('meter_readings', {})),
            'total_predictions': len(db.get('predictions', [])),
            'last_processed_index': db.get('last_processed_index', 0)
        },
        'alert_stats': db.get('alert_stats', {})
    }
    
    # Add alert type breakdown
    predictions = db.get('predictions', [])
    if predictions:
        from collections import Counter
        type_counts = Counter(p.event_type for p in predictions)
        stats['alert_breakdown'] = dict(type_counts)
        
        severity_counts = Counter(p.severity for p in predictions)
        stats['severity_breakdown'] = dict(severity_counts)
        
        # Confidence distribution
        confidences = [p.confidence for p in predictions]
        stats['confidence_stats'] = {
            'min': min(confidences),
            'max': max(confidences),
            'avg': sum(confidences) / len(confidences),
            'median': sorted(confidences)[len(confidences)//2]
        }
    
    return jsonify(stats)


@bp.route('/api/export/alerts', methods=['GET'])
def export_alerts_csv():
    """
    Export alerts as CSV
    GET /api/export/alerts?format=csv&days=7
    """
    from datetime import datetime, timedelta
    import io
    import csv
    
    days = request.args.get('days', 7, type=int)
    cutoff = datetime.now() - timedelta(days=days)
    
    predictions = db.get('predictions', [])
    
    # Filter by date
    filtered = []
    for pred in predictions:
        try:
            ts = datetime.fromisoformat(pred.timestamp.replace('Z', '+00:00'))
            if ts >= cutoff:
                filtered.append(pred)
        except:
            continue
    
    # Create CSV
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(['Timestamp', 'Node ID', 'Event Type', 'Confidence', 'Severity', 'Explanation'])
    
    for pred in filtered:
        writer.writerow([
            pred.timestamp,
            pred.node_id,
            pred.event_type,
            f"{pred.confidence:.1f}%",
            pred.severity,
            pred.explanation
        ])
    
    from flask import Response
    return Response(
        output.getvalue(),
        mimetype='text/csv',
        headers={'Content-Disposition': f'attachment; filename=alerts_{days}days.csv'}
    )


@bp.route('/api/health-check', methods=['GET'])
def health_check():
    """
    System health check endpoint
    GET /api/health-check
    """
    from datetime import datetime
    
    health = {
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'components': {
            'database': 'ok' if db.get('json_data') else 'no_data',
            'ai_model': 'ok',  # Could check if model is loaded
            'pid_simulation': 'ok',
            'analytics': 'ok' if ANALYTICS_ENABLED else 'disabled'
        },
        'metrics': {
            'total_nodes': len(db.get('meter_readings', {})),
            'active_alerts': len([p for p in db.get('predictions', []) if p.severity == 'high']),
            'system_uptime': 'available',  # Could track actual uptime
        }
    }
    
    # Determine overall status
    if health['components']['database'] == 'no_data':
        health['status'] = 'degraded'
    
    return jsonify(health)
