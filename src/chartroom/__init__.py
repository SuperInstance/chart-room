"""
ChartRoom — Multi-model perspective library.

Route a single query to four different model perspectives, analyze
consensus and divergence. Each chart is a different attention configuration
looking at the same thing.

Usage:
    from chartroom import ChartRoom

    room = ChartRoom()
    result = room.navigate("What is consciousness?")
    print(result["consensus"])
    print(result["divergence"])

Without an API key, ChartRoom runs in mock mode — useful for testing,
demos, and development.
"""

from chartroom.engine import ChartRoom, CHART_CONFIG
from chartroom.analysis import find_consensus, find_divergence
from chartroom.chart_bridge import (
    chart_configs_from_system,
    get_chart_observations,
    HAS_CHART_SYSTEM,
)

__version__ = "0.2.0"
__author__ = "SuperInstance"
__license__ = "MIT"

__all__ = [
    "ChartRoom",
    "CHART_CONFIG",
    "find_consensus",
    "find_divergence",
    "chart_configs_from_system",
    "get_chart_observations",
    "HAS_CHART_SYSTEM",
]
