"""Tests verifying JWT enforcement on all protected routes (NFR-03/04)."""
import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.deps import create_access_token

client = TestClient(app)


def _auth_header() -> dict:
    token = create_access_token(data={"sub": "test-key"})
    return {"Authorization": f"Bearer {token}"}


def _expired_header() -> dict:
    from datetime import timedelta
    token = create_access_token(data={"sub": "test-key"}, expires_delta=timedelta(seconds=-10))
    return {"Authorization": f"Bearer {token}"}


# -- Unauthenticated access should be rejected (401) --

@pytest.mark.parametrize("method,path", [
    ("POST", "/api/v1/assess"),
    ("GET", "/api/v1/assessments"),
    ("GET", "/api/v1/reports/some-id"),
    ("POST", "/api/v1/whatif"),
    ("DELETE", "/api/v1/assessments/some-id"),
    ("DELETE", "/api/v1/data"),
    ("GET", "/api/v1/data/export"),
])
def test_unauthenticated_returns_401(method, path):
    resp = getattr(client, method.lower())(path)
    assert resp.status_code == 401, f"{method} {path} returned {resp.status_code}, expected 401"


# -- Expired token should be rejected --

@pytest.mark.parametrize("method,path", [
    ("GET", "/api/v1/assessments"),
    ("GET", "/api/v1/data/export"),
])
def test_expired_token_returns_401(method, path):
    resp = getattr(client, method.lower())(path, headers=_expired_header())
    assert resp.status_code == 401


# -- Valid token should be accepted --

def test_list_assessments_authenticated():
    resp = client.get("/api/v1/assessments", headers=_auth_header())
    assert resp.status_code == 200


def test_export_data_authenticated():
    resp = client.get("/api/v1/data/export", headers=_auth_header())
    assert resp.status_code == 200


# -- Health check is public --

def test_health_check_no_auth():
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


# -- Auth token endpoint --

def test_auth_token_wrong_key():
    resp = client.post("/api/v1/auth/token", json={"api_key": "wrong"})
    assert resp.status_code == 401
