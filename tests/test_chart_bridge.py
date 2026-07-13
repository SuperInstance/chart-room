"""Tests for chart-system bridge integration."""

import pytest
from chartroom.chart_bridge import (
    chart_configs_from_system,
    get_chart_observations,
    HAS_CHART_SYSTEM,
)


class TestChartBridge:
    def test_has_chart_system_or_graceful(self):
        """Either chart-system is available or the bridge degrades gracefully."""
        assert isinstance(HAS_CHART_SYSTEM, bool)

    @pytest.mark.skipif(not HAS_CHART_SYSTEM, reason="chart-system not installed")
    def test_configs_from_system(self):
        configs = chart_configs_from_system()
        assert configs is not None
        assert "fisherman" in configs
        assert "sailor" in configs
        assert "tourist" in configs
        assert "native" in configs

    @pytest.mark.skipif(not HAS_CHART_SYSTEM, reason="chart-system not installed")
    def test_config_has_gamma_ratio(self):
        configs = chart_configs_from_system()
        assert "gamma_ratio" in configs["fisherman"]
        assert configs["fisherman"]["gamma_ratio"] > 0

    @pytest.mark.skipif(not HAS_CHART_SYSTEM, reason="chart-system not installed")
    def test_config_has_eta_ratio(self):
        configs = chart_configs_from_system()
        assert "eta_ratio" in configs["native"]
        assert configs["native"]["eta_ratio"] >= 0

    @pytest.mark.skipif(not HAS_CHART_SYSTEM, reason="chart-system not installed")
    def test_get_chart_observations_fisherman(self):
        from chart_system.charts import Observation
        obs = [
            Observation(location="A", signal="abundance", value=0.8),
            Observation(location="A", signal="current", value=0.5),
        ]
        result = get_chart_observations("fisherman", obs)
        assert result is not None
        # Fisherman should see abundance but not current
        signals = {o.signal for o in result.positive_observations}
        assert "abundance" in signals
        assert "current" not in signals

    @pytest.mark.skipif(not HAS_CHART_SYSTEM, reason="chart-system not installed")
    def test_get_chart_observations_unknown(self):
        result = get_chart_observations("nonexistent", [])
        assert result is None
