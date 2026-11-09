"""
API endpoint tests for /api/scan, /api/health, /api/reports, /api/dashboard.
"""

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "database_connected" in data


def test_scan_endpoint_success():
    payload = {
        "url": "https://example-shop.com",
        "page_text": "Only 3 minutes left! No thanks, I hate saving money.",
        "buttons": [
            {"text": "No, I don't want to save money", "is_visible": True}
        ],
        "links": [],
        "checkboxes": [
            {"label": "Subscribe to warranty $14.99", "is_checked": True, "is_visible": True}
        ],
        "forms": [],
        "timers": [],
        "meta": {"title": "Flash Sale", "description": "Deals"},
    }

    response = client.post("/api/scan", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "scan_id" in data
    assert data["risk_score"] > 0
    assert data["total_patterns"] >= 1
    assert len(data["patterns"]) >= 1


def test_dashboard_stats_endpoint():
    response = client.get("/api/dashboard/stats")
    assert response.status_code == 200
    data = response.json()
    assert "total_scans" in data
    assert "average_risk_score" in data


def test_reports_list_endpoint():
    response = client.get("/api/reports")
    assert response.status_code == 200
    data = response.json()
    assert "reports" in data
    assert "total" in data

