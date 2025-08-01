"""
Tests for fraud detection API.
"""

import pytest
from datetime import datetime
from fastapi.testclient import TestClient

from banking_fraud_api.api.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Banking Fraud Detection API" in data["message"]


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "timestamp" in data
    assert "version" in data


def test_metrics_endpoint():
    """Test metrics endpoint."""
    response = client.get("/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "total_requests" in data
    assert "fraud_rate" in data


def test_fraud_detection():
    """Test fraud detection endpoint."""
    test_transaction = {
        "transaction_id": "test_123",
        "user_id": "user_456",
        "amount": 1000.0,
        "merchant_category": "retail",
        "transaction_type": "purchase",
        "timestamp": datetime.utcnow().isoformat(),
        "location": "Istanbul, Turkey"
    }
    
    response = client.post("/api/v1/fraud/detect", json=test_transaction)
    assert response.status_code == 200
    
    data = response.json()
    assert "fraud_score" in data
    assert "is_fraud" in data
    assert "risk_level" in data
    assert "correlation_id" in data
    assert data["transaction_id"] == test_transaction["transaction_id"]


def test_high_amount_fraud_detection():
    """Test fraud detection with high amount."""
    test_transaction = {
        "transaction_id": "test_high_amount",
        "user_id": "user_789",
        "amount": 15000.0,  # High amount
        "merchant_category": "gambling",  # High risk category
        "transaction_type": "purchase",
        "timestamp": "2024-01-01T02:00:00",  # Late night
        "location": "unknown"
    }
    
    response = client.post("/api/v1/fraud/detect", json=test_transaction)
    assert response.status_code == 200
    
    data = response.json()
    assert data["fraud_score"] > 0.5  # Should be high
    assert data["is_fraud"] == True
    assert data["risk_level"] in ["HIGH", "CRITICAL"]


def test_batch_fraud_detection():
    """Test batch fraud detection."""
    transactions = [
        {
            "transaction_id": f"batch_{i}",
            "user_id": f"user_{i}",
            "amount": 100.0 * i,
            "merchant_category": "retail",
            "transaction_type": "purchase",
            "timestamp": datetime.utcnow().isoformat()
        }
        for i in range(1, 4)
    ]
    
    response = client.post("/api/v1/fraud/detect/batch", json=transactions)
    assert response.status_code == 200
    
    data = response.json()
    assert "results" in data
    assert len(data["results"]) == 3


def test_batch_size_limit():
    """Test batch size limit."""
    # Create too many transactions
    transactions = [
        {
            "transaction_id": f"test_{i}",
            "user_id": "user_test",
            "amount": 100.0,
            "merchant_category": "retail",
            "transaction_type": "purchase",
            "timestamp": datetime.utcnow().isoformat()
        }
        for i in range(101)  # 101 transactions (over limit)
    ]
    
    response = client.post("/api/v1/fraud/detect/batch", json=transactions)
    assert response.status_code == 400
    assert "Batch size too large" in response.json()["detail"]


if __name__ == "__main__":
    pytest.main([__file__])
