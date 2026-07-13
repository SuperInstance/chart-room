"""
Consensus and divergence analysis for ChartRoom results.
"""

from __future__ import annotations


def find_consensus(results: dict) -> dict:
    """Determine consensus level across charts.

    Heuristic analysis based on keyword overlap between chart responses.

    Args:
        results: Dict mapping chart_type to response dict (with 'text' key).

    Returns:
        Dict with level ('consensus', 'complementary', 'contradiction'),
        description, and overlap keywords.
    """
    texts = [r.get("text", "") for r in results.values()]
    chart_count = len([t for t in texts if t and not t.startswith("(")])

    if chart_count == 0:
        return {"level": "unknown", "description": "No signals received."}

    word_sets = []
    for text in texts:
        words = set(text.lower().split())
        words = {w for w in words if len(w) > 4}
        word_sets.append(words)

    if len(word_sets) >= 2:
        overlap = word_sets[0]
        for ws in word_sets[1:]:
            overlap = overlap & ws

        if len(overlap) >= 5:
            return {
                "level": "consensus",
                "description": f"Charts converge on {len(overlap)} shared concepts.",
                "overlap": sorted(overlap)[:10],
            }
        elif len(overlap) > 1:
            return {
                "level": "complementary",
                "description": f"Charts share {len(overlap)} concepts but diverge in focus.",
                "overlap": sorted(overlap)[:10],
            }
        else:
            return {
                "level": "contradiction",
                "description": "Charts see entirely different things.",
                "overlap": [],
            }

    return {"level": "unknown", "description": "Insufficient data."}


def find_divergence(results: dict) -> dict:
    """Identify key divergences between charts.

    Finds unique observations — signals only one chart noticed.

    Args:
        results: Dict mapping chart_type to response dict (with 'text' key).

    Returns:
        Dict with divergence type, unique points, and description.
    """
    texts = {k: v.get("text", "") for k, v in results.items()}

    all_words = set()
    chart_unique = {}
    for chart, text in texts.items():
        words = {w for w in text.lower().split() if len(w) > 5}
        chart_unique[chart] = words
        all_words = all_words | words

    divergence_points = []
    for word in all_words:
        seen_by = [c for c, ws in chart_unique.items() if word in ws]
        if len(seen_by) == 1:
            divergence_points.append({"signal": word, "chart": seen_by[0]})

    return {
        "type": "complementary" if len(divergence_points) > 3 else "constructive",
        "points": sorted(divergence_points, key=lambda p: p["chart"])[:10],
        "description": f"{len(divergence_points)} unique observations across charts.",
    }
