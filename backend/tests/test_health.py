import sys
import os

# Add the parent directory (backend) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from fastapi.testclient import TestClient
from dotenv import load_dotenv
from main import app

load_dotenv()

client = TestClient(app)

def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"
    assert response.json()["services"]["api"] == "running"
    assert response.json()["services"]["openai"] == "configured"
    assert response.json()["services"]["qdrant"] == "configured"
    assert response.json()["services"]["database"] == "configured"
