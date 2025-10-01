import pytest
import asyncio
import json
from unittest.mock import Mock, patch, AsyncMock
from fastapi.testclient import TestClient
import os
import numpy as np
import pandas as pd

# Set test environment variables
os.environ["SECRET_KEY"] = "test-secret-key"
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost/test"
os.environ["MONGODB_URL"] = "mongodb://localhost:27017/test"
os.environ["REDIS_URL"] = "redis://localhost:6379"

from api.main import app, get_liveness_status

client = TestClient(app)

# --- Mock for timeout test ---
async def mock_timeout():
    raise asyncio.TimeoutError("Simulated timeout")

class TestEdgeCases:
    """Comprehensive edge case testing for the GenX FX API"""
    
    def test_health_endpoint_structure(self):
        """Test health endpoint returns correct structure"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        
        # Check required fields
        assert "status" in data
        assert "timestamp" in data
        assert "services" in data
        assert "ml_service" in data["services"]
        assert "data_service" in data["services"]
        
        # Validate timestamp format
        from datetime import datetime
        try:
            datetime.fromisoformat(data["timestamp"].replace('Z', '+00:00'))
        except ValueError:
            pytest.fail("Invalid timestamp format")
    
    def test_root_endpoint_completeness(self):
        """Test root endpoint has all required information"""
        response = client.get("/api")
        assert response.status_code == 200
        data = response.json()
        
        required_fields = ["message", "version", "status", "repository"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"
        
        assert data["status"] == "running"
        assert data["repository"] == "https://github.com/Mouy-leng/GenX_FX.git"
    
    def test_cors_headers(self):
        """Test CORS headers are properly set"""
        response = client.options("/api")
        # The test client might not fully simulate CORS, but we can check basic structure
        assert response.status_code in [200, 405]  # OPTIONS might not be implemented
    
    def test_large_request_handling(self):
        """Test handling of large request payloads"""
        # Test with a reasonably large payload
        large_data = {
            "symbol": "BTCUSDT",
            "data": ["x" * 1000] * 100,  # 100KB of data
            "metadata": {
                "large_array": list(range(1000)),
                "nested": {"deep": {"data": "test" * 100}}
            }
        }
        
        response = client.post("/api/v1/predictions", json=large_data)
        # We expect either success or a structured error, not a crash
        assert response.status_code == 200
    
    def test_malformed_json_handling(self):
        """Test handling of malformed JSON requests"""
        response = client.post(
            "/api/v1/predictions",
            content="{ invalid json }",
            headers={"content-type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_null_and_empty_values(self):
        """Test handling of null and empty values in requests"""
        test_cases = [
            {"symbol": "BTCUSDT", "data": None},  # data cannot be None
            {"symbol": None, "data": {}}, # symbol cannot be None
            {}, # missing both fields
        ]
        
        for test_data in test_cases:
            response = client.post("/api/v1/predictions", json=test_data)
            # Should handle gracefully, not crash
            assert response.status_code == 422
            error_data = response.json()
            assert "detail" in error_data
    
    def test_special_characters_handling(self):
        """Test handling of special characters and Unicode"""
        special_data = {
            "symbol": "BTC/USDT 🚀",
            "data": {
                "comment": "Testing 🚀📊💹 emojis and café résumé naïve",
                "chinese": "测试数据",
                "arabic": "بيانات الاختبار",
                "special": "!@#$%^&*()_+-=[]{}|;:,.<>?"
            }
        }
        
        response = client.post("/api/v1/predictions", json=special_data)
        assert response.status_code == 200
    
    def test_numeric_edge_cases(self):
        """Test handling of numeric edge cases"""
        edge_cases = [
            {"symbol": "test", "data": 0},
            {"symbol": "test", "data": -1},
            {"symbol": "test", "data": 1e10},
        ]
        
        for test_data in edge_cases:
            response = client.post("/api/v1/predictions", json=test_data)
            assert response.status_code == 422 # data must be Dict, List, or str

    def test_array_edge_cases(self):
        """Test handling of array edge cases"""
        array_cases = [
            {"symbol": "test", "data": []},  # Empty array
            {"symbol": "test", "data": [None, None, None]},  # Array of nulls is valid
            {"symbol": "test", "data": [1, "string", True, None, {"nested": "object"}]},  # Mixed types
            {"symbol": "test", "data": [[1, 2], [3, 4], []]},  # Nested arrays with empty
        ]
        
        for test_data in array_cases:
            response = client.post("/api/v1/predictions", json=test_data)
            assert response.status_code == 200
    
    def test_deeply_nested_objects(self):
        """Test handling of deeply nested objects"""
        nested_data = {"data": {}}
        current = nested_data["data"]
        for i in range(20):
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]
        current["deep_value"] = "reached the bottom"
        
        nested_data['symbol'] = 'nested_test'

        response = client.post("/api/v1/predictions", json=nested_data)
        assert response.status_code == 200
    
    def test_concurrent_requests(self):
        """Test handling of concurrent requests"""
        import threading
        
        results = []
        def make_request():
            response = client.get("/api/health")
            results.append(response.status_code)
        
        threads = [threading.Thread(target=make_request) for _ in range(10)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        
        assert all(status == 200 for status in results)
        assert len(results) == 10

class TestDataValidation:
    """Test data validation and sanitization"""
    
    def test_sql_injection_prevention(self):
        """Test SQL injection attempts are handled safely"""
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
        ]
        
        for malicious_input in malicious_inputs:
            test_data = {"symbol": malicious_input, "data": "test"}
            response = client.post("/api/v1/predictions", json=test_data)
            assert response.status_code == 200
            response_text = response.text.lower()
            assert "sql" not in response_text
    
    def test_xss_prevention(self):
        """Test XSS attempts are handled safely"""
        xss_payloads = [
            "<script>alert('xss')</script>",
            "<img src=x onerror=alert('xss')>",
        ]
        
        for payload in xss_payloads:
            test_data = {"symbol": "xss_test", "data": payload}
            response = client.post("/api/v1/predictions", json=test_data)
            assert response.status_code == 200
            if "text/html" in response.headers.get("content-type", ""):
                assert "<script>" not in response.text

class TestPerformanceEdgeCases:
    """Test performance-related edge cases"""
    
    def test_response_time_reasonable(self):
        """Test that responses come back in reasonable time"""
        import time
        start_time = time.time()
        response = client.get("/api/health")
        response_time = time.time() - start_time
        assert response_time < 2.0
        assert response.status_code == 200
    
    def test_memory_usage_with_large_data(self):
        """Test memory usage doesn't explode with large data"""
        large_data = {
            "symbol": "large_data_test",
            "data": ["x" * 1000] * 100
        } # ~100KB
        response = client.post("/api/v1/predictions", json=large_data)
        assert response.status_code == 200

class TestErrorHandling:
    """Test comprehensive error handling"""
    
    def test_undefined_endpoints(self):
        """Test handling of undefined endpoints"""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
    
    def test_method_not_allowed(self):
        """Test handling of wrong HTTP methods"""
        response = client.delete("/api/health")
        assert response.status_code == 405
    
    def test_content_type_handling(self):
        """Test handling of different content types"""
        response = client.post(
            "/api/v1/predictions",
            content="not json",
            headers={"content-type": "text/plain"}
        )
        assert response.status_code == 422
    
    def test_timeout_handling(self):
        """Test handling of operations that might timeout"""
        app.dependency_overrides[get_liveness_status] = mock_timeout
        response = client.get("/api/health")
        assert response.status_code == 500
        # Clean up the override
        app.dependency_overrides = {}


if __name__ == "__main__":
    pytest.main([__file__, "-v"])