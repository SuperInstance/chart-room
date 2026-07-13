"""
Basic tests for the Chart Room backend.
Tests routes, consensus/divergence analysis, and mock responses.
"""

import pytest
import json

from app import app, _mock_response, find_consensus, find_divergence, CHART_CONFIG


@pytest.fixture
def client():
    """Flask test client."""
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    def test_health_returns_ok(self, client):
        resp = client.get("/health")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["status"] == "ok"
        assert "models" in data

    def test_health_lists_all_charts(self, client):
        resp = client.get("/health")
        data = resp.get_json()
        for chart in ("fisherman", "sailor", "tourist", "native"):
            assert chart in data["models"]


class TestChartEndpoint:
    def test_empty_query_returns_400(self, client):
        resp = client.post("/chart", json={"query": ""})
        assert resp.status_code == 400

    def test_missing_query_returns_400(self, client):
        resp = client.post("/chart", json={})
        assert resp.status_code == 400

    def test_valid_query_returns_all_charts(self, client):
        resp = client.post("/chart", json={"query": "ocean currents"})
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["query"] == "ocean currents"
        for chart in ("fisherman", "sailor", "tourist", "native"):
            assert chart in data
            assert "text" in data[chart]
        assert "consensus" in data
        assert "divergence" in data
        assert "elapsed_ms" in data


class TestMockResponse:
    def test_returns_text_for_each_chart(self):
        for chart_type in CHART_CONFIG:
            text = _mock_response(chart_type, "test query")
            assert isinstance(text, str)
            assert len(text) > 0

    def test_includes_query_in_response(self):
        text = _mock_response("fisherman", "unique_test_string")
        assert "unique_test_string" in text

    def test_unknown_chart_returns_fallback(self):
        text = _mock_response("nonexistent", "test")
        assert text == "No signal."


class TestConsensus:
    def test_returns_dict(self):
        results = {
            "fisherman": {"response": "The ocean is blue."},
            "sailor": {"response": "The sea appears blue."},
            "tourist": {"response": "The water is blue."},
            "native": {"response": "The ocean is blue and deep."},
        }
        consensus = find_consensus(results)
        assert isinstance(consensus, dict)

    def test_handles_empty_responses(self):
        results = {
            "fisherman": {"response": ""},
            "sailor": {"response": ""},
            "tourist": {"response": ""},
            "native": {"response": ""},
        }
        consensus = find_consensus(results)
        assert isinstance(consensus, dict)


class TestDivergence:
    def test_returns_dict(self):
        results = {
            "fisherman": {"response": "Fish and scales."},
            "sailor": {"response": "Waves and wind."},
            "tourist": {"response": "Beaches and photos."},
            "native": {"response": "History and loss."},
        }
        divergence = find_divergence(results)
        assert isinstance(divergence, dict)

    def test_handles_empty_responses(self):
        results = {
            "fisherman": {"response": ""},
            "sailor": {"response": ""},
            "tourist": {"response": ""},
            "native": {"response": ""},
        }
        divergence = find_divergence(results)
        assert isinstance(divergence, dict)


class TestIndexRoute:
    def test_index_returns_html(self, client):
        resp = client.get("/")
        assert resp.status_code == 200
