import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "online"
    assert data["supabase_connected"] is True


def test_get_jerseys():
    response = client.get("/jerseys")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    # Check that Como is in the data
    found = any("Como" in item.get("name", "") for item in data)
    assert found is True


def test_chat_order_request():
    # 1. First message: request order
    response = client.post("/chat", json={
        "conversation_id": "test-order-001",
        "customer_id": "cust-001",
        "message": "kak saya mau pesan Como Home ukuran L"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["intent"] == "order_request"
    # Should NOT have payment info yet
    assert "BCA" not in data["message"]
    assert "Pengiriman Oktober 2026" in data["message"]
    assert "Size: L" in data["message"]


def test_chat_payment_notification():
    # 2. Second message: full form details (triggers handover + payment info)
    response = client.post("/chat", json={
        "conversation_id": "test-order-001",
        "customer_id": "cust-001",
        "message": "Nama: Fariz, Alamat: Jl. Sukabumi No 1, No telp: 08123456789"
    })
    assert response.status_code == 200
    data = response.json()
    assert data["handover"] is True
    # Should have payment info
    assert "Bank BCA" in data["message"]
    assert "5790318864" in data["message"]
