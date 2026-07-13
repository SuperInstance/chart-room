"""Bridge between chart-system formal types and chart-room runtime.

chart-system provides the formal definitions: ChartType, ChartProfile,
ChartConfiguration with γ allocations. chart-room provides the runtime
that dispatches queries to different model perspectives.

This bridge ensures chart-room's CHART_CONFIG stays synchronized with
chart-system's formal chart definitions.
"""

from __future__ import annotations

from typing import Any, Optional

try:
    from chart_system.charts import (
        ChartType as FormalChartType,
        ChartProfile,
        Chart,
        ChartFisherman,
        ChartSailor,
        ChartTourist,
        ChartNative,
    )
    from chart_system.configuration import (
        ChartConfiguration,
        get_configuration,
        DEFAULT_CONFIGURATIONS,
    )
    HAS_CHART_SYSTEM = True
except ImportError:
    HAS_CHART_SYSTEM = False
    FormalChartType = None
    ChartConfiguration = None


def chart_configs_from_system() -> Optional[dict[str, dict]]:
    """Build chart-room CHART_CONFIG entries from chart-system definitions.

    If chart-system is installed, this maps formal ChartProfiles to the
    runtime config format chart-room expects (model, system prompt, etc).

    Returns None if chart-system is not available.
    """
    if not HAS_CHART_SYSTEM:
        return None

    chart_models = {
        FormalChartType.FISHERMAN: "deepseek-ai/DeepSeek-V4-Flash",
        FormalChartType.SAILOR: "ByteDance/Seed-2.0-pro",
        FormalChartType.TOURIST: "deepreinforce-ai/Ornith-1.0-35B",
        FormalChartType.NATIVE: "moonshotai/Kimi-K2.7-Code",
    }

    configs: dict[str, dict] = {}
    for chart_type in FormalChartType:
        formal_profile: ChartProfile = None
        # Get the chart class for this type
        for cls in [ChartFisherman, ChartSailor, ChartTourist, ChartNative]:
            if cls.profile.chart_type == chart_type:
                formal_profile = cls.profile
                break

        if formal_profile is None:
            continue

        cfg = get_configuration(chart_type)
        configs[chart_type.value] = {
            "model": chart_models.get(chart_type, "unknown"),
            "system": formal_profile.description,
            "gamma_ratio": cfg.total_gamma_ratio,
            "eta_ratio": cfg.eta_ratio,
            "horizon": formal_profile.horizon,
            "abstraction_depth": formal_profile.abstraction_depth,
        }

    return configs


def get_chart_observations(
    chart_type_name: str,
    observations: list,
) -> Optional[Any]:
    """Process observations through a chart-system chart.

    If chart-system is available, instantiate the appropriate chart and
    run observations through it. Returns ChartOutput or None.

    Args:
        chart_type_name: One of 'fisherman', 'sailor', 'tourist', 'native'.
        observations: List of chart_system.charts.Observation objects.
    """
    if not HAS_CHART_SYSTEM:
        return None

    chart_map = {
        "fisherman": ChartFisherman,
        "sailor": ChartSailor,
        "tourist": ChartTourist,
        "native": ChartNative,
    }

    chart_cls = chart_map.get(chart_type_name)
    if chart_cls is None:
        return None

    chart: Chart = chart_cls()
    return chart.plot(observations)


__all__ = [
    "chart_configs_from_system",
    "get_chart_observations",
    "HAS_CHART_SYSTEM",
]
