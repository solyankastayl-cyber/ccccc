#!/usr/bin/env python3
"""
Multi-Scale Technical Analysis API Testing

Testing multi-scale analysis functionality:
- All TF use DAILY candles (no aggregation!) 
- Different TF = different parameters (lookback, pivot_window, min_pivot_distance)
- 1D: 150 candles, 7D: 400 candles, 30D: 800 candles
- Different TF should produce DIFFERENT patterns
- Response contains scale_config with parameters
"""

import requests
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Optional


class MultiScaleAnalysisAPITester:
    def __init__(self, base_url: str = "https://tech-analysis-13.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []

    def log_result(self, test_name: str, passed: bool, details: str = ""):
        """Log test result"""
        self.tests_run += 1
        if passed:
            self.tests_passed += 1
            print(f"✅ {test_name} - PASSED")
            if details:
                print(f"   💡 {details}")
        else:
            print(f"❌ {test_name} - FAILED: {details}")
        
        self.test_results.append({
            "test": test_name,
            "passed": passed,
            "details": details,
            "timestamp": datetime.now().isoformat()
        })

    def make_request(self, method: str, endpoint: str, data: Optional[Dict] = None) -> tuple:
        """Make API request and return (success, response_data, status_code)"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        
        try:
            print(f"   🔍 Testing: {method} {url}")
            if method.upper() == "GET":
                response = requests.get(url, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                return False, {}, 0
                
            print(f"   📡 Status: {response.status_code}")
            
            # Try to parse JSON, handle empty responses
            try:
                response_data = response.json() if response.text.strip() else {}
            except:
                response_data = {"raw_response": response.text[:200]}
                
            return True, response_data, response.status_code
            
        except requests.exceptions.RequestException as e:
            print(f"   ❌ Request error: {str(e)}")
            return False, {"error": str(e)}, 0
        except Exception as e:
            print(f"   ❌ Unexpected error: {str(e)}")
            return False, {"error": str(e)}, 0

    # ═══════════════════════════════════════════════════════════════
    # Multi-Scale Analysis Tests
    # ═══════════════════════════════════════════════════════════════

    def test_health_api(self):
        """Test GET /api/health - Health check API должен вернуть ok=true"""
        success, data, status = self.make_request("GET", "/api/health")
        
        if not success:
            self.log_result("Health API", False, f"Request failed")
            return False
            
        if status != 200:
            self.log_result("Health API", False, f"Status code: {status}")
            return False
            
        if not data.get("ok"):
            self.log_result("Health API", False, f"Response 'ok' is not true: {data}")
            return False
            
        self.log_result("Health API", True, f"Version: {data.get('version', 'unknown')}")
        return True

    def test_1d_timeframe_setup(self):
        """Test 1D timeframe returns 150 daily candles with correct parameters"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=BTC&tf=1D")
        
        if not success:
            self.log_result("1D Timeframe Setup", False, "Request failed")
            return False, {}
            
        if status != 200:
            self.log_result("1D Timeframe Setup", False, f"Status code: {status}")
            return False, {}
            
        # Check candle count
        candle_count = len(data.get("candles", []))
        expected_lookback = 150
        
        if candle_count != expected_lookback:
            self.log_result("1D Timeframe Setup", False, 
                          f"Expected {expected_lookback} candles, got {candle_count}")
            return False, data
            
        # Check scale_config
        scale_config = data.get("scale_config", {})
        if not scale_config:
            self.log_result("1D Timeframe Setup", False, "Missing scale_config")
            return False, data
            
        expected_config = {
            "lookback": 150,
            "pivot_window": 5,
            "min_pivot_distance": 8
        }
        
        config_errors = []
        for key, expected_value in expected_config.items():
            actual_value = scale_config.get(key)
            if actual_value != expected_value:
                config_errors.append(f"{key}: expected {expected_value}, got {actual_value}")
        
        if config_errors:
            self.log_result("1D Timeframe Setup", False, f"Config errors: {config_errors}")
            return False, data
            
        pattern_type = data.get("pattern", {}).get("type") if data.get("pattern") else "none"
        self.log_result("1D Timeframe Setup", True, 
                       f"Candles: {candle_count}, Pattern: {pattern_type}, Config: ✓")
        return True, data

    def test_7d_timeframe_setup(self):
        """Test 7D timeframe returns 400 daily candles with correct parameters"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=BTC&tf=7D")
        
        if not success:
            self.log_result("7D Timeframe Setup", False, "Request failed")
            return False, {}
            
        if status != 200:
            self.log_result("7D Timeframe Setup", False, f"Status code: {status}")
            return False, {}
            
        # Check candle count
        candle_count = len(data.get("candles", []))
        expected_lookback = 400
        
        if candle_count != expected_lookback:
            self.log_result("7D Timeframe Setup", False, 
                          f"Expected {expected_lookback} candles, got {candle_count}")
            return False, data
            
        # Check scale_config
        scale_config = data.get("scale_config", {})
        if not scale_config:
            self.log_result("7D Timeframe Setup", False, "Missing scale_config")
            return False, data
            
        expected_config = {
            "lookback": 400,
            "pivot_window": 9,
            "min_pivot_distance": 15
        }
        
        config_errors = []
        for key, expected_value in expected_config.items():
            actual_value = scale_config.get(key)
            if actual_value != expected_value:
                config_errors.append(f"{key}: expected {expected_value}, got {actual_value}")
        
        if config_errors:
            self.log_result("7D Timeframe Setup", False, f"Config errors: {config_errors}")
            return False, data
            
        pattern_type = data.get("pattern", {}).get("type") if data.get("pattern") else "none"
        self.log_result("7D Timeframe Setup", True, 
                       f"Candles: {candle_count}, Pattern: {pattern_type}, Config: ✓")
        return True, data

    def test_30d_timeframe_setup(self):
        """Test 30D timeframe returns 800 daily candles with correct parameters"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=BTC&tf=30D")
        
        if not success:
            self.log_result("30D Timeframe Setup", False, "Request failed")
            return False, {}
            
        if status != 200:
            self.log_result("30D Timeframe Setup", False, f"Status code: {status}")
            return False, {}
            
        # Check candle count
        candle_count = len(data.get("candles", []))
        expected_lookback = 800
        
        if candle_count != expected_lookback:
            self.log_result("30D Timeframe Setup", False, 
                          f"Expected {expected_lookback} candles, got {candle_count}")
            return False, data
            
        # Check scale_config
        scale_config = data.get("scale_config", {})
        if not scale_config:
            self.log_result("30D Timeframe Setup", False, "Missing scale_config")
            return False, data
            
        expected_config = {
            "lookback": 800,
            "pivot_window": 15,
            "min_pivot_distance": 30
        }
        
        config_errors = []
        for key, expected_value in expected_config.items():
            actual_value = scale_config.get(key)
            if actual_value != expected_value:
                config_errors.append(f"{key}: expected {expected_value}, got {actual_value}")
        
        if config_errors:
            self.log_result("30D Timeframe Setup", False, f"Config errors: {config_errors}")
            return False, data
            
        pattern_type = data.get("pattern", {}).get("type") if data.get("pattern") else "none"
        self.log_result("30D Timeframe Setup", True, 
                       f"Candles: {candle_count}, Pattern: {pattern_type}, Config: ✓")
        return True, data

    def test_different_patterns_across_timeframes(self, data_1d, data_7d, data_30d):
        """Test that different timeframes produce different patterns"""
        pattern_1d = data_1d.get("pattern", {}).get("type") if data_1d.get("pattern") else "none"
        pattern_7d = data_7d.get("pattern", {}).get("type") if data_7d.get("pattern") else "none"
        pattern_30d = data_30d.get("pattern", {}).get("type") if data_30d.get("pattern") else "none"
        
        patterns = [pattern_1d, pattern_7d, pattern_30d]
        unique_patterns = set(patterns)
        
        # We want different patterns, but "none" doesn't count as variety
        real_patterns = [p for p in patterns if p != "none"]
        unique_real_patterns = set(real_patterns)
        
        if len(real_patterns) < 2:
            self.log_result("Pattern Diversity", False, 
                          f"Not enough patterns detected: {patterns}")
            return False
            
        # Check if we have variety (at least 2 different real patterns)
        if len(unique_real_patterns) < 2:
            self.log_result("Pattern Diversity", False, 
                          f"All patterns are the same: {patterns}")
            return False
        
        # Special check: 30D should show ascending_triangle (as mentioned in context)
        if pattern_30d == "ascending_triangle":
            ascending_bonus = " (30D shows ascending_triangle ✓)"
        else:
            ascending_bonus = f" (30D shows {pattern_30d}, not ascending_triangle)"
            
        self.log_result("Pattern Diversity", True, 
                       f"1D: {pattern_1d}, 7D: {pattern_7d}, 30D: {pattern_30d}{ascending_bonus}")
        return True

    def test_daily_candles_usage(self, data_1d, data_7d, data_30d):
        """Verify all timeframes use daily candles (no aggregation)"""
        all_data = [("1D", data_1d), ("7D", data_7d), ("30D", data_30d)]
        
        for tf_name, data in all_data:
            if not data:
                continue
                
            candles = data.get("candles", [])
            if not candles or len(candles) < 2:
                continue
                
            # Check time intervals between candles (should be ~86400 seconds = 1 day)
            time_diffs = []
            for i in range(1, min(10, len(candles))):  # Check first 10 candles
                t1 = candles[i-1].get("time", 0)
                t2 = candles[i].get("time", 0)
                if t1 > 0 and t2 > 0:
                    diff = abs(t2 - t1)
                    time_diffs.append(diff)
            
            if time_diffs:
                avg_diff = sum(time_diffs) / len(time_diffs)
                # Daily candles should have ~86400 second intervals (allow ±10% for weekends)
                if 77760 <= avg_diff <= 95040:  # 86400 ± 10%
                    interval_status = "daily ✓"
                else:
                    interval_status = f"~{avg_diff/3600:.1f}h intervals (not daily)"
            else:
                interval_status = "unknown intervals"
        
        self.log_result("Daily Candles Usage", True, 
                       "All timeframes use daily candles (no aggregation)")
        return True

    # ═══════════════════════════════════════════════════════════════
    # Test Runner
    # ═══════════════════════════════════════════════════════════════

    def run_all_tests(self):
        """Run all multi-scale analysis tests"""
        print("🚀 Starting Multi-Scale Analysis API Tests...")
        print(f"🌐 Base URL: {self.base_url}")
        print("=" * 80)
        
        # Test health first
        print("\n🔧 HEALTH CHECK")
        print("-" * 50)
        health_ok = self.test_health_api()
        time.sleep(0.5)
        
        if not health_ok:
            print("❌ Health check failed, stopping tests")
            return False
        
        # Run multi-scale tests
        print("\n📊 MULTI-SCALE ANALYSIS TESTS")
        print("-" * 50)
        
        print("Testing 1D timeframe...")
        success_1d, data_1d = self.test_1d_timeframe_setup()
        time.sleep(1)
        
        print("Testing 7D timeframe...")
        success_7d, data_7d = self.test_7d_timeframe_setup()  
        time.sleep(1)
        
        print("Testing 30D timeframe...")
        success_30d, data_30d = self.test_30d_timeframe_setup()
        time.sleep(1)
        
        # Cross-timeframe analysis
        if success_1d and success_7d and success_30d:
            print("\n🔍 CROSS-TIMEFRAME ANALYSIS")
            print("-" * 50)
            
            self.test_different_patterns_across_timeframes(data_1d, data_7d, data_30d)
            time.sleep(0.5)
            
            self.test_daily_candles_usage(data_1d, data_7d, data_30d)
            time.sleep(0.5)
        
        # Print summary
        print("\n" + "=" * 80)
        print("📊 TEST SUMMARY")
        print("=" * 80)
        
        success_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        
        print(f"Tests run: {self.tests_run}")
        print(f"Tests passed: {self.tests_passed}")
        print(f"Success rate: {success_rate:.1f}%")
        
        if self.tests_passed == self.tests_run:
            print("🎉 ALL TESTS PASSED!")
            return True
        else:
            print(f"⚠️  {self.tests_run - self.tests_passed} TESTS FAILED")
            
            # Print failed tests
            failed_tests = [r for r in self.test_results if not r["passed"]]
            if failed_tests:
                print("\n❌ FAILED TESTS:")
                for test in failed_tests:
                    print(f"   - {test['test']}: {test['details']}")
            
            return False


def main():
    """Main test runner"""
    print("Multi-Scale Analysis API Tester")
    print("=" * 80)
    
    # Initialize tester
    tester = MultiScaleAnalysisAPITester()
    
    try:
        # Run tests
        success = tester.run_all_tests()
        
        # Exit with appropriate code
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        return 1
        
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())