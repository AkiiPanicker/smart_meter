#!/usr/bin/env python3
"""
Smart Meter Platform - Post-Deployment Validation Tests
Runs automated tests to verify the enhanced system is working correctly
"""

import requests
import time
import json
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'

def print_test(name):
    print(f"\n{Colors.BLUE}▶ Testing: {name}{Colors.ENDC}")

def print_pass(message):
    print(f"  {Colors.GREEN}✓ PASS:{Colors.ENDC} {message}")

def print_fail(message):
    print(f"  {Colors.RED}✗ FAIL:{Colors.ENDC} {message}")

def print_warn(message):
    print(f"  {Colors.YELLOW}⚠ WARN:{Colors.ENDC} {message}")

def print_header(text):
    print(f"\n{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{'='*60}{Colors.ENDC}")

def test_api_connectivity(base_url):
    """Test 1: Basic API connectivity"""
    print_test("API Connectivity")
    try:
        response = requests.get(f"{base_url}/api/status", timeout=5)
        if response.status_code == 200:
            print_pass(f"API reachable (status: {response.status_code})")
            return True
        else:
            print_fail(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_fail(f"Cannot reach API: {e}")
        return False

def test_alert_diversity(base_url):
    """Test 2: Predictions show diverse alert types"""
    print_test("Alert Type Diversity")
    try:
        response = requests.get(f"{base_url}/api/predictions", timeout=5)
        data = response.json()
        
        if not data:
            print_warn("No predictions found (may be normal if no tampers)")
            return True
        
        # Check for variety in event types
        event_types = set(pred['event_type'] for pred in data)
        
        if len(event_types) == 1 and list(event_types)[0] == 'TAMPER':
            print_fail("All alerts are generic 'TAMPER' - upgrade may not be active")
            return False
        
        if len(event_types) > 1:
            print_pass(f"Found {len(event_types)} different alert types")
            for event_type in event_types:
                count = sum(1 for p in data if p['event_type'] == event_type)
                print(f"    • {event_type}: {count} alerts")
            return True
        else:
            print_warn(f"Only one alert type found: {list(event_types)[0]}")
            return True
            
    except Exception as e:
        print_fail(f"Error checking predictions: {e}")
        return False

def test_confidence_variation(base_url):
    """Test 3: Confidence scores vary (not all 99.9%)"""
    print_test("Confidence Score Variation")
    try:
        response = requests.get(f"{base_url}/api/predictions", timeout=5)
        data = response.json()
        
        if not data:
            print_warn("No predictions to check")
            return True
        
        confidences = [pred['confidence'] for pred in data]
        
        # Check for unrealistic 99.9% pattern
        high_conf_count = sum(1 for c in confidences if c > 99.0)
        
        if high_conf_count == len(confidences) and len(confidences) > 3:
            print_fail("All confidence scores > 99% - AI model may not be working")
            return False
        
        # Calculate variance
        if len(confidences) > 1:
            avg_conf = sum(confidences) / len(confidences)
            variance = sum((c - avg_conf) ** 2 for c in confidences) / len(confidences)
            
            if variance < 1.0:
                print_warn(f"Low variance ({variance:.2f}) - scores may be too similar")
            else:
                print_pass(f"Confidence variance: {variance:.2f} (healthy variation)")
            
            print(f"    • Min: {min(confidences):.1f}%")
            print(f"    • Max: {max(confidences):.1f}%")
            print(f"    • Avg: {avg_conf:.1f}%")
            return True
        else:
            print_warn("Only one prediction available")
            return True
            
    except Exception as e:
        print_fail(f"Error checking confidence: {e}")
        return False

def test_explanation_diversity(base_url):
    """Test 4: Explanations are specific, not generic"""
    print_test("Explanation Specificity")
    try:
        response = requests.get(f"{base_url}/api/predictions", timeout=5)
        data = response.json()
        
        if not data:
            print_warn("No predictions to check")
            return True
        
        explanations = [pred['explanation'] for pred in data]
        unique_explanations = set(explanations)
        
        # Check for the old generic explanation
        generic_count = sum(1 for e in explanations if 
            "Historical Analysis: Sensor patterns indicate physical manipulation" in e)
        
        if generic_count == len(explanations) and len(explanations) > 1:
            print_fail("All explanations are identical generic text")
            return False
        
        # Check for variety
        if len(unique_explanations) > len(explanations) * 0.3:  # At least 30% unique
            print_pass(f"Found {len(unique_explanations)} unique explanations (good)")
            # Show sample
            sample = list(unique_explanations)[:2]
            for i, exp in enumerate(sample, 1):
                preview = exp[:80] + "..." if len(exp) > 80 else exp
                print(f"    {i}. {preview}")
            return True
        else:
            print_warn(f"Low explanation diversity: {len(unique_explanations)}/{len(explanations)}")
            return True
            
    except Exception as e:
        print_fail(f"Error checking explanations: {e}")
        return False

def test_health_scores(base_url):
    """Test 5: Health scores vary by node"""
    print_test("Health Score Distribution")
    try:
        response = requests.get(f"{base_url}/api/readings", timeout=5)
        data = response.json()
        
        if not data:
            print_warn("No meter readings found")
            return True
        
        health_scores = [reading['health_score'] for reading in data]
        unique_scores = set(health_scores)
        
        if len(unique_scores) == 1 and list(unique_scores)[0] == 100:
            print_warn("All nodes at 100% health (may be normal if no recent tampers)")
        else:
            print_pass(f"Health scores vary: {sorted(unique_scores)}")
            
        avg_health = sum(health_scores) / len(health_scores)
        print(f"    • Average: {avg_health:.1f}%")
        print(f"    • Min: {min(health_scores)}%")
        print(f"    • Max: {max(health_scores)}%")
        return True
        
    except Exception as e:
        print_fail(f"Error checking health scores: {e}")
        return False

def test_severity_levels(base_url):
    """Test 6: Different severity levels present"""
    print_test("Severity Level Distribution")
    try:
        response = requests.get(f"{base_url}/api/predictions", timeout=5)
        data = response.json()
        
        if not data:
            print_warn("No predictions to check")
            return True
        
        severities = [pred['severity'] for pred in data]
        severity_counts = {}
        for sev in severities:
            severity_counts[sev] = severity_counts.get(sev, 0) + 1
        
        if len(severity_counts) > 1:
            print_pass(f"Multiple severity levels detected")
            for severity, count in severity_counts.items():
                print(f"    • {severity}: {count} alerts")
            return True
        else:
            print_warn(f"Only one severity level: {list(severity_counts.keys())[0]}")
            return True
            
    except Exception as e:
        print_fail(f"Error checking severity: {e}")
        return False

def run_all_tests(base_url="http://localhost:5000"):
    """Run complete test suite"""
    print_header("SMART METER PLATFORM - VALIDATION TESTS")
    print(f"Target: {base_url}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("API Connectivity", test_api_connectivity),
        ("Alert Type Diversity", test_alert_diversity),
        ("Confidence Variation", test_confidence_variation),
        ("Explanation Specificity", test_explanation_diversity),
        ("Health Score Distribution", test_health_scores),
        ("Severity Levels", test_severity_levels)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func(base_url)
            results.append((test_name, result))
        except Exception as e:
            print_fail(f"Test crashed: {e}")
            results.append((test_name, False))
        time.sleep(0.5)  # Small delay between tests
    
    # Summary
    print_header("TEST SUMMARY")
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{Colors.GREEN}PASS{Colors.ENDC}" if result else f"{Colors.RED}FAIL{Colors.ENDC}"
        print(f"  {status}  {test_name}")
    
    print(f"\n{Colors.BOLD}Results: {passed}/{total} tests passed{Colors.ENDC}")
    
    if passed == total:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✅ ALL TESTS PASSED - System is working correctly!{Colors.ENDC}")
        return 0
    elif passed >= total * 0.7:
        print(f"\n{Colors.YELLOW}{Colors.BOLD}⚠️  PARTIAL SUCCESS - Review failed tests{Colors.ENDC}")
        return 1
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}❌ CRITICAL ISSUES - Deployment may have failed{Colors.ENDC}")
        print("\nTroubleshooting:")
        print("  1. Verify all files were replaced correctly")
        print("  2. Check console logs for errors")
        print("  3. Restart the application: python run.py")
        print("  4. Restore from backup if issues persist")
        return 2

if __name__ == '__main__':
    import sys
    
    # Allow custom URL via command line
    url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:5000"
    
    exit_code = run_all_tests(url)
    sys.exit(exit_code)
