"""
API Test Suite
Run with: pytest api/tests/ -v
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from api.main import app


@pytest.fixture
def client():
    return TestClient(app)


# ── Health & Root ──────────────────────────────────────────────────────────────

class TestHealth:
    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()


# ── News (no auth) ─────────────────────────────────────────────────────────────

class TestNews:
    def test_get_news(self, client):
        response = client.get("/api/news/Microsoft")
        assert response.status_code == 200
        data = response.json()
        assert "company_name" in data
        assert "articles" in data

    def test_get_news_with_limit(self, client):
        response = client.get("/api/news/Google?num_articles=3")
        assert response.status_code == 200
        assert len(response.json()["articles"]) <= 3


# ── Auth (no-login mode: dev user always returned) ────────────────────────────

class TestAuth:
    def test_me_returns_dev_user(self, client):
        """No token needed — always returns the local dev user."""
        response = client.get("/api/auth/me")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "email" in data


# ── Jobs (no auth gate on main branch) ────────────────────────────────────────

class TestJobs:
    def test_list_jobs(self, client):
        response = client.get("/api/jobs")
        assert response.status_code == 200
        assert isinstance(response.json(), list)

    def test_get_job_not_found(self, client):
        response = client.get("/api/jobs/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


# ── Cover Letters ──────────────────────────────────────────────────────────────

class TestCoverLetters:
    def test_list_cover_letters(self, client):
        response = client.get("/api/cover-letters")
        assert response.status_code == 200
        assert isinstance(response.json(), list)
