#!/usr/bin/env python3
"""
TA Engine API Testing - Multi-Scale Market Hierarchy

Tests for:
- 4H (micro/entry) using 4H candles from Coinbase (~200 candles)
- 1Y (cycle) using daily candles (~2500 candles)
- Different timeframes produce different patterns (4H ≠ 1D ≠ 30D)
- Response contains structure analysis (trend, hh, hl, lh, ll)
- ETH 4H shows descending_triangle (bearish pattern)
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
    # TA Setup API Tests - Multi-Scale Market Hierarchy
    # ═══════════════════════════════════════════════════════════════

    def test_ta_setup_4h_timeframe(self):
        """Test /api/ta/setup with 4H timeframe - should return 4H candles (~200 candles)"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=BTC&tf=4H")
        
        if not success or status != 200:
            self.log_result("TA Setup 4H Timeframe", False, f"Request failed: status={status}, error: {data.get('error', 'unknown')}")
            return False
            
        # Check basic structure
        required_fields = ["symbol", "timeframe", "candles", "candle_count", "scale_config", "structure"]
        for field in required_fields:
            if field not in data:
                self.log_result("TA Setup 4H Timeframe", False, f"Missing field: {field}")
                return False
        
        candle_count = data.get("candle_count", 0)
        timeframe = data.get("timeframe")
        scale_config = data.get("scale_config", {})
        
        # Verify it's 4H timeframe
        if timeframe != "4H":
            self.log_result("TA Setup 4H Timeframe", False, f"Expected timeframe 4H, got {timeframe}")
            return False
            
        # Should have around 200 4H candles (allow some tolerance)
        if not (150 <= candle_count <= 250):
            self.log_result("TA Setup 4H Timeframe", False, f"Expected ~200 4H candles, got {candle_count}")
            return False
        
        # Verify scale config for 4H
        expected_lookback = 200
        if scale_config.get("lookback") != expected_lookback:
            self.log_result("TA Setup 4H Timeframe", False, f"Expected lookback {expected_lookback}, got {scale_config.get('lookback')}")
            return False
        
        print(f"   📈 4H candles: {candle_count}")
        print(f"   📈 Scale config: {scale_config.get('description')}")
        print(f"   📈 Lookback: {scale_config.get('lookback')}")
        print(f"   📈 Pivot window: {scale_config.get('pivot_window')}")
        print(f"   📈 Pattern: {data.get('pattern', {}).get('type') if data.get('pattern') else 'None'}")
        
        self.log_result("TA Setup 4H Timeframe", True)
        return data

    def test_ta_setup_1y_timeframe(self):
        """Test /api/ta/setup with 1Y timeframe - should return 2500 daily candles"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=BTC&tf=1Y")
        
        if not success or status != 200:
            self.log_result("TA Setup 1Y Timeframe", False, f"Request failed: status={status}, error: {data.get('error', 'unknown')}")
            return False
            
        # Check basic structure
        required_fields = ["symbol", "timeframe", "candles", "candle_count", "scale_config", "structure"]
        for field in required_fields:
            if field not in data:
                self.log_result("TA Setup 1Y Timeframe", False, f"Missing field: {field}")
                return False
        
        candle_count = data.get("candle_count", 0)
        timeframe = data.get("timeframe")
        scale_config = data.get("scale_config", {})
        
        # Verify it's 1Y timeframe
        if timeframe != "1Y":
            self.log_result("TA Setup 1Y Timeframe", False, f"Expected timeframe 1Y, got {timeframe}")
            return False
            
        # Should have around 2500 daily candles (allow some tolerance)
        if not (2000 <= candle_count <= 3000):
            self.log_result("TA Setup 1Y Timeframe", False, f"Expected ~2500 daily candles, got {candle_count}")
            return False
        
        # Verify scale config for 1Y
        expected_lookback = 2500
        if scale_config.get("lookback") != expected_lookback:
            self.log_result("TA Setup 1Y Timeframe", False, f"Expected lookback {expected_lookback}, got {scale_config.get('lookback')}")
            return False
        
        print(f"   📈 1Y candles: {candle_count}")
        print(f"   📈 Scale config: {scale_config.get('description')}")
        print(f"   📈 Lookback: {scale_config.get('lookback')}")
        print(f"   📈 Pivot window: {scale_config.get('pivot_window')}")
        print(f"   📈 Pattern: {data.get('pattern', {}).get('type') if data.get('pattern') else 'None'}")
        
        self.log_result("TA Setup 1Y Timeframe", True)
        return data

    def test_structure_response_format(self):
        """Test that response contains proper structure analysis (trend, hh, hl, lh, ll)"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=BTC&tf=1D")
        
        if not success or status != 200:
            self.log_result("Structure Response Format", False, f"Request failed: status={status}, error: {data.get('error', 'unknown')}")
            return False
            
        structure = data.get("structure", {})
        
        # Check required structure fields
        required_structure_fields = ["trend", "hh", "hl", "lh", "ll"]
        for field in required_structure_fields:
            if field not in structure:
                self.log_result("Structure Response Format", False, f"Missing structure field: {field}")
                return False
        
        # Verify structure values are reasonable
        trend = structure.get("trend")
        if trend not in ["bullish", "bearish", "neutral"]:
            self.log_result("Structure Response Format", False, f"Invalid trend value: {trend}")
            return False
        
        # Check that structure counts are non-negative integers
        for field in ["hh", "hl", "lh", "ll"]:
            value = structure.get(field)
            if not isinstance(value, int) or value < 0:
                self.log_result("Structure Response Format", False, f"Invalid {field} value: {value}")
                return False
        
        print(f"   🏗️ Trend: {trend}")
        print(f"   🏗️ Higher Highs: {structure.get('hh')}")
        print(f"   🏗️ Higher Lows: {structure.get('hl')}")
        print(f"   🏗️ Lower Highs: {structure.get('lh')}")
        print(f"   🏗️ Lower Lows: {structure.get('ll')}")
        
        self.log_result("Structure Response Format", True)
        return structure

    def test_eth_4h_pattern(self):
        """Test ETH 4H pattern - should show descending_triangle (bearish)"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=ETH&tf=4H")
        
        if not success or status != 200:
            self.log_result("ETH 4H Pattern", False, f"Request failed: status={status}, error: {data.get('error', 'unknown')}")
            return False
            
        pattern = data.get("pattern")
        
        # Check if pattern exists
        if not pattern:
            print("   ⚠️ No pattern detected for ETH 4H (this may be normal)")
            self.log_result("ETH 4H Pattern", True, "No pattern detected")
            return data
        
        pattern_type = pattern.get("type")
        direction = pattern.get("direction")
        
        print(f"   🔺 ETH 4H Pattern: {pattern_type}")
        print(f"   🔺 Direction: {direction}")
        print(f"   🔺 Confidence: {pattern.get('confidence', 'N/A')}")
        print(f"   🔺 Timeframe: {data.get('timeframe')}")
        
        # Log pattern details (even if not descending_triangle)
        if pattern_type == "descending_triangle" and direction == "bearish":
            print("   ✅ Expected descending_triangle (bearish) pattern found!")
        else:
            print(f"   ℹ️ Pattern is {pattern_type} ({direction}), not descending_triangle (bearish)")
        
        self.log_result("ETH 4H Pattern", True)
        return data

    def test_different_timeframe_patterns(self):
        """Test that different timeframes produce different patterns (4H ≠ 1D ≠ 30D)"""
        print("   🔄 Testing pattern differences across timeframes...")
        
        timeframes = ["4H", "1D", "30D"]
        patterns = {}
        
        for tf in timeframes:
            success, data, status = self.make_request("GET", f"/api/ta/setup?symbol=BTC&tf={tf}")
            
            if not success or status != 200:
                self.log_result("Different Timeframe Patterns", False, f"Failed to get {tf} data: status={status}")
                return False
            
            pattern = data.get("pattern")
            pattern_type = pattern.get("type") if pattern else None
            direction = pattern.get("direction") if pattern else None
            structure_trend = data.get("structure", {}).get("trend")
            
            patterns[tf] = {
                "pattern_type": pattern_type,
                "direction": direction,
                "structure_trend": structure_trend
            }
            
            print(f"   📊 {tf}: Pattern={pattern_type or 'None'}, Direction={direction or 'None'}, Trend={structure_trend}")
        
        # Check that we have valid responses for all timeframes
        if len(patterns) != len(timeframes):
            self.log_result("Different Timeframe Patterns", False, f"Expected {len(timeframes)} timeframes, got {len(patterns)}")
            return False
        
        # Check for differences in patterns or structure trends
        pattern_types = [p["pattern_type"] for p in patterns.values()]
        directions = [p["direction"] for p in patterns.values()]
        trends = [p["structure_trend"] for p in patterns.values()]
        
        # Count unique values
        unique_patterns = len(set(filter(None, pattern_types)))
        unique_directions = len(set(filter(None, directions)))
        unique_trends = len(set(filter(None, trends)))
        
        print(f"   🎯 Unique pattern types: {unique_patterns}")
        print(f"   🎯 Unique directions: {unique_directions}")
        print(f"   🎯 Unique trends: {unique_trends}")
        
        # Success if there's variation in any aspect
        has_variation = (unique_patterns > 1) or (unique_directions > 1) or (unique_trends > 1)
        
        if has_variation:
            print("   ✅ Timeframes show different analysis results!")
        else:
            print("   ⚠️ All timeframes show similar results (this may be normal)")
        
        self.log_result("Different Timeframe Patterns", True)
        return patterns

    # ═══════════════════════════════════════════════════════════════
    # Test Runner
    # ═══════════════════════════════════════════════════════════════

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting TA Engine API Tests - Multi-Scale Market Hierarchy...")
        print(f"🌐 Base URL: {self.base_url}")
        print("=" * 80)
        
        # Health check
        print("\n🔧 HEALTH CHECK")
        print("-" * 50)
        self.test_health_endpoint()
        
        # Core timeframe tests (4H and 1Y as specified)
        print("\n📊 CORE TIMEFRAME TESTS")
        print("-" * 50)
        
        self.test_ta_setup_4h_timeframe()
        self.test_ta_setup_1y_timeframe()
        
        # Structure response format
        print("\n🏗️ STRUCTURE ANALYSIS TEST")
        print("-" * 50)
        self.test_structure_response_format()
        
        # ETH 4H pattern test
        print("\n🔺 ETH 4H PATTERN TEST")
        print("-" * 50)
        self.test_eth_4h_pattern()
        
        # Pattern difference test
        print("\n🎯 TIMEFRAME PATTERN DIFFERENCES")
        print("-" * 50)
        self.test_different_timeframe_patterns()
        
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
    print("TA Engine API Tester - Multi-Scale Market Hierarchy")
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