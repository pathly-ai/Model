from __future__ import annotations

import json
from pathlib import Path

from fastapi.testclient import TestClient

# Import the app
import sys
import os
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from api import app  # noqa: E402


def test_health():
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json().get("status") == "ok"


def test_predict():
    payload = {
        "p1": "Small teams with close-knit relationships",
        "p2": "Analyze all possible solutions methodically",
        "p3": "Working on complex, challenging tasks",
        "s1": ["Mathematics and Statistics", "Problem Solving"],
        "s2": ["Data Analysis (Excel, SQL, Python)", "Web Development (HTML, CSS, JavaScript)"],
        "i1": ["Analyzing data and finding patterns", "Exploring new technologies"],
        "i2": "Work with cutting-edge technology",
        "v1": "Opportunities for advancement",
        "v2": "Continuous learning and growth",
        "v3": "innovative, research-driven"
    }
    with TestClient(app) as client:
        r = client.post("/predict", data=json.dumps(payload))
        assert r.status_code == 200, r.text
        data = r.json()
        assert "career_recommendation" in data
        assert isinstance(data["career_recommendation"], str)


def test_chatbot():
    with TestClient(app) as client:
        r = client.post("/chatbot", json={"message": "Which career suits me if I like design and coding?"})
        assert r.status_code == 200
        text = r.json().get("response", "")
        assert "UI/UX" in text or "Frontend" in text


if __name__ == "__main__":
    # Run tests ad-hoc
    test_health()
    test_predict()
    test_chatbot()
    print("All backend endpoint smoke tests passed.")
