# Minimal Function-Calling Agent (Python)

A minimal agent using OpenAI's Python SDK with function calling (tool use).

## Setup
1. Create and activate a virtual env (optional).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Set environment variables (use `.env` or shell):

```bash
export OPENAI_API_KEY=sk-...
# optional
export OPENAI_MODEL=gpt-4o-mini
export QUESTION="台北現在的天氣？"
```

## Run
```bash
python agent.py
```

## How it works
- Defines a Pydantic schema `WeatherRequest` for a tool.
- Lets the model decide whether to call the `fake_weather_api` tool.
- On tool call, executes it and returns a final combined answer.

## Notes
- Replace `fake_weather_api` with real APIs as needed.
- You can add more tools by extending the `tools` list and handlers.

## Architecture diagrams
- docs/diagrams/diagrams-1.svg — MVP+two-role control flow
- docs/diagrams/diagrams-2.svg — Complete two-layer control flow (reference)
- docs/diagrams/diagrams-3.svg — System Analyzer data flow
- docs/diagrams/diagrams-4.svg — Supervisor monitoring loop
- docs/diagrams/diagrams-updated-1.svg…5.svg — Updated set including Adapter layer

## Comparison vs other SDKs/LLMs
See the section below (in chat) for a concise comparison of Cursor agent style vs other major SDKs/LLMs.

