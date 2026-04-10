"""
Advanced Analytics & Recommendations Engine
Production-grade insights for smart meter platform
"""

from collections import defaultdict, Counter
from datetime import datetime, timedelta
import json
import numpy as np

class AnalyticsEngine:
    """
    Provides actionable insights and recommendations
    """
    
    def __init__(self, db):
        self.db = db
    
    def get_alert_distribution_analysis(self):
        """
        Analyze alert distribution to detect systematic issues
        """
        predictions = self.db.get('predictions', [])
        
        if not predictions:
            return {
                'status': 'insufficient_data',
                'message': 'No alerts to analyze yet.'
            }
        
        # Count by type
        type_counts = Counter(p.event_type for p in predictions)
        total = len(predictions)
        
        analysis = {
            'total_alerts': total,
            'distribution': dict(type_counts),
            'insights': [],
            'recommendations': []
        }
        
        # Detect concerning patterns
        for alert_type, count in type_counts.items():
            percentage = (count / total) * 100
            
            # If one type dominates (>70%), investigate
            if percentage > 70:
                analysis['insights'].append({
                    'severity': 'high',
                    'title': f'Alert Concentration: {alert_type}',
                    'description': f'{percentage:.0f}% of all alerts are "{alert_type}". This may indicate:',
                    'possibilities': [
                        'Systematic tampering pattern',
                        'Sensor miscalibration',
                        'Environmental factor affecting multiple meters',
                        'Classification threshold needs tuning'
                    ]
                })
                
                # Type-specific recommendations
                if 'Magnetic' in alert_type:
                    analysis['recommendations'].append({
                        'priority': 'high',
                        'action': 'Review magnetic tamper thresholds',
                        'details': 'Current threshold may be too sensitive. Consider increasing the required current drop delta or adding temporal validation.'
                    })
                elif 'Physical Access' in alert_type or 'Cover' in alert_type:
                    analysis['recommendations'].append({
                        'priority': 'critical',
                        'action': 'Immediate field inspection recommended',
                        'details': 'Multiple physical access alerts suggest ongoing tampering campaign.'
                    })
        
        return analysis
    
    def get_node_health_trends(self, hours=24):
        """
        Analyze health trends per node
        """
        meter_readings = self.db.get('meter_readings', {})
        predictions = self.db.get('predictions', [])
        
        node_analysis = {}
        
        for node_id, reading in meter_readings.items():
            # Get alerts for this node
            node_alerts = [p for p in predictions if p.node_id == node_id]
            
            analysis = {
                'current_health': reading.health_score,
                'total_alerts': len(node_alerts),
                'alert_types': list(set(p.event_type for p in node_alerts)),
                'risk_level': 'low',
                'recommendation': 'Continue monitoring'
            }
            
            # Risk assessment
            if len(node_alerts) > 10:
                analysis['risk_level'] = 'critical'
                analysis['recommendation'] = 'URGENT: Schedule immediate field inspection'
            elif len(node_alerts) > 5:
                analysis['risk_level'] = 'high'
                analysis['recommendation'] = 'Schedule inspection within 48 hours'
            elif len(node_alerts) > 2:
                analysis['risk_level'] = 'medium'
                analysis['recommendation'] = 'Monitor closely, inspect within 1 week'
            
            node_analysis[node_id] = analysis
        
        return node_analysis
    
    def get_temporal_patterns(self):
        """
        Detect time-based tampering patterns
        """
        predictions = self.db.get('predictions', [])
        
        if len(predictions) < 10:
            return {'status': 'insufficient_data'}
        
        # Group by hour of day
        hourly_counts = defaultdict(int)
        for pred in predictions:
            try:
                ts = datetime.fromisoformat(pred.timestamp.replace('Z', '+00:00'))
                hour = ts.hour
                hourly_counts[hour] += 1
            except:
                continue
        
        # Detect suspicious time windows
        if hourly_counts:
            max_hour = max(hourly_counts.items(), key=lambda x: x[1])
            avg_count = sum(hourly_counts.values()) / 24
            
            insights = []
            if max_hour[1] > avg_count * 3:
                insights.append({
                    'pattern': 'Time-concentrated alerts',
                    'peak_hour': f"{max_hour[0]:02d}:00",
                    'count': max_hour[1],
                    'significance': 'Tampering may be occurring during specific time windows',
                    'recommendation': 'Consider increased monitoring or automated responses during this time'
                })
            
            return {
                'hourly_distribution': dict(hourly_counts),
                'insights': insights
            }
        
        return {'status': 'no_patterns_detected'}
    
    def get_configuration_recommendations(self):
        """
        Provide configuration tuning recommendations based on observed data
        """
        predictions = self.db.get('predictions', [])
        readings = list(self.db.get('meter_readings', {}).values())
        
        recommendations = []
        
        # Analyze confidence score distribution
        if predictions:
            confidences = [p.confidence for p in predictions]
            avg_conf = sum(confidences) / len(confidences)
            std_conf = np.std(confidences)
            
            if std_conf < 5:
                recommendations.append({
                    'category': 'Classification',
                    'issue': 'Low confidence variance',
                    'current_value': f'σ = {std_conf:.1f}',
                    'suggested_action': 'Increase diversity by adjusting alert thresholds or enabling diversity boost feature',
                    'config_change': 'Set _diversity_boost = True in AlertClassifier'
                })
            
            if avg_conf > 90:
                recommendations.append({
                    'category': 'Classification',
                    'issue': 'Overconfident predictions',
                    'current_value': f'avg = {avg_conf:.1f}%',
                    'suggested_action': 'Reduce confidence ranges in ALERT_CONFIG to more realistic levels',
                    'config_change': 'Lower confidence_range upper bounds by 5-10%'
                })
        
        # Analyze sensor baselines
        if readings:
            voltages = [r.voltage for r in readings]
            currents = [r.current for r in readings]
            lights = [r.light for r in readings]
            
            # Check light intensity
            avg_light = sum(lights) / len(lights)
            if avg_light < 200:
                recommendations.append({
                    'category': 'Sensor Calibration',
                    'issue': 'Low ambient light baseline',
                    'current_value': f'{avg_light:.0f} lux',
                    'suggested_action': 'Your meters operate in low-light environment. Light spike thresholds have been auto-calibrated, but verify physical installation.',
                    'config_change': 'Baselines auto-learned - no manual change needed'
                })
        
        return recommendations


class RealtimeMonitor:
    """
    Real-time monitoring and alerting
    """
    
    def __init__(self):
        self.alert_history = []
        self.notification_thresholds = {
            'critical_alerts_per_hour': 5,
            'high_alerts_per_node': 3,
            'health_drop_threshold': 30  # % drop
        }
    
    def should_trigger_notification(self, new_prediction, db):
        """
        Determine if this prediction warrants immediate notification
        """
        triggers = []
        
        # Critical severity
        if new_prediction.severity == 'high' and new_prediction.confidence > 85:
            triggers.append({
                'type': 'HIGH_CONFIDENCE_CRITICAL',
                'message': f'High-confidence critical alert on {new_prediction.node_id}',
                'urgency': 'immediate'
            })
        
        # Rapid succession alerts (same node)
        recent_for_node = [p for p in db.get('predictions', [])[:10] 
                          if p.node_id == new_prediction.node_id]
        if len(recent_for_node) >= 3:
            triggers.append({
                'type': 'RAPID_ALERTS',
                'message': f'{len(recent_for_node)} alerts in quick succession on {new_prediction.node_id}',
                'urgency': 'high'
            })
        
        # Multi-sensor tamper
        if 'Multi-Sensor' in new_prediction.event_type or 'Critical' in new_prediction.event_type:
            triggers.append({
                'type': 'COORDINATED_ATTACK',
                'message': 'Coordinated tampering attempt detected',
                'urgency': 'critical'
            })
        
        return triggers


def generate_executive_summary(db):
    """
    Generate executive-level summary for dashboard
    """
    predictions = db.get('predictions', [])
    readings = db.get('meter_readings', {})
    
    # Overall system health
    if readings:
        avg_health = sum(r.health_score for r in readings.values()) / len(readings)
        tampered_count = sum(1 for r in readings.values() if r.event_type == 'TAMPER')
    else:
        avg_health = 100
        tampered_count = 0
    
    # Alert severity breakdown
    severity_counts = Counter(p.severity for p in predictions)
    
    # Recent trend (last 10 vs previous 10)
    if len(predictions) >= 20:
        recent_critical = sum(1 for p in predictions[:10] if p.severity == 'high')
        previous_critical = sum(1 for p in predictions[10:20] if p.severity == 'high')
        trend = 'increasing' if recent_critical > previous_critical else 'decreasing'
    else:
        trend = 'stable'
    
    summary = {
        'overall_status': 'healthy' if avg_health > 80 else 'at_risk' if avg_health > 50 else 'critical',
        'average_health': round(avg_health, 1),
        'active_tampers': tampered_count,
        'total_alerts_24h': len(predictions),
        'critical_alerts': severity_counts.get('high', 0),
        'trend': trend,
        'top_priority_actions': []
    }
    
    # Priority actions
    if tampered_count > 0:
        summary['top_priority_actions'].append(
            f'Inspect {tampered_count} nodes currently showing tamper indicators'
        )
    
    if severity_counts.get('high', 0) > 3:
        summary['top_priority_actions'].append(
            'Review and respond to critical alerts requiring field inspection'
        )
    
    if avg_health < 70:
        summary['top_priority_actions'].append(
            'System health declining - investigate recurring tamper patterns'
        )
    
    return summary
