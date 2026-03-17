#!/usr/bin/env python3
"""
TA Engine Backend API Testing

Tests for the required endpoints:
- GET /api/health - Health check API должен вернуть ok=true  
- GET /api/system/db-health - Проверка подключения MongoDB
- GET /api/ta-engine/status - Статус TA Engine модуля
- GET /api/ta/setup?symbol=BTCUSDT&tf=1D - TA Setup API с паттернами и уровнями
- GET /api/provider/coinbase/status - Статус Coinbase провайдера  
- GET /api/broker/health - Broker adapters health
- GET /api/broker/list - Список доступных брокеров включая Coinbase
"""

import requests
import sys
import time
import json
from datetime import datetime
from typing import Dict, List, Optional


class TAEngineAPITester:
    def __init__(self, base_url: str = "https://github-analyzer-21.preview.emergentagent.com"):
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
    # Required API Tests
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

    def test_db_health(self):
        """Test GET /api/system/db-health - Проверка подключения MongoDB"""
        success, data, status = self.make_request("GET", "/api/system/db-health")
        
        if not success:
            self.log_result("DB Health Check", False, "Request failed")
            return False
            
        if status != 200:
            self.log_result("DB Health Check", False, f"Status code: {status}")
            return False
            
        # Check if connected is true or status is ok
        connected = data.get("connected", False)
        db_status = data.get("status", "")
        
        if not connected and db_status != "ok":
            self.log_result("DB Health Check", False, f"Database not connected: {data}")
            return False
            
        self.log_result("DB Health Check", True, f"Connected: {connected}")
        return True

    def test_ta_engine_status(self):
        """Test GET /api/ta-engine/status - Статус TA Engine модуля"""
        success, data, status = self.make_request("GET", "/api/ta-engine/status")
        
        if not success:
            self.log_result("TA Engine Status", False, "Request failed")
            return False
            
        if status != 200:
            self.log_result("TA Engine Status", False, f"Status code: {status}")
            return False
            
        if not data.get("ok"):
            self.log_result("TA Engine Status", False, f"TA Engine not ok: {data}")
            return False
            
        module_name = data.get("module", "unknown")
        version = data.get("version", "unknown")
        
        self.log_result("TA Engine Status", True, f"Module: {module_name}, Version: {version}")
        return True

    def test_ta_setup_api(self):
        """Test GET /api/ta/setup?symbol=BTCUSDT&tf=1D - TA Setup API с паттернами и уровнями"""
        success, data, status = self.make_request("GET", "/api/ta/setup?symbol=BTCUSDT&tf=1D")
        
        if not success:
            self.log_result("TA Setup API", False, "Request failed")
            return False
            
        if status != 200:
            self.log_result("TA Setup API", False, f"Status code: {status}")
            return False
            
        # Validate response structure
        required_fields = ["symbol", "timeframe", "candles", "pattern", "levels", "structure", "setup"]
        missing_fields = []
        
        for field in required_fields:
            if field not in data:
                missing_fields.append(field)
                
        if missing_fields:
            self.log_result("TA Setup API", False, f"Missing fields: {missing_fields}")
            return False
            
        # Check data quality
        candles_count = len(data.get("candles", []))
        levels_count = len(data.get("levels", []))
        pattern_type = data.get("pattern", {}).get("type", "none")
        setup_direction = data.get("setup", {}).get("direction", "none") if data.get("setup") else "none"
        
        details = f"Candles: {candles_count}, Levels: {levels_count}, Pattern: {pattern_type}, Direction: {setup_direction}"
        self.log_result("TA Setup API", True, details)
        return True

    def test_coinbase_provider_status(self):
        """Test GET /api/provider/coinbase/status - Статус Coinbase провайдера"""
        success, data, status = self.make_request("GET", "/api/provider/coinbase/status")
        
        if not success:
            self.log_result("Coinbase Provider Status", False, "Request failed")
            return False
            
        if status != 200:
            self.log_result("Coinbase Provider Status", False, f"Status code: {status}")
            return False
            
        provider_status = data.get("status", "unknown")
        provider = data.get("provider", "unknown")
        
        # Accept various valid statuses
        valid_statuses = ["active", "connected", "ok", "online"]
        if provider_status not in valid_statuses and "error" not in data:
            self.log_result("Coinbase Provider Status", False, f"Provider status unclear: {data}")
            return False
            
        self.log_result("Coinbase Provider Status", True, f"Provider: {provider}, Status: {provider_status}")
        return True

    def test_broker_health(self):
        """Test GET /api/broker/health - Broker adapters health"""
        success, data, status = self.make_request("GET", "/api/broker/health")
        
        if not success:
            self.log_result("Broker Health", False, "Request failed")
            return False
            
        if status != 200:
            self.log_result("Broker Health", False, f"Status code: {status}")
            return False
            
        # Check if enabled or status is ok
        enabled = data.get("enabled", False)
        broker_status = data.get("status", "unknown")
        
        if not enabled and broker_status not in ["ok", "healthy"]:
            self.log_result("Broker Health", False, f"Broker adapters not healthy: {data}")
            return False
            
        version = data.get("version", "unknown")
        active_connections = data.get("active_connections", 0)
        
        details = f"Status: {broker_status}, Enabled: {enabled}, Connections: {active_connections}, Version: {version}"
        self.log_result("Broker Health", True, details)
        return True

    def test_broker_list(self):
        """Test GET /api/broker/list - Список доступных брокеров включая Coinbase"""
        success, data, status = self.make_request("GET", "/api/broker/list")
        
        if not success:
            self.log_result("Broker List", False, "Request failed")
            return False
            
        if status != 200:
            self.log_result("Broker List", False, f"Status code: {status}")
            return False
            
        brokers = data.get("brokers", {})
        if not isinstance(brokers, dict):
            self.log_result("Broker List", False, f"Brokers not a dict: {type(brokers)}")
            return False
            
        # Check if Coinbase is in the list
        coinbase_found = False
        broker_names = list(brokers.keys()) if brokers else []
        
        for broker_name in broker_names:
            if "coinbase" in broker_name.lower():
                coinbase_found = True
                break
                
        if not coinbase_found:
            self.log_result("Broker List", False, f"Coinbase not found in brokers: {broker_names}")
            return False
            
        details = f"Brokers available: {len(broker_names)}, Found: {broker_names}"
        self.log_result("Broker List", True, details)
        return True

    # ═══════════════════════════════════════════════════════════════
    # Test Runner
    # ═══════════════════════════════════════════════════════════════

    def run_all_tests(self):
        """Run all required tests"""
        print("🚀 Starting TA Engine API Tests...")
        print(f"🌐 Base URL: {self.base_url}")
        print("=" * 80)
        
        # Run all required tests
        print("\n🔧 REQUIRED API TESTS")
        print("-" * 50)
        
        self.test_health_api()
        time.sleep(0.5)  # Small delay between tests
        
        self.test_db_health()
        time.sleep(0.5)
        
        self.test_ta_engine_status()
        time.sleep(0.5)
        
        self.test_ta_setup_api()
        time.sleep(1)  # Longer delay for heavy API
        
        self.test_coinbase_provider_status()
        time.sleep(0.5)
        
        self.test_broker_health()
        time.sleep(0.5)
        
        self.test_broker_list()
        
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
    print("TA Engine API Tester")
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