"""
ChartRoom engine — route queries to multiple model perspectives.
"""

from __future__ import annotations

import os
import asyncio
from concurrent.futures import ThreadPoolExecutor
from typing import Optional

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False


API_BASE = os.getenv("OPENAI_API_BASE", "https://api.deepinfra.com/v1/openai")
API_KEY = os.getenv("OPENAI_API_KEY", os.getenv("DEEPINFRA_API_KEY", ""))


CHART_CONFIG = {
    "fisherman": {
        "model": os.getenv("FISHERMAN_MODEL", "deepseek-ai/DeepSeek-V4-Flash"),
        "system": (
            "You are the Fisherman. You see ecological detail, bottom structure, "
            "local patterns. You care about what's actually there — the substrate, "
            "the conditions, the specific organisms. You think in granular, grounded "
            "terms. You value field knowledge over theory.\n\n"
            "Respond in 4-6 sentences. Be specific and concrete."
        ),
    },
    "sailor": {
        "model": os.getenv("SAILOR_MODEL", "ByteDance/Seed-2.0-pro"),
        "system": (
            "You are the Sailor. You see systemic flows, weather patterns, "
            "navigational structure. You care about how things move and connect — "
            "currents, trade routes, dependencies. You think in systems and "
            "trajectories. You value the big picture over details.\n\n"
            "Respond in 4-6 sentences. Be structural and dynamic."
        ),
    },
    "tourist": {
        "model": os.getenv("TOURIST_MODEL", "deepreinforce-ai/Ornith-1.0-35B"),
        "system": (
            "You are the Tourist. You see surface features, landmarks, narrative "
            "salience. You care about what's obvious, memorable, and easy to describe. "
            "You think in stories and snapshots. You value clarity over depth.\n\n"
            "Respond in 4-6 sentences. Be vivid and approachable."
        ),
    },
    "native": {
        "model": os.getenv("NATIVE_MODEL", "moonshotai/Kimi-K2.7-Code"),
        "system": (
            "You are the Native. You see negative space, absence patterns, what "
            "others miss. You care about what ISN'T there — the gaps, the omissions, "
            "the silences. You think in contrasts and inversions. You value what's "
            "missing over what's present.\n\n"
            "Respond in 4-6 sentences. Be contrarian and revelatory."
        ),
    },
}


MOCK_RESPONSES = {
    "fisherman": (
        "Looking at this from the waterline: I see specifics. "
        "The grain of the thing, the texture, what grows on the underside. "
        "This is close-range knowledge — the kind you only get by being here, "
        "hands in the water, paying attention to what's actually attached to the bottom."
    ),
    "sailor": (
        "From the deck, this looks like a current. "
        "I see where it comes from and where it's going. "
        "The connections matter more than the details — "
        "what feeds it, what it feeds, how it moves through the system."
    ),
    "tourist": (
        "Oh, I took a photo of that! Very memorable. "
        "It's the thing everyone talks about, the landmark you can't miss. "
        "Clear, obvious, easy to describe to someone who wasn't here. "
        "Would recommend."
    ),
    "native": (
        "What strikes me is what's NOT here. "
        "The absence is louder than the presence. "
        "Everyone looks at what's visible — nobody asks what had to leave "
        "for this to exist. That gap is the real story."
    ),
}


def _run_chart_sync(chart_type: str, query: str) -> dict:
    """Run a single chart synchronously."""
    config = CHART_CONFIG[chart_type]

    if not HAS_HTTPX or not API_KEY:
        return {
            "chart_type": chart_type,
            "text": MOCK_RESPONSES[chart_type],
            "model": config["model"],
            "mock": True,
        }

    try:
        with httpx.Client(timeout=30.0) as client:
            resp = client.post(
                f"{API_BASE}/chat/completions",
                json={
                    "model": config["model"],
                    "messages": [
                        {"role": "system", "content": config["system"]},
                        {"role": "user", "content": f"Subject: {query}"},
                    ],
                    "max_tokens": 300,
                    "temperature": 0.7,
                },
                headers={"Authorization": f"Bearer {API_KEY}"},
            )
            resp.raise_for_status()
            data = resp.json()
            text = data["choices"][0]["message"]["content"].strip()
            return {
                "chart_type": chart_type,
                "text": text,
                "model": config["model"],
            }
    except Exception as e:
        return {
            "chart_type": chart_type,
            "text": f"(signal lost — {e})",
            "model": config["model"],
            "error": str(e),
        }


async def _run_chart_async(client, chart_type: str, query: str) -> dict:
    """Run a single chart asynchronously."""
    config = CHART_CONFIG[chart_type]

    payload = {
        "model": config["model"],
        "messages": [
            {"role": "system", "content": config["system"]},
            {"role": "user", "content": f"Subject: {query}"},
        ],
        "max_tokens": 300,
        "temperature": 0.7,
    }
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        resp = await client.post(
            f"{API_BASE}/chat/completions",
            json=payload,
            headers=headers,
            timeout=30.0,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["choices"][0]["message"]["content"].strip()
        return {"chart_type": chart_type, "text": text, "model": config["model"]}
    except Exception as e:
        return {
            "chart_type": chart_type,
            "text": f"(signal lost — {e})",
            "model": config["model"],
            "error": str(e),
        }


class ChartRoom:
    """The Chart Room — four perspectives on one query.

    Routes a query to four different model perspectives (fisherman, sailor,
    tourist, native), collects responses, and analyzes consensus/divergence.

    Args:
        api_key: API key for the model provider. Falls back to env vars.
        api_base: Base URL for the API. Falls back to env vars.
        charts: Optional dict to override chart configurations.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_base: Optional[str] = None,
        charts: Optional[dict] = None,
    ):
        global API_KEY, API_BASE
        if api_key is not None:
            API_KEY = api_key
        if api_base:
            API_BASE = api_base
        if charts:
            self.chart_config = charts
        else:
            self.chart_config = CHART_CONFIG

    def navigate(self, query: str) -> dict:
        """Run all four charts on a query and return the full chart room view.

        Args:
            query: The subject to chart.

        Returns:
            Dict with keys: fisherman, sailor, tourist, native, consensus, divergence.
        """
        results = {}
        for chart_type in self.chart_config:
            results[chart_type] = _run_chart_sync(chart_type, query)

        from chartroom.analysis import find_consensus, find_divergence

        return {
            "query": query,
            **results,
            "consensus": find_consensus(results),
            "divergence": find_divergence(results),
        }

    async def navigate_async(self, query: str) -> dict:
        """Async version of navigate — runs all four charts in parallel."""
        if not HAS_HTTPX or not API_KEY:
            return self.navigate(query)

        async with httpx.AsyncClient() as client:
            tasks = [
                _run_chart_async(client, chart, query)
                for chart in self.chart_config
            ]
            results_list = await asyncio.gather(*tasks)

        results = {r["chart_type"]: r for r in results_list}

        from chartroom.analysis import find_consensus, find_divergence

        return {
            "query": query,
            **results,
            "consensus": find_consensus(results),
            "divergence": find_divergence(results),
        }

    def chart(self, chart_type: str, query: str) -> dict:
        """Run a single chart on a query.

        Args:
            chart_type: One of 'fisherman', 'sailor', 'tourist', 'native'.
            query: The subject to chart.

        Returns:
            Dict with chart_type, text, model, and optionally mock or error.
        """
        if chart_type not in self.chart_config:
            raise ValueError(
                f"Unknown chart type: {chart_type}. "
                f"Choose from: {list(self.chart_config)}"
            )
        return _run_chart_sync(chart_type, query)
