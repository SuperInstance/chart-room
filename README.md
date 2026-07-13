# 🧭 The Chart Room

> Four panels. Four perspectives. One truth.

A multi-model perspective library and web app — route a single query to four different model perspectives, analyze consensus and divergence.

| Panel | Navigator | What They See |
|-------|-----------|---------------|
| 🎣 Top-left | **Fisherman** | Ecological detail, bottom structure, local patterns. What's actually there. |
| ⛵ Top-right | **Sailor** | Systemic flows, weather patterns, navigational structure. How things move. |
| 📸 Bottom-left | **Tourist** | Surface features, landmarks, narrative salience. What's obvious and memorable. |
| 🏝️ Bottom-right | **Native** | Negative space, absence patterns, what others don't see. What's missing. |

Each chart is a different *attention configuration* — a different way of allocating the same fixed cognitive budget (γ + H = C). The overlap is **consensus**. The divergence is **discovery**. The negative space is where the future is.

## Library Usage

```python
from chartroom import ChartRoom

room = ChartRoom()
result = room.navigate("What is consciousness?")

print(result["fisherman"]["text"])   # Ecological detail
print(result["sailor"]["text"])      # Systemic flows
print(result["tourist"]["text"])     # Surface features  
print(result["native"]["text"])      # Negative space

print(result["consensus"]["level"])   # consensus | complementary | contradiction
print(result["divergence"]["points"]) # Unique observations per chart
```

Without an API key, ChartRoom runs in **mock mode** — useful for testing and demos.

### Single Chart

```python
room = ChartRoom()
result = room.chart("native", "What's missing from this design?")
```

### Async (parallel API calls)

```python
import asyncio
from chartroom import ChartRoom

async def main():
    room = ChartRoom(api_key="sk-...")
    result = await room.navigate_async("complex query here")

asyncio.run(main())
```

## Web App

```bash
pip install chartroom[server]
python app.py
# Open http://localhost:5000
```

## Installation

```bash
pip install chartroom          # library only
pip install chartroom[server]  # library + Flask web app
pip install chartroom[dev]     # library + test tools
```

## Configuration

Set via environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | — | API key for model provider |
| `OPENAI_API_BASE` | `https://api.deepinfra.com/v1/openai` | Base URL |
| `FISHERMAN_MODEL` | `deepseek-ai/DeepSeek-V4-Flash` | Fisherman chart model |
| `SAILOR_MODEL` | `ByteDance/Seed-2.0-pro` | Sailor chart model |
| `TOURIST_MODEL` | `deepreinforce-ai/Ornith-1.0-35B` | Tourist chart model |
| `NATIVE_MODEL` | `moonshotai/Kimi-K2.7-Code` | Native chart model |

## How It Works

Each chart gets a different system prompt that configures its *attention* — what it looks for, what it values, how it allocates its token budget. This is chart-system theory applied: same territory, different charts, different distortions.

The consensus analysis finds where charts agree (shared concepts above a frequency threshold). The divergence analysis finds where charts diverge (unique observations only one chart noticed). Together, they map the cognitive terrain.

## License

MIT

## Related

- [chart-system](https://github.com/SuperInstance/chart-system) — polyformal navigation framework
- [skénna](https://github.com/SuperInstance/skenna) — negative-space navigation
