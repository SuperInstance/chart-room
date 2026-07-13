# 🧭 The Chart Room

> Four panels. Four perspectives. One truth.

A visual interface for [chart-system](https://github.com/SuperInstance/chart-system) — the polyformal navigation framework for Working Animal Architecture.

---

## What Is This?

Drop a question into the Chart Room and four navigators look at it simultaneously:

| Panel | Navigator | What They See |
|-------|-----------|---------------|
| 🎣 Top-left | **Fisherman** | Ecological detail, bottom structure, local patterns. What's actually there. |
| ⛵ Top-right | **Sailor** | Systemic flows, weather patterns, navigational structure. How things move. |
| 📸 Bottom-left | **Tourist** | Surface features, landmarks, narrative salience. What's obvious and memorable. |
| 🏝️ Bottom-right | **Native** | Negative space, absence patterns, what others don't see. What's missing. |

Each chart is a different *attention configuration* — a different way of allocating the same fixed cognitive budget (γ + H = C). The overlap is **consensus**. The divergence is **discovery**. The negative space is where the future is.

## The Interface

```
┌─────────────────┬─────────────────┐
│   🎣 FISHERMAN   │   ⛵ SAILOR      │
│   (detail/ecology) │   (flows/system) │
├─────────────────┼─────────────────┤
│   📸 TOURIST     │   🏝️ NATIVE     │
│   (surface/story) │   (absence/gaps) │
└─────────────────┴─────────────────┘
         [ What are you looking at? ]
```

- **Center indicator** shows consensus (🟢 green), complementary findings (🟡 yellow), or contradictions (🔴 red)
- Each quadrant streams independently — different models, different latencies, different truths
- The same observation passes through all four charts. What differs is what each chart *chooses to see*

## Quick Start

### Docker (recommended)

```bash
docker run -p 5000:5000 ghcr.io/superinstance/chart-room
```

Open `http://localhost:5000`

### Local

```bash
pip install -r requirements.txt
python app.py
```

### Configure Models

Set any of these environment variables to route quadrants to different LLM backends:

```bash
export FISHERMAN_MODEL="deepseek-ai/DeepSeek-V4-Flash"
export SAILOR_MODEL="byteDance/Seed-2.0-pro"
export TOURIST_MODEL="deepreinforce-ai/Ornith-1.0-35B"
export NATIVE_MODEL="moonshotai/Kimi-K2.7-Code"
export OPENAI_API_BASE="https://api.deepinfra.com/v1/openai"
export OPENAI_API_KEY="your-key"
```

Each panel runs its own model. Different perspectives, literally.

## How It Works

```
User Input ──────┬──▶ Fisherman Model ──▶ Panel 1
                 ├──▶ Sailor Model ─────▶ Panel 2
                 ├──▶ Tourist Model ────▶ Panel 3
                 └──▶ Native Model ─────▶ Panel 4
                                              │
                         ◀── Consensus/Divergence Analysis ──▶
```

The backend (`app.py`) dispatches the same query to four model endpoints in parallel, then runs divergence analysis to compute the center indicator:

- **🟢 Consensus** — All charts converge. High confidence answer.
- **🟡 Complementary** — Charts see different facets. Richer picture.
- **🔴 Contradiction** — Charts disagree. Something interesting is happening.

## API

### `POST /chart`

```json
{
  "query": "What are you looking at?"
}
```

Response:

```json
{
  "fisherman": { "chart_type": "fisherman", "observations": [...], "coverage": [...] },
  "sailor": { "chart_type": "sailor", "observations": [...], "coverage": [...] },
  "tourist": { "chart_type": "tourist", "observations": [...], "coverage": [...] },
  "native": { "chart_type": "native", "observations": [...], "coverage": [...] },
  "consensus": { "level": "complementary", "overlap": [...], "description": "..." },
  "divergence": { "type": "complementary", "locations": [...], "description": "..." }
}
```

## Philosophy

From the Conservation Law of Intelligence: γ + H = C.

You can't see everything. Every way of looking is a way of not-looking. The Fisherman sees the bottom but misses the weather. The Sailor reads the wind but can't see the fish. The Tourist sees the landmark but not the ecosystem. The Native sees the absence but not the surface.

**The Chart Room doesn't try to merge them into one view. It shows all four, side by side, and lets you navigate the spaces between them.**

## License

MIT

## Related

- [chart-system](https://github.com/SuperInstance/chart-system) — The Python library this interface runs on
- [Working Animal Architecture](https://github.com/SuperInstance/working-animal-architecture) — The theoretical framework
