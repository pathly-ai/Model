from __future__ import annotations

import json
from typing import Any, Dict, List

from fastapi.testclient import TestClient

# Import the FastAPI app from api.py
from api import app


def assert_condition(cond: bool, message: str) -> None:
    if not cond:
        raise AssertionError(message)


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert_condition(r.status_code == 200, f"/health status != 200: {r.status_code}, body={r.text}")
    data = r.json()
    assert_condition(data.get("status") == "ok", f"/health payload unexpected: {data}")


def test_predict(client: TestClient) -> Dict[str, Any]:
    payload = {
        "p1": "I like to build websites",
        "s1": ["javascript", "react", "css"],
        "i2": "frontend development",
    }
    r = client.post("/predict", json=payload)
    assert_condition(r.status_code == 200, f"/predict status != 200: {r.status_code}, body={r.text}")
    data = r.json()
    recs: List[Dict[str, Any]] = data.get("recommendations", [])
    assert_condition(len(recs) == 3, f"/predict expected 3 recommendations, got {len(recs)}: {recs}")

    required_fields = {
        "title",
        "matchPercentage",
        "description",
        "category",
        "salaryRange",
        "growthRate",
        "location",
        "requiredSkills",
        "educationPath",
        "examsCertifications",
        "jobOutlook",
        "workEnvironment",
    }
    for idx, rec in enumerate(recs):
        missing = required_fields - set(rec.keys())
        assert_condition(not missing, f"/predict rec[{idx}] missing fields: {missing}; rec={rec}")
        assert_condition(0 <= rec["matchPercentage"] <= 100, f"/predict rec[{idx}] bad matchPercentage: {rec['matchPercentage']}")
    return data


def test_chat_basic(client: TestClient) -> None:
    # Chatbot returns 200 either way: if GEMINI_API_KEY is missing (message explaining that),
    # or a valid model-generated response if configured.
    payload = {"message": "Hi! Can you help me explore careers?", "sessionId": "smoke-test"}
    r = client.post("/chatbot", json=payload)
    assert_condition(r.status_code == 200, f"/chatbot status != 200: {r.status_code}, body={r.text}")
    data = r.json()
    assert_condition("response" in data, f"/chatbot payload missing 'response': {data}")


def test_predict_empty_400(client: TestClient) -> None:
    # Empty payload should be rejected with 400
    r = client.post("/predict", json={})
    assert_condition(r.status_code == 400, f"/predict empty should be 400, got {r.status_code}, body={r.text}")


def test_chat_with_recs(client: TestClient) -> None:
    # Use predict output as recommendations for chatbot
    pr = client.post("/predict", json={
        "p1": "I enjoy data and ML",
        "s1": ["python", "pandas", "sklearn"],
        "i2": "machine learning"
    })
    assert_condition(pr.status_code == 200, f"/predict for chat failed: {pr.status_code}")
    recs = pr.json()["recommendations"]
    payload = {
        "message": "Given these recommendations, what should I learn next?",
        "sessionId": "smoke-test-recs",
        "recommendations": recs
    }
    r = client.post("/chatbot", json=payload)
    # Either live response (200) or friendly fallback (still 200)
    assert_condition(r.status_code == 200, f"/chatbot with recs status != 200: {r.status_code}, body={r.text}")


if __name__ == "__main__":
    errors: List[str] = []
    results: Dict[str, Any] = {}
    
    with TestClient(app) as client:
        try:
            test_health(client)
            results["health"] = "ok"
        except Exception as e:
            errors.append(f"health: {e}")
        
        try:
            results["predict"] = test_predict(client)
            test_predict_empty_400(client)
            results["predict_empty"] = "ok"
        except Exception as e:
            errors.append(f"predict: {e}")
        
        try:
            test_chat_basic(client)
            test_chat_with_recs(client)
            results["chatbot"] = "ok"
        except Exception as e:
            errors.append(f"chatbot: {e}")
    
    print("SMOKE TEST RESULTS:\n" + json.dumps(results, indent=2))
    if errors:
        print("\nFAILURES:\n" + "\n".join(errors))
        raise SystemExit(1)
    else:
        print("\nAll smoke tests passed.")
