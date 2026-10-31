import httpx

url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": 13.0827,
    "longitude": 80.2707,
    "daily": "temperature_2m_max,temperature_2m_min,precipitation_probability_max,uv_index_max",
    "hourly": "temperature_2m,apparent_temperature,relative_humidity_2m",
    "timezone": "Asia/Kolkata",
    "forecast_days": 2,
}

r = httpx.get(url, params=params, timeout=10)
r.raise_for_status()
data = r.json()

print("DAILY:", data["daily"])
print("Tomorrow 6 AM feels like:", data["hourly"]["apparent_temperature"][30], "°C")
print("Tomorrow 6 AM humidity:", data["hourly"]["relative_humidity_2m"][30], "%")