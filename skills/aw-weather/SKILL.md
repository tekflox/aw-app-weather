---
name: aw-weather
description: Current conditions and a daily forecast for any place on Earth — temperature, feels-like, humidity, wind, precipitation, and rain chance up to 16 days out. Backed by the free Open-Meteo API through the aw-weather MCP server contributed by aw-app-weather. Use for any "what's the weather", "is it going to rain", "how hot is it in X" question.
---

# aw-weather — current conditions and forecast

Two tools, gateway-prefixed `aw__weather__*`. Ported from agentic-workspace's
`src/mcp/open_meteo.py` (2026-08-18) with the request formatting untouched —
results look exactly as they did there, condition text in Portuguese.

**No API key, no setup.** Open-Meteo is a free, keyless API — unlike
aw-google-maps or aw-google-workspace, there is nothing to configure and
nothing that expires. Both tools work the moment the app is installed.

## Which tool answers which question

| Question | Tool |
|---|---|
| "what's it like outside right now", "how hot is it in X" | `get_current_weather` |
| "will it rain this week", "what's the forecast for X" | `get_weather_forecast` |

### Both tools need coordinates, not place names

`get_current_weather(lat, lon)` and `get_weather_forecast(lat, lon, days)`
only take latitude/longitude. If the user names a place instead of giving
coordinates, resolve it first:

- `aw-google-maps`'s `geocode_address` (if that app is installed), or
- a mobile companion app's `get_location` for "here" / "my current location".

Do not guess coordinates from memory for anything more precise than a large
city — pass through geocoding instead.

### `get_weather_forecast` defaults and caps

`days` defaults to 3 and is capped at 16 (Open-Meteo's own limit) — a request
for `days=30` silently comes back with 16 days, not an error.

## Failure modes

| Symptom | Cause |
|---|---|
| "Weather lookup failed: ..." / "Forecast lookup failed: ..." | Open-Meteo returned an error — usually an out-of-range lat/lon. The `detail` in the message is Open-Meteo's own reason. |
| "lat and lon are required" | Called without coordinates — resolve a place name first (see above). |

No key to check, no Settings page — if a call fails, it's either a bad
coordinate or Open-Meteo itself being unreachable.
