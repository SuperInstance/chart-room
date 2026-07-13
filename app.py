#!/usr/bin/env python3
"""
The Chart Room — Backend
========================
Routes a single query to four different model perspectives,
runs divergence analysis, and returns the full chart room view.

Each chart is a different attention configuration looking at the same thing.
The overlap is consensus. The divergence is discovery. The negative space
is where the future is.

Run:  python app.py
Open: http://localhost:5000
"""

from __future__ import annotations

import os
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, request, jsonify, send_from_directory

try:
    import httpx
    HAS_HTTPX = True
except ImportError:
    HAS_HTTPX = False

app = Flask(__name__, static_folder=None)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

API_BASE = os.getenv("OPENAI_API_BASE", "https://api.deepinfra.com/v1/openai")
API_KEY = os.getenv("OPENAI_API_KEY", os.getenv("DEEPINFRA_API_KEY", ""))

# Each chart gets its own model — different perspectives, literally
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
        "accent": "brine",
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
        "accent": "foam",
    },
    "tourist": {
        "model": os.getenv("TOURIST_MODEL", "deepreinforce-ai/Ornith-1.0-35B"),
        "system": (
            "You are the Tourist. You see surface features, landmarks, narrative "
            "salience. You care about what's obvious, memorable, and easy to describe. "
            "You think in stories and snapshots. You value clarity over depth.\n\n"
            "Respond in 4-6 sentences. Be vivid and approachable."
        ),
        "accent": "rust",
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
        "accent": "brass",
    },
}


# ---------------------------------------------------------------------------
# Chart generation
# ---------------------------------------------------------------------------

async def run_chart(client: httpx.AsyncClient, chart_type: str, query: str) -> dict:
    """Run a single chart perspective on the query."""
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


def chart_fisherman(query: str) -> dict:
    """Fisherman's chart: detail, ecology, bottom structure."""
    return _run_sync("fisherman", query)


def chart_sailor(query: str) -> dict:
    """Sailor's chart: flows, patterns, system-level view."""
    return _run_sync("sailor", query)


def chart_tourist(query: str) -> dict:
    """Tourist's chart: surface, landmarks, narrative."""
    return _run_sync("tourist", query)


def chart_native(query: str) -> dict:
    """Native's chart: negative space, absence, what's missing."""
    return _run_sync("native", query)


def _run_sync(chart_type: str, query: str) -> dict:
    """Run a chart synchronously (for non-async callers)."""
    if not HAS_HTTPX or not API_KEY:
        return {
            "chart_type": chart_type,
            "text": _mock_response(chart_type, query),
            "model": CHART_CONFIG[chart_type]["model"],
            "mock": True,
        }

    try:
        with httpx.Client(timeout=30.0) as client:
            config = CHART_CONFIG[chart_type]
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
            "model": CHART_CONFIG[chart_type]["model"],
            "error": str(e),
        }


async def run_all_charts(query: str) -> dict:
    """Run all four charts in parallel."""
    if not HAS_HTTPX or not API_KEY:
        # Fallback to mock mode
        return {
            chart: _run_sync(chart, query) for chart in CHART_CONFIG
        }

    async with httpx.AsyncClient() as client:
        tasks = [run_chart(client, chart, query) for chart in CHART_CONFIG]
        results = await asyncio.gather(*tasks)

    return {r["chart_type"]: r for r in results}


# ---------------------------------------------------------------------------
# Consensus & Divergence
# ---------------------------------------------------------------------------

def find_consensus(results: dict) -> dict:
    """
    Determine consensus level across the four charts.

    This is a lightweight heuristic. For full divergence analysis,
    use chart_system.divergence.DivergenceAnalyzer.
    """
    texts = [r.get("text", "") for r in results.values()]
    chart_count = len([t for t in texts if t and not t.startswith("(")])

    if chart_count == 0:
        return {"level": "unknown", "description": "No signals received."}

    # Simple keyword overlap heuristic
    word_sets = []
    for text in texts:
        words = set(text.lower().split())
        words = {w for w in words if len(w) > 4}  # skip short words
        word_sets.append(words)

    if len(word_sets) >= 2:
        overlap = word_sets[0]
        for ws in word_sets[1:]:
            overlap = overlap & ws

        if len(overlap) > 5:
            return {
                "level": "consensus",
                "description": f"Charts converge on {len(overlap)} shared concepts.",
                "overlap": list(overlap)[:10],
            }
        elif len(overlap) > 1:
            return {
                "level": "complementary",
                "description": f"Charts share {len(overlap)} concepts but diverge in focus.",
                "overlap": list(overlap)[:10],
            }
        else:
            return {
                "level": "contradiction",
                "description": "Charts see entirely different things.",
                "overlap": [],
            }

    return {"level": "unknown", "description": "Insufficient data."}


def find_divergence(results: dict) -> dict:
    """
    Identify key divergences between charts.

    Simplified heuristic version. The chart_system library provides
    DivergenceAnalyzer for rigorous analysis.
    """
    texts = {k: v.get("text", "") for k, v in results.items()}

    # Find unique themes per chart
    all_words = set()
    chart_unique = {}
    for chart, text in texts.items():
        words = {w for w in text.lower().split() if len(w) > 5}
        chart_unique[chart] = words
        all_words = all_words | words

    # Words only seen by one chart = divergence
    divergence_points = []
    for word in all_words:
        seen_by = [c for c, ws in chart_unique.items() if word in ws]
        if len(seen_by) == 1:
            divergence_points.append({"signal": word, "chart": seen_by[0]})

    return {
        "type": "complementary" if len(divergence_points) > 3 else "constructive",
        "points": divergence_points[:10],
        "description": f"{len(divergence_points)} unique observations across charts.",
    }


# ---------------------------------------------------------------------------
# Mock responses (when no API key configured)
# ---------------------------------------------------------------------------

def _mock_response(chart_type: str, query: str) -> str:
    mocks = {
        "fisherman": (
            f"Looking at \"{query}\" from the waterline: I see specifics. "
            "The grain of the thing, the texture, what grows on the underside. "
            "This is close-range knowledge — the kind you only get by being here, "
            "hands in the water, paying attention to what's actually attached to the bottom."
        ),
        "sailor": (
            f"From the deck, \"{query}\" looks like a current. "
            "I see where it comes from and where it's going. "
            "The connections matter more than the details — "
            "what feeds it, what it feeds, how it moves through the system."
        ),
        "tourist": (
            f"\"{query}\" — oh, I took a photo of that! Very memorable. "
            "It's the thing everyone talks about, the landmark you can't miss. "
            "Clear, obvious, easy to describe to someone who wasn't here. "
            "Would recommend."
        ),
        "native": (
            f"What strikes me about \"{query}\" is what's NOT here. "
            "The absence is louder than the presence. "
            "Everyone looks at what's visible — nobody asks what had to leave "
            "for this to exist. That gap is the real story."
        ),
    }
    return mocks.get(chart_type, "No signal.")


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)


@app.route("/chart", methods=["POST"])
def chart():
    """Main endpoint: run all four charts and return the full chart room view."""
    query = request.json.get("query", "").strip()
    if not query:
        return jsonify({"error": "No query provided."}), 400

    start = time.time()

    # Run all charts
    results = {}
    for chart_type in CHART_CONFIG:
        results[chart_type] = _run_sync(chart_type, query)

    # Analyze
    consensus = find_consensus(results)
    divergence = find_divergence(results)

    elapsed = time.time() - start

    return jsonify({
        "query": query,
        "fisherman": results["fisherman"],
        "sailor": results["sailor"],
        "tourist": results["tourist"],
        "native": results["native"],
        "consensus": consensus,
        "divergence": divergence,
        "elapsed_ms": round(elapsed * 1000),
    })


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "api_configured": bool(API_KEY),
        "api_base": API_BASE,
        "models": {k: v["model"] for k, v in CHART_CONFIG.items()},
    })


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    print(f"\n  🧭 THE CHART ROOM")
    print(f"  Four panels. Four perspectives. One truth.")
    print(f"\n  → http://localhost:{port}")
    print(f"\n  API: {'configured' if API_KEY else 'NOT configured (mock mode)'}")
    print(f"  Base: {API_BASE}")
    print(f"  Models:")
    for chart, config in CHART_CONFIG.items():
        print(f"    {chart:12s} → {config['model']}")
    print()

    app.run(host="0.0.0.0", port=port, debug=os.getenv("DEBUG", "0") == "1")
