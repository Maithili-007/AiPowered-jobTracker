import pytest
import json
import time
from app import app  # Import your Flask app
import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

# ✅ Test 1: Valid request returns keywords
def test_extract_keywords(client):
    payload = {
        "description": "We are looking for a Python developer with experience in Flask and machine learning."
    }
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 200
    data = response.get_json()
    assert "keywords" in data
    assert isinstance(data["keywords"], list)
    assert len(data["keywords"]) > 0
    assert any("Python" in kw or "Flask" in kw for kw in data["keywords"])

# ✅ Test 2: Empty description
def test_empty_description(client):
    payload = {"description": ""}
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 200
    data = response.get_json()
    assert "keywords" in data
    assert isinstance(data["keywords"], list)

# ✅ Test 3: Missing description key
def test_missing_description_key(client):
    payload = {}
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")

    assert response.status_code == 200
    data = response.get_json()
    assert "keywords" in data
    assert isinstance(data["keywords"], list)

# ✅ Test 4: Invalid JSON
def test_invalid_json(client):
    invalid_payload = "not json"
    response = client.post("/extract-keywords", data=invalid_payload, content_type="application/json")

    assert response.status_code in [400, 500]

# ✅ Test 5: Performance test (under 2 seconds)
def test_performance(client):
    payload = {"description": " ".join(["Python Flask AI Machine Learning"] * 50)}
    start = time.time()
    response = client.post("/extract-keywords", data=json.dumps(payload), content_type="application/json")
    elapsed = time.time() - start

    assert response.status_code == 200
    assert elapsed < 2.0
