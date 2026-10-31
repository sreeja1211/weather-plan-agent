import httpx
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-plan")

GEO_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"


async def get_coordinates(city: str):
    """Turn a city name into latitude/longitude (free Open-Meteo geocoding)."""
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(GEO_URL, params={"name": city, "count": 1})
        r.raise_for_status()
        results = r.json().get("results")
    if not results:
        return None
    place = results[0]
    return place["latitude"], place["longitude"], place["name"]


@mcp.tool()
async def get_forecast(city: str, day_offset: int = 1) -> dict:
    """Get the weather forecast for a city.
    day_offset: 0 = today, 1 = tomorrow, up to 6.
    Returns daily summary plus 6 AM and 6 PM details (good run windows)."""
    day_offset = max(0, min(day_offset, 6))

    coords = await get_coordinates(city)
    if coords is None:
        return {"error": f"Could not find city: {city}"}
    lat, lon, name = coords

    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max",
        "hourly": "apparent_temperature,relative_humidity_2m,precipitation_probability",
        "timezone": "auto",
        "forecast_days": day_offset + 1,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        r = await client.get(FORECAST_URL, params=params)
        r.raise_for_status()
        data = r.json()

    d = data["daily"]
    h = data["hourly"]

    def slot(hour: int) -> dict:
        i = day_offset * 24 + hour
        return {
            "feels_like_c": h["apparent_temperature"][i],
            "humidity_pct": h["relative_humidity_2m"][i],
            "rain_chance_pct": h["precipitation_probability"][i],
        }

    return {
        "city": name,
        "date": d["time"][day_offset],
        "temp_max_c": d["temperature_2m_max"][day_offset],
        "temp_min_c": d["temperature_2m_min"][day_offset],
        "rain_chance_max_pct": d["precipitation_probability_max"][day_offset],
        "uv_index_max": d["uv_index_max"][day_offset],
        "morning_6am": slot(6),
        "evening_6pm": slot(18),
    }


if __name__ == "__main__":
    mcp.run()