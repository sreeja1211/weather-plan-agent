# Weather & Plan Agent 🏃‍♀️🌦️

An AI-agent project that answers "Should I go for a run tomorrow?" using live weather data.

## How it works
- **MCP server** (`server.py`): a custom Model Context Protocol server that wraps the free Open-Meteo API (no API key) and exposes a `get_forecast` tool.
- **Agent** (`agent.py`): an MCP client that calls the tool, scores the 6 AM and 6 PM running windows on rain chance, "feels like" temperature and humidity, and recommends the best time or a rest day.

## Run it
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python agent.py
```

## Test the server alone
```bash
npx @modelcontextprotocol/inspector python server.py
```

## Tech
Python, MCP (Model Context Protocol), httpx, asyncio, Open-Meteo API

## Example output
[paste a screenshot of your agent output here]

## Future improvements
- Add air quality (AQI) to the decision
- Natural-language answers using a free LLM
- Support multi-day run planning