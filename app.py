#!/usr/bin/env python3
"""
The Chart Room — Flask web app
==============================
Thin Flask wrapper around the chartroom library.

Run:  pip install chartroom[server]
      python app.py
Open: http://localhost:5000
"""

from __future__ import annotations

import os
import time

from flask import Flask, request, jsonify, send_from_directory
from chartroom import ChartRoom

app = Flask(__name__, static_folder=None)
room = ChartRoom()


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/<path:filename>")
def static_files(filename):
    return send_from_directory(".", filename)


@app.route("/chart", methods=["POST"])
def chart():
    """Run all four charts and return the full chart room view."""
    query = request.json.get("query", "").strip()
    if not query:
        return jsonify({"error": "No query provided."}), 400

    start = time.time()
    result = room.navigate(query)
    result["elapsed_ms"] = round((time.time() - start) * 1000)

    return jsonify(result)


@app.route("/health")
def health():
    return jsonify({
        "status": "ok",
        "api_configured": bool(os.getenv("OPENAI_API_KEY") or os.getenv("DEEPINFRA_API_KEY")),
        "models": {k: v["model"] for k, v in room.chart_config.items()},
    })


if __name__ == "__main__":
    port = int(os.getenv("PORT", "5000"))
    print(f"\n  🧭 THE CHART ROOM")
    print(f"  Four panels. Four perspectives. One truth.")
    print(f"\n  → http://localhost:{port}")
    print()
    app.run(host="0.0.0.0", port=port, debug=os.getenv("DEBUG", "0") == "1")
