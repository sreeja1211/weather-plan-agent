import asyncio
import json
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# The agent starts your MCP server itself, using the same Python as your venv
SERVER = StdioServerParameters(command=sys.executable, args=["server.py"])


async def fetch_forecast(city: str, day_offset: int) -> dict:
    """Connect to the MCP server and call the get_forecast tool."""
    async with stdio_client(SERVER) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            result = await session.call_tool(
                "get_forecast", {"city": city, "day_offset": day_offset}
            )
            return json.loads(result.content[0].text)


def score_slot(slot: dict) -> tuple[int, list[str]]:
    """Score a time slot from 0 to 100 for running. Higher is better."""
    score = 100
    notes = []

    rain = slot["rain_chance_pct"]
    feels = slot["feels_like_c"]
    humidity = slot["humidity_pct"]

    if rain >= 60:
        score -= 50
        notes.append(f"high rain chance ({rain}%)")
    elif rain >= 30:
        score -= 20
        notes.append(f"some rain chance ({rain}%)")

    if feels >= 35:
        score -= 50
        notes.append(f"dangerously hot, feels like {feels}°C")
    elif feels >= 32:
        score -= 30
        notes.append(f"hot, feels like {feels}°C")
    elif feels >= 29:
        score -= 10
        notes.append(f"warm, feels like {feels}°C")

    if humidity >= 85:
        score -= 15
        notes.append(f"very humid ({humidity}%)")

    return score, notes


def decide(forecast: dict) -> str:
    """Pick the best run window and build the advice."""
    morning_score, morning_notes = score_slot(forecast["morning_6am"])
    evening_score, evening_notes = score_slot(forecast["evening_6pm"])

    if morning_score >= evening_score:
        best, best_score, notes = "6 AM", morning_score, morning_notes
    else:
        best, best_score, notes = "6 PM", evening_score, evening_notes

    if best_score >= 80:
        verdict = f"✅ Good to run. Best time: {best}."
    elif best_score >= 50:
        verdict = f"⚠️ Okay to run with care. Best time: {best}."
    else:
        verdict = "❌ Skip the outdoor run. Try a treadmill or rest day."

    advice = [verdict]
    if notes:
        advice.append("Watch out: " + ", ".join(notes) + ".")
    if forecast["uv_index_max"] >= 8:
        advice.append("UV is high at midday, so avoid running 11 AM to 3 PM.")
    if forecast["morning_6am"]["humidity_pct"] >= 85 or forecast["evening_6pm"]["humidity_pct"] >= 85:
        advice.append("Carry water and go slower than your usual pace.")
    return "\n".join(advice)


async def main():
    city = input("City (default Chennai): ").strip() or "Chennai"
    day = input("Today or tomorrow? (default tomorrow): ").strip().lower()
    day_offset = 0 if day == "today" else 1

    forecast = await fetch_forecast(city, day_offset)

    if "error" in forecast:
        print(forecast["error"])
        return

    print(f"\n📍 {forecast['city']} on {forecast['date']}")
    print(f"🌡️  {forecast['temp_min_c']}°C to {forecast['temp_max_c']}°C, "
          f"max rain chance {forecast['rain_chance_max_pct']}%")
    print(f"🌅 6 AM: {forecast['morning_6am']}")
    print(f"🌇 6 PM: {forecast['evening_6pm']}\n")
    print(decide(forecast))


if __name__ == "__main__":
    asyncio.run(main())