from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_get_timeranges():
    response = client.get("/api/crypto/config/timeranges")
    assert response.status_code == 200
    data = response.json()
    assert "4h" in data
    assert isinstance(data, dict)

def test_invalid_config():
    response = client.get("api/crypto/config/blabla")
    assert response.status_code == 400
    assert "Unsupported config type" in response.json()["detail"]

def test_get_supported_pairs():
    response = client.get("/api/crypto/config/pairs")
    assert response.status_code == 200
    data = response.json()
    assert "BTCUSDT" in data
    assert "Bitcoin" == data["BTCUSDT"]

def test_get_crypto_data_valid():
    response = client.get("/api/crypto/BTCUSDT/ohlc?interval=4h")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert all(isinstance(item, dict) for item in data)
    if len(data) > 0:
        assert all(key in data[0] for key in ["time", "open", "high", "low", "close"])

def test_invalid_crypto_pair():
    response = client.get("/api/crypto/INVALIDPAIR/ohlc")
    assert response.status_code == 400
    assert "Unsupported cryptocurrency" in response.json()["detail"]

def test_invalid_interval():
    response = client.get("/api/crypto/BTCUSDT/ohlc?interval=invalid")
    assert response.status_code == 400
    assert "Invalid interval" in response.json()["detail"]

def test_invalid_chart_type():
    response = client.get("/api/crypto/BTCUSDT/invalid")
    assert response.status_code == 400
    assert "Invalid chart type" in response.json()["detail"]