#!/usr/bin/env python3
"""
Backend API Testing for Signal Lifecycle Engine + Performance Analytics

Tests for:
- Signal lifecycle (pending → active → tp1_hit → tp2_hit → tp3_hit)
- Performance metrics (win_rate, profit_factor, avg_rr)
- TP/SL hit detection
- Regime confidence/stability/outlook
- Indicator quality analysis
- Signal outcomes tracking
"""

import requests
import sys
import time
import uuid
from datetime import datetime
from typing import Dict, List, Optional


class TradingEngineAPITester:
    def __init__(self, base_url: str = "https://confluence-map.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.test_results = []
        
        # Track created signals for cleanup
        self.created_signals: List[str] = []

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
    # Core API Tests
    # ═══════════════════════════════════════════════════════════════

    def test_trading_engine_status(self):
        """Test trading engine health check"""
        success, data, status = self.make_request("GET", "/api/trading/status")
        
        if not success or status != 200:
            self.log_result("Trading Engine Status", False, f"Request failed: status={status}")
            return False
            
        if not data.get("ok"):
            self.log_result("Trading Engine Status", False, "Status not OK")
            return False
            
        # Check required components
        components = data.get("components", {})
        required_components = ["entry_filter", "position_sizer", "state_engine"]
        
        for comp in required_components:
            if components.get(comp) != "active":
                self.log_result("Trading Engine Status", False, f"Component {comp} not active")
                return False
        
        self.log_result("Trading Engine Status", True)
        return True

    def test_full_analysis_with_regime_metrics(self):
        """Test full analysis endpoint with regime_confidence/stability/outlook"""
        success, data, status = self.make_request("GET", "/api/trading/full-analysis/BTC/1H")
        
        if not success or status != 200:
            self.log_result("Full Analysis with Regime Metrics", False, f"Request failed: status={status}")
            return False
            
        # Check basic structure
        if not all(key in data for key in ["symbol", "market_state", "trading_decision"]):
            self.log_result("Full Analysis with Regime Metrics", False, "Missing required fields")
            return False
            
        # Check regime metrics specifically
        market_state = data.get("market_state", {})
        regime_fields = ["regime_confidence", "regime_stability", "regime_outlook"]
        
        missing_fields = []
        for field in regime_fields:
            if field not in market_state:
                missing_fields.append(field)
                
        if missing_fields:
            self.log_result("Full Analysis with Regime Metrics", False, f"Missing regime fields: {missing_fields}")
            return False
            
        # Validate regime field types and ranges
        regime_confidence = market_state.get("regime_confidence")
        if not isinstance(regime_confidence, (int, float)) or not (0 <= regime_confidence <= 1):
            self.log_result("Full Analysis with Regime Metrics", False, f"Invalid regime_confidence: {regime_confidence}")
            return False
            
        regime_stability = market_state.get("regime_stability")
        valid_stability_values = ["stable", "weakening", "transitioning", "forming"]
        if regime_stability not in valid_stability_values:
            self.log_result("Full Analysis with Regime Metrics", False, f"Invalid regime_stability: {regime_stability}")
            return False
            
        regime_outlook = market_state.get("regime_outlook")
        if not isinstance(regime_outlook, str) or len(regime_outlook) == 0:
            self.log_result("Full Analysis with Regime Metrics", False, f"Invalid regime_outlook: {regime_outlook}")
            return False
            
        print(f"   💡 Regime confidence: {regime_confidence:.3f}")
        print(f"   💡 Regime stability: {regime_stability}")
        print(f"   💡 Regime outlook: {regime_outlook}")
        
        self.log_result("Full Analysis with Regime Metrics", True)
        return True

    def test_performance_metrics_endpoint(self):
        """Test performance metrics endpoint"""
        success, data, status = self.make_request("GET", "/api/trading/performance")
        
        if not success or status != 200:
            self.log_result("Performance Metrics Endpoint", False, f"Request failed: status={status}")
            return False
            
        # Check performance data structure
        performance = data.get("performance", {})
        
        required_fields = [
            "win_rate", "profit_factor", "avg_rr_achieved",
            "tp1_hit_rate", "tp2_hit_rate", "tp3_hit_rate",
            "signals_total", "signals_closed", "signals_active"
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in performance:
                missing_fields.append(field)
                
        if missing_fields:
            self.log_result("Performance Metrics Endpoint", False, f"Missing fields: {missing_fields}")
            return False
            
        # Validate metric ranges
        win_rate = performance.get("win_rate", 0)
        if not isinstance(win_rate, (int, float)) or not (0 <= win_rate <= 1):
            self.log_result("Performance Metrics Endpoint", False, f"Invalid win_rate: {win_rate}")
            return False
            
        profit_factor = performance.get("profit_factor", 0)
        if not isinstance(profit_factor, (int, float)) or profit_factor < 0:
            self.log_result("Performance Metrics Endpoint", False, f"Invalid profit_factor: {profit_factor}")
            return False
            
        print(f"   📊 Win rate: {win_rate:.1%}")
        print(f"   📊 Profit factor: {profit_factor:.2f}")
        print(f"   📊 Signals total: {performance.get('signals_total', 0)}")
        
        self.log_result("Performance Metrics Endpoint", True)
        return True

    def test_indicator_quality_analysis(self):
        """Test indicator quality analysis endpoint"""
        success, data, status = self.make_request("GET", "/api/trading/indicator-quality")
        
        if not success or status != 200:
            self.log_result("Indicator Quality Analysis", False, f"Request failed: status={status}")
            return False
            
        # Check quality report structure
        quality_report = data.get("quality_report", {})
        
        required_fields = [
            "best_indicator_drivers", "worst_indicator_drivers", 
            "indicator_win_rates", "signals_analyzed"
        ]
        
        for field in required_fields:
            if field not in quality_report:
                self.log_result("Indicator Quality Analysis", False, f"Missing field: {field}")
                return False
                
        # Validate structure
        best_drivers = quality_report.get("best_indicator_drivers", [])
        if not isinstance(best_drivers, list):
            self.log_result("Indicator Quality Analysis", False, "best_indicator_drivers not a list")
            return False
            
        indicator_win_rates = quality_report.get("indicator_win_rates", {})
        if not isinstance(indicator_win_rates, dict):
            self.log_result("Indicator Quality Analysis", False, "indicator_win_rates not a dict")
            return False
            
        signals_analyzed = quality_report.get("signals_analyzed", 0)
        print(f"   🎯 Signals analyzed: {signals_analyzed}")
        print(f"   🎯 Best indicators count: {len(best_drivers)}")
        print(f"   🎯 Indicator win rates tracked: {len(indicator_win_rates)}")
        
        self.log_result("Indicator Quality Analysis", True)
        return True

    def test_signal_outcomes_endpoint(self):
        """Test signal outcomes endpoint"""
        success, data, status = self.make_request("GET", "/api/trading/outcomes")
        
        if not success or status != 200:
            self.log_result("Signal Outcomes Endpoint", False, f"Request failed: status={status}")
            return False
            
        # Check outcomes structure
        outcomes = data.get("outcomes", [])
        if not isinstance(outcomes, list):
            self.log_result("Signal Outcomes Endpoint", False, "outcomes not a list")
            return False
            
        # If we have outcomes, validate structure
        if outcomes:
            outcome = outcomes[0]
            required_fields = [
                "signal_id", "direction", "entry_price", "exit_price", 
                "outcome", "pnl_pct", "rr_achieved"
            ]
            
            for field in required_fields:
                if field not in outcome:
                    self.log_result("Signal Outcomes Endpoint", False, f"Missing field in outcome: {field}")
                    return False
                    
            # Validate outcome values
            if outcome.get("outcome") not in ["win", "loss", "breakeven"]:
                self.log_result("Signal Outcomes Endpoint", False, f"Invalid outcome value: {outcome.get('outcome')}")
                return False
        
        print(f"   📋 Outcomes retrieved: {len(outcomes)}")
        
        self.log_result("Signal Outcomes Endpoint", True)
        return True

    # ═══════════════════════════════════════════════════════════════
    # Signal Lifecycle Tests
    # ═══════════════════════════════════════════════════════════════

    def test_signal_generation(self):
        """Test signal generation"""
        success, data, status = self.make_request("GET", "/api/trading/signals/generate/BTC/1H?save=true")
        
        if not success or status != 200:
            self.log_result("Signal Generation", False, f"Request failed: status={status}")
            return None
            
        signal = data.get("signal")
        if signal is None:
            # No signal generated is also valid
            print(f"   ⚠️  No signal generated (market conditions not met)")
            self.log_result("Signal Generation", True, "No signal conditions met")
            return None
            
        # Validate signal structure
        required_fields = ["signal_id", "symbol", "direction", "status", "entry_price", "take_profit"]
        
        for field in required_fields:
            if field not in signal:
                self.log_result("Signal Generation", False, f"Missing field: {field}")
                return None
                
        signal_id = signal.get("signal_id")
        if signal_id:
            self.created_signals.append(signal_id)
            
        print(f"   🎯 Signal generated: {signal_id}")
        print(f"   🎯 Direction: {signal.get('direction')}")
        print(f"   🎯 Status: {signal.get('status')}")
        
        self.log_result("Signal Generation", True)
        return signal

    def test_price_update_and_tp_detection(self):
        """Test price updates and TP/SL detection"""
        # First, try to get active signals
        success, data, status = self.make_request("GET", "/api/trading/signals/active")
        
        if not success or status != 200:
            self.log_result("Price Update & TP Detection", False, f"Failed to get active signals: status={status}")
            return False
            
        active_signals = data.get("signals", [])
        
        # If no active signals, generate one first
        if not active_signals:
            print("   ⚠️  No active signals found, generating test signal first...")
            generated_signal = self.test_signal_generation()
            if not generated_signal:
                self.log_result("Price Update & TP Detection", False, "Could not generate test signal")
                return False
                
        # Test price update mechanism
        price_updates = {
            "BTC": 50000.0,  # Test price
            "ETH": 3000.0,
            "SOL": 100.0
        }
        
        success, data, status = self.make_request("POST", "/api/trading/signals/update-prices", price_updates)
        
        if not success or status != 200:
            self.log_result("Price Update & TP Detection", False, f"Price update failed: status={status}")
            return False
            
        # Check response structure
        if "signals_updated" not in data or "alerts_generated" not in data:
            self.log_result("Price Update & TP Detection", False, "Missing response fields")
            return False
            
        signals_updated = data.get("signals_updated", 0)
        alerts_generated = data.get("alerts_generated", 0)
        
        print(f"   🔄 Signals updated: {signals_updated}")
        print(f"   🔔 Alerts generated: {alerts_generated}")
        
        self.log_result("Price Update & TP Detection", True)
        return True

    def test_signal_invalidation(self):
        """Test signal invalidation"""
        # First get active signals to invalidate
        success, data, status = self.make_request("GET", "/api/trading/signals/active")
        
        if not success:
            self.log_result("Signal Invalidation", False, f"Failed to get active signals: status={status}")
            return False
            
        active_signals = data.get("signals", [])
        
        if not active_signals:
            # Generate a signal first
            print("   ⚠️  No active signals, generating one for invalidation test...")
            generated_signal = self.test_signal_generation()
            if not generated_signal:
                self.log_result("Signal Invalidation", False, "Could not generate test signal")
                return False
            signal_id = generated_signal.get("signal_id")
        else:
            signal_id = active_signals[0].get("signal_id")
            
        if not signal_id:
            self.log_result("Signal Invalidation", False, "No signal ID found")
            return False
            
        # Test invalidation
        endpoint = f"/api/trading/signals/{signal_id}/invalidate?reason=Test invalidation"
        success, data, status = self.make_request("POST", endpoint)
        
        if not success or status != 200:
            self.log_result("Signal Invalidation", False, f"Invalidation failed: status={status}")
            return False
            
        if not data.get("invalidated"):
            self.log_result("Signal Invalidation", False, "Signal not marked as invalidated")
            return False
            
        print(f"   ❌ Signal invalidated: {signal_id}")
        
        self.log_result("Signal Invalidation", True)
        return True

    # ═══════════════════════════════════════════════════════════════
    # Additional Signal Management Tests
    # ═══════════════════════════════════════════════════════════════

    def test_signal_listing_and_filtering(self):
        """Test signal listing with various filters"""
        # Test basic signal listing
        success, data, status = self.make_request("GET", "/api/trading/signals")
        
        if not success or status != 200:
            self.log_result("Signal Listing & Filtering", False, f"Basic listing failed: status={status}")
            return False
            
        signals = data.get("signals", [])
        total_signals = len(signals)
        
        # Test with symbol filter
        success, data, status = self.make_request("GET", "/api/trading/signals?symbol=BTC&limit=10")
        
        if not success or status != 200:
            self.log_result("Signal Listing & Filtering", False, f"Symbol filter failed: status={status}")
            return False
            
        btc_signals = data.get("signals", [])
        
        # Test with status filter
        success, data, status = self.make_request("GET", "/api/trading/signals?status=active&limit=10")
        
        if success and status == 200:
            active_signals = data.get("signals", [])
            print(f"   📊 Total signals: {total_signals}")
            print(f"   📊 BTC signals: {len(btc_signals)}")
            print(f"   📊 Active signals: {len(active_signals)}")
        
        self.log_result("Signal Listing & Filtering", True)
        return True

    def test_signal_stats(self):
        """Test signal statistics endpoint"""
        success, data, status = self.make_request("GET", "/api/trading/signals/stats")
        
        if not success or status != 200:
            self.log_result("Signal Stats", False, f"Request failed: status={status}")
            return False
            
        stats = data.get("stats", {})
        if not isinstance(stats, dict):
            self.log_result("Signal Stats", False, "Stats not a dictionary")
            return False
            
        print(f"   📈 Signal stats retrieved: {len(stats)} metrics")
        
        self.log_result("Signal Stats", True)
        return True

    # ═══════════════════════════════════════════════════════════════
    # Test Runner
    # ═══════════════════════════════════════════════════════════════

    def run_all_tests(self):
        """Run all tests in sequence"""
        print("🚀 Starting Trading Engine API Tests...")
        print(f"🌐 Base URL: {self.base_url}")
        print("=" * 80)
        
        # Core functionality tests
        print("\n🔧 CORE FUNCTIONALITY TESTS")
        print("-" * 50)
        
        self.test_trading_engine_status()
        self.test_full_analysis_with_regime_metrics()
        self.test_performance_metrics_endpoint()
        self.test_indicator_quality_analysis()
        self.test_signal_outcomes_endpoint()
        
        # Signal lifecycle tests
        print("\n🔄 SIGNAL LIFECYCLE TESTS")
        print("-" * 50)
        
        self.test_signal_generation()
        self.test_price_update_and_tp_detection()
        self.test_signal_invalidation()
        
        # Additional management tests
        print("\n📊 SIGNAL MANAGEMENT TESTS")
        print("-" * 50)
        
        self.test_signal_listing_and_filtering()
        self.test_signal_stats()
        
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

    def cleanup(self):
        """Clean up created test data"""
        print(f"\n🧹 Cleaning up {len(self.created_signals)} test signals...")
        
        for signal_id in self.created_signals:
            try:
                success, _, status = self.make_request("DELETE", f"/api/trading/signals/{signal_id}")
                if success and status == 200:
                    print(f"   ✅ Deleted signal: {signal_id}")
                else:
                    print(f"   ⚠️  Failed to delete signal: {signal_id}")
            except Exception as e:
                print(f"   ❌ Error deleting signal {signal_id}: {e}")


def main():
    """Main test runner"""
    print("Trading Engine API Tester")
    print("=" * 80)
    
    # Initialize tester
    tester = TradingEngineAPITester()
    
    try:
        # Run tests
        success = tester.run_all_tests()
        
        # Cleanup
        tester.cleanup()
        
        # Exit with appropriate code
        return 0 if success else 1
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        tester.cleanup()
        return 1
        
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        tester.cleanup()
        return 1


if __name__ == "__main__":
    sys.exit(main())