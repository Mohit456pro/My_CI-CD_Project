"""Integration tests for FastAPI endpoints."""

from fastapi.testclient import TestClient

from src.app.main import app

client = TestClient(app)


def test_root_endpoint():
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["service"] == "ci-cd-demo-service"
    assert "version" in data


def test_liveness_probe():
    response = client.get("/health/live")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "alive"
    assert "uptime_seconds" in data


def test_readiness_probe():
    response = client.get("/health/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["database"] == "connected"


def test_version_endpoint():
    response = client.get("/version")
    assert response.status_code == 200
    data = response.json()
    assert "version" in data
    assert "commit_sha" in data


def test_calculate_discount_api_success():
    payload = {"price": 100.0, "discount_percent": 20.0}
    response = client.post("/api/v1/discounts/calculate", json=payload)
    assert response.status_code == 200
    assert response.json()["final_price"] == 80.0


def test_calculate_discount_api_validation_error():
    # Negative price rejected by Pydantic validation (422)
    payload = {"price": -50.0, "discount_percent": 10.0}
    response = client.post("/api/v1/discounts/calculate", json=payload)
    assert response.status_code == 422


def test_order_summary_api_success():
    payload = {
        "items": [
            {"name": "Book", "price": 25.0, "quantity": 2},
            {"name": "Pen", "price": 5.0, "quantity": 4},
        ],
        "tax_rate": 0.05,
    }
    response = client.post("/api/v1/orders/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["item_count"] == 6
    assert data["subtotal"] == 70.0
    assert data["tax"] == 3.50
    assert data["total"] == 73.50
