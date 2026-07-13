"""Tests for the chartroom library."""

import pytest
from chartroom import ChartRoom, find_consensus, find_divergence


class TestChartConfig:
    def test_four_charts_exist(self):
        from chartroom.engine import CHART_CONFIG
        assert set(CHART_CONFIG.keys()) == {"fisherman", "sailor", "tourist", "native"}

    def test_each_chart_has_model_and_system(self):
        from chartroom.engine import CHART_CONFIG
        for chart_type, config in CHART_CONFIG.items():
            assert "model" in config, f"{chart_type} missing model"
            assert "system" in config, f"{chart_type} missing system prompt"
            assert len(config["system"]) > 20, f"{chart_type} system prompt too short"


class TestMockMode:
    def test_navigate_without_api_key(self):
        """ChartRoom should work in mock mode without an API key."""
        room = ChartRoom(api_key="")
        result = room.navigate("artificial intelligence")
        assert "fisherman" in result
        assert "sailor" in result
        assert "tourist" in result
        assert "native" in result
        assert result["fisherman"]["mock"] is True

    def test_mock_responses_are_distinct(self):
        room = ChartRoom(api_key="")
        result = room.navigate("test query")
        texts = [result[c]["text"] for c in ["fisherman", "sailor", "tourist", "native"]]
        assert len(set(texts)) == 4, "Mock responses should be distinct"

    def test_single_chart(self):
        room = ChartRoom(api_key="")
        result = room.chart("fisherman", "ocean currents")
        assert result["chart_type"] == "fisherman"
        assert len(result["text"]) > 10

    def test_invalid_chart_raises(self):
        room = ChartRoom(api_key="")
        with pytest.raises(ValueError, match="Unknown chart type"):
            room.chart("astronaut", "space")


class TestConsensus:
    def test_identical_texts_full_consensus(self):
        results = {
            "a": {"text": "testing consensus analysis function words"},
            "b": {"text": "testing consensus analysis function words"},
            "c": {"text": "testing consensus analysis function words"},
            "d": {"text": "testing consensus analysis function words"},
        }
        c = find_consensus(results)
        assert c["level"] == "consensus"

    def test_disjoint_texts_contradiction(self):
        results = {
            "a": {"text": "alpha beta gamma delta epsilon"},
            "b": {"text": "zeta eta theta iota kappa"},
            "c": {"text": "lambda mu nu xi omicron"},
            "d": {"text": "pi rho sigma tau upsilon"},
        }
        c = find_consensus(results)
        assert c["level"] == "contradiction"

    def test_empty_results(self):
        c = find_consensus({})
        assert c["level"] == "unknown"


class TestDivergence:
    def test_finds_unique_signals(self):
        results = {
            "a": {"text": "common words unusual_alpha signal"},
            "b": {"text": "common words unusual_beta signal"},
        }
        d = find_divergence(results)
        assert len(d["points"]) >= 2
        charts = [p["chart"] for p in d["points"]]
        assert "a" in charts
        assert "b" in charts

    def test_describes_divergence(self):
        results = {
            "a": {"text": "short"},
            "b": {"text": "short"},
        }
        d = find_divergence(results)
        assert "description" in d
        assert "type" in d


class TestNavigate:
    def test_returns_all_fields(self):
        room = ChartRoom(api_key="")
        result = room.navigate("consciousness")
        assert "query" in result
        assert "consensus" in result
        assert "divergence" in result

    def test_query_preserved(self):
        room = ChartRoom(api_key="")
        result = room.navigate("test subject 123")
        assert result["query"] == "test subject 123"
