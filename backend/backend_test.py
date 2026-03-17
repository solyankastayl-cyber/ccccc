#!/usr/bin/env python3
"""
TA Engine API Testing - Timeframe Isolation

Tests for:
- Timeframe isolation with aggregated candles (1D, 7D, 30D, 180D)
- Proper candle count for each timeframe
- Pattern detection differences across timeframes
- Debug endpoint showing aggregation metrics
- Health check functionality
"""

import requests
import sys
import time
from datetime import datetime
from typing import Dict, List, Optional


class TAEngineAPITester:
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
            if method.upper() == "GET":
                response = requests.get(url, timeout=30)
            elif method.upper() == "POST":
                response = requests.post(url, json=data, timeout=30)
            else:
                return False, {}, 0
                
            return True, response.json() if response.text else {}, response.status_code
            
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}, 0
        except Exception as e:
            return False, {"error": str(e)}, 0

    # ═══════════════════════════════════════════════════════════════
    # Core Health Check Tests
    # ═══════════════════════════════════════════════════════════════

    def test_health_endpoint(self):
        """Test /api/health endpoint"""
        success, data, status = self.make_request("GET", "/api/health")
        
        if not success or status != 200:
            self.log_result("Health Endpoint", False, f"Request failed: status={status}")
            return False
            
        if not data.get("ok"):
            self.log_result("Health Endpoint", False, "Status not OK")
            return False
            
        # Check required fields
        required_fields = ["ok", "mode", "version", "timestamp"]
        for field in required_fields:
            if field not in data:
                self.log_result("Health Endpoint", False, f"Missing field: {field}")
                return False
        
        print(f"   💚 Mode: {data.get('mode')}")
        print(f"   💚 Version: {data.get('version')}")
        
        self.log_result("Health Endpoint", True)
        return True

    # ═══════════════════════════════════════════════════════════════
    # TA Setup API Tests - Timeframe Isolation
    # ═══════════════════════════════════════════════════════════════

    def test_ta_setup_1d_timeframe(self):
        """Test /api/ta/setup with 1D timeframe - should return ~2500 daily candles"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=BTC&tf=1D")
        
        if not success or status != 200:
            self.log_result("TA Setup 1D Timeframe", False, f"Request failed: status={status}, error: {data.get('error', 'unknown')}")
            return False
            
        # Check basic structure
        required_fields = ["symbol", "timeframe", "candles", "candle_count", "raw_daily_count"]
        for field in required_fields:
            if field not in data:
                self.log_result("TA Setup 1D Timeframe", False, f"Missing field: {field}")
                return False
        
        candle_count = data.get("candle_count", 0)
        raw_daily_count = data.get("raw_daily_count", 0)
        
        # For 1D, candles should be the same as raw daily count
        if candle_count != raw_daily_count:
            self.log_result("TA Setup 1D Timeframe", False, f"1D candles ({candle_count}) should equal raw daily ({raw_daily_count})")
            return False
            
        # Should have around 2500 daily candles (allow some tolerance)
        if not (2000 <= candle_count <= 3000):
            self.log_result("TA Setup 1D Timeframe", False, f"Expected ~2500 candles, got {candle_count}")
            return False
        
        print(f"   📈 1D candles: {candle_count}")
        print(f"   📈 Raw daily count: {raw_daily_count}")
        print(f"   📈 Pattern: {data.get('pattern', {}).get('type') if data.get('pattern') else 'None'}")
        
        self.log_result("TA Setup 1D Timeframe", True)
        return data

    def test_ta_setup_7d_timeframe(self):
        """Test /api/ta/setup with 7D timeframe - should return ~350 weekly candles"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=BTC&tf=7D")
        
        if not success or status != 200:
            self.log_result("TA Setup 7D Timeframe", False, f"Request failed: status={status}, error: {data.get('error', 'unknown')}")
            return False
            
        # Check basic structure
        required_fields = ["symbol", "timeframe", "candles", "candle_count", "raw_daily_count"]
        for field in required_fields:
            if field not in data:
                self.log_result("TA Setup 7D Timeframe", False, f"Missing field: {field}")
                return False
        
        candle_count = data.get("candle_count", 0)
        raw_daily_count = data.get("raw_daily_count", 0)
        
        # For 7D, aggregated candles should be much less than raw daily
        if candle_count >= raw_daily_count:
            self.log_result("TA Setup 7D Timeframe", False, f"7D aggregated candles ({candle_count}) should be less than raw daily ({raw_daily_count})")
            return False
            
        # Should have around 350 weekly candles (allow tolerance)
        if not (250 <= candle_count <= 450):
            self.log_result("TA Setup 7D Timeframe", False, f"Expected ~350 weekly candles, got {candle_count}")
            return False
        
        print(f"   📈 7D candles: {candle_count}")
        print(f"   📈 Raw daily count: {raw_daily_count}")
        print(f"   📈 Aggregation ratio: {raw_daily_count/candle_count:.1f}:1")
        print(f"   📈 Pattern: {data.get('pattern', {}).get('type') if data.get('pattern') else 'None'}")
        
        self.log_result("TA Setup 7D Timeframe", True)
        return data

    def test_ta_setup_30d_timeframe(self):
        """Test /api/ta/setup with 30D timeframe - should return ~80 monthly candles"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=BTC&tf=30D")
        
        if not success or status != 200:
            self.log_result("TA Setup 30D Timeframe", False, f"Request failed: status={status}, error: {data.get('error', 'unknown')}")
            return False
            
        # Check basic structure
        required_fields = ["symbol", "timeframe", "candles", "candle_count", "raw_daily_count"]
        for field in required_fields:
            if field not in data:
                self.log_result("TA Setup 30D Timeframe", False, f"Missing field: {field}")
                return False
        
        candle_count = data.get("candle_count", 0)
        raw_daily_count = data.get("raw_daily_count", 0)
        
        # For 30D, aggregated candles should be much less than raw daily
        if candle_count >= raw_daily_count:
            self.log_result("TA Setup 30D Timeframe", False, f"30D aggregated candles ({candle_count}) should be less than raw daily ({raw_daily_count})")
            return False
            
        # Should have around 80 monthly candles (allow tolerance)
        if not (60 <= candle_count <= 100):
            self.log_result("TA Setup 30D Timeframe", False, f"Expected ~80 monthly candles, got {candle_count}")
            return False
        
        print(f"   📈 30D candles: {candle_count}")
        print(f"   📈 Raw daily count: {raw_daily_count}")
        print(f"   📈 Aggregation ratio: {raw_daily_count/candle_count:.1f}:1")
        print(f"   📈 Pattern: {data.get('pattern', {}).get('type') if data.get('pattern') else 'None'}")
        
        self.log_result("TA Setup 30D Timeframe", True)
        return data

    def test_ta_setup_180d_timeframe(self):
        """Test /api/ta/setup with 180D timeframe - should return quarterly candles"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=BTC&tf=180D")
        
        if not success or status != 200:
            self.log_result("TA Setup 180D Timeframe", False, f"Request failed: status={status}, error: {data.get('error', 'unknown')}")
            return False
            
        # Check basic structure
        required_fields = ["symbol", "timeframe", "candles", "candle_count", "raw_daily_count"]
        for field in required_fields:
            if field not in data:
                self.log_result("TA Setup 180D Timeframe", False, f"Missing field: {field}")
                return False
        
        candle_count = data.get("candle_count", 0)
        raw_daily_count = data.get("raw_daily_count", 0)
        
        # For 180D, aggregated candles should be much less than raw daily
        if candle_count >= raw_daily_count:
            self.log_result("TA Setup 180D Timeframe", False, f"180D aggregated candles ({candle_count}) should be less than raw daily ({raw_daily_count})")
            return False
            
        # Should have quarterly candles (roughly 7 years / 4 = ~28 quarters, allow tolerance)
        if not (20 <= candle_count <= 40):
            self.log_result("TA Setup 180D Timeframe", False, f"Expected ~28 quarterly candles, got {candle_count}")
            return False
        
        print(f"   📈 180D candles: {candle_count}")
        print(f"   📈 Raw daily count: {raw_daily_count}")
        print(f"   📈 Aggregation ratio: {raw_daily_count/candle_count:.1f}:1")
        print(f"   📈 Pattern: {data.get('pattern', {}).get('type') if data.get('pattern') else 'None'}")
        
        self.log_result("TA Setup 180D Timeframe", True)
        return data

    def test_ta_debug_endpoint(self):
        """Test /api/ta/debug endpoint - should show aggregated vs raw counts"""
        success, data, status = self.make_request("GET", "/api/ta/debug?symbol=BTC&tf=7D")
        
        if not success or status != 200:
            self.log_result("TA Debug Endpoint", False, f"Request failed: status={status}, error: {data.get('error', 'unknown')}")
            return False
            
        # Check debug structure
        required_fields = ["symbol", "timeframe", "raw_daily_count", "aggregated_count"]
        for field in required_fields:
            if field not in data:
                self.log_result("TA Debug Endpoint", False, f"Missing field: {field}")
                return False
        
        raw_count = data.get("raw_daily_count", 0)
        aggregated_count = data.get("aggregated_count", 0)
        
        # Debug endpoint should show proper aggregation
        if aggregated_count >= raw_count:
            self.log_result("TA Debug Endpoint", False, f"Aggregated count ({aggregated_count}) should be less than raw ({raw_count})")
            return False
        
        print(f"   🔍 Symbol: {data.get('symbol')}")
        print(f"   🔍 Timeframe: {data.get('timeframe')}")
        print(f"   🔍 Raw daily count: {raw_count}")
        print(f"   🔍 Aggregated count: {aggregated_count}")
        print(f"   🔍 Pivot highs: {data.get('pivot_highs', 0)}")
        print(f"   🔍 Pivot lows: {data.get('pivot_lows', 0)}")
        print(f"   🔍 Pattern window: {data.get('pattern_window', 'N/A')}")
        print(f"   🔍 Pivot window: {data.get('pivot_window', 'N/A')}")
        
        self.log_result("TA Debug Endpoint", True)
        return data

    def test_timeframe_pattern_differences(self):
        """Test that different timeframes can produce different patterns"""
        print("   🔄 Testing pattern differences across timeframes...")
        
        timeframes = ["1D", "7D", "30D", "180D"]
        patterns = {}
        
        for tf in timeframes:
            success, data, status = self.make_request("GET", f"/api/ta/setup?symbol=BTC&tf={tf}")
            
            if not success or status != 200:
                self.log_result("Timeframe Pattern Differences", False, f"Failed to get {tf} data: status={status}")
                return False
            
            pattern = data.get("pattern")
            pattern_type = pattern.get("type") if pattern else None
            patterns[tf] = pattern_type
            
            print(f"   📊 {tf}: {pattern_type or 'None'}")
        
        # Check that we have valid responses for all timeframes
        if len(patterns) != len(timeframes):
            self.log_result("Timeframe Pattern Differences", False, f"Expected {len(timeframes)} timeframes, got {len(patterns)}")
            return False
        
        # It's OK if patterns are the same or different - the test is that the system handles different TFs
        unique_patterns = set(patterns.values())
        print(f"   🎯 Unique patterns found: {len(unique_patterns)}")
        
        self.log_result("Timeframe Pattern Differences", True)
        return patterns

    # ═══════════════════════════════════════════════════════════════
    # Test Runner
    # ═══════════════════════════════════════════════════════════════

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting TA Engine API Tests - Timeframe Isolation...")
        print(f"🌐 Base URL: {self.base_url}")
        print("=" * 80)
        
        # Health check
        print("\n🔧 HEALTH CHECK")
        print("-" * 50)
        self.test_health_endpoint()
        
        # Timeframe isolation tests
        print("\n📊 TIMEFRAME ISOLATION TESTS")
        print("-" * 50)
        
        self.test_ta_setup_1d_timeframe()
        self.test_ta_setup_7d_timeframe()
        self.test_ta_setup_30d_timeframe()
        self.test_ta_setup_180d_timeframe()
        
        # Debug endpoint test
        print("\n🔍 DEBUG ENDPOINT TEST")
        print("-" * 50)
        self.test_ta_debug_endpoint()
        
        # Pattern difference test
        print("\n🎯 PATTERN DIFFERENCE TEST")
        print("-" * 50)
        self.test_timeframe_pattern_differences()
        
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
    print("TA Engine API Tester - Timeframe Isolation")
    print("=" * 80)
    
    # Initialize tester
    tester = TAEngineAPITester()
    
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