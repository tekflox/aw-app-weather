"""Stdio MCP server for the decoupled aw-app-weather app.

Ported from agentic-workspace's ``src/mcp/open_meteo.py`` — this is that file
relocated into the app's own package, unchanged in behavior. Talks directly to
the free Open-Meteo API (https://open-meteo.com): no API key, no account, no
rate-limit auth, so — unlike aw-app-google-maps — there is nothing to put in
Settings and nothing to self-register over HTTP. Following the aw-app-code-server
/ aw-app-mcp-tools concept instead: the gateway that federates a session's tools
(aw-mcp-gateway) scans each installed app's own root ``mcp.json`` and spawns
whatever it declares — a plain committed, static file here, since there is no
per-install secret or host:port to bake in.

Two tools: current conditions and a short daily forecast, both by lat/lon.
Pair with aw-google-maps' geocode_address or a location app's get_location to
resolve a place name first.

Run: ``python3 -m weather_app.mcp_server`` (stdio). Registered via this repo's
root ``mcp.json`` — the gateway spawns it with cwd set to the app root.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request

_FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather interpretation codes — https://open-meteo.com/en/docs
_WEATHER_CODES = {
    0: "céu limpo",
    1: "principalmente limpo",
    2: "parcialmente nublado",
    3: "nublado",
    45: "névoa",
    48: "névoa com geada",
    51: "garoa leve",
    53: "garoa moderada",
    55: "garoa forte",
    56: "garoa congelante leve",
    57: "garoa congelante forte",
    61: "chuva leve",
    63: "chuva moderada",
    65: "chuva forte",
    66: "chuva congelante leve",
    67: "chuva congelante forte",
    71: "neve leve",
    73: "neve moderada",
    75: "neve forte",
    77: "grãos de neve",
    80: "pancadas de chuva leves",
    81: "pancadas de chuva moderadas",
    82: "pancadas de chuva violentas",
    85: "pancadas de neve leves",
    86: "pancadas de neve fortes",
    95: "trovoada",
    96: "trovoada com granizo leve",
    99: "trovoada com granizo forte",
}


def _weather_desc(code) -> str:
    try:
        return _WEATHER_CODES.get(int(code), f"código {code}")
    except (TypeError, ValueError):
        return "desconhecido"


def _get(params: dict) -> tuple[dict, bool]:
    url = f"{_FORECAST_URL}?{urllib.parse.urlencode(params)}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.loads(resp.read()), False
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read())
            return {"detail": body.get("reason") or str(e)}, True
        except Exception:
            return {"detail": str(e)}, True
    except Exception as e:
        return {"detail": str(e)}, True


def _get_current_weather(args: dict) -> tuple[str, bool]:
    lat = args.get("lat")
    lon = args.get("lon")
    if lat is None or lon is None:
        return "lat and lon are required", True

    data, is_error = _get({
        "latitude": lat,
        "longitude": lon,
        "current": "temperature_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m,relative_humidity_2m",
        "timezone": "auto",
    })
    if is_error:
        return f"Weather lookup failed: {data.get('detail', data)}", True

    cur = data.get("current") or {}
    if not cur:
        return "No current weather data returned.", False

    lines = [
        f"Condição: {_weather_desc(cur.get('weather_code'))}",
        f"Temperatura: {cur.get('temperature_2m')}°C (sensação {cur.get('apparent_temperature')}°C)",
        f"Umidade: {cur.get('relative_humidity_2m')}%",
        f"Vento: {cur.get('wind_speed_10m')} km/h",
        f"Precipitação: {cur.get('precipitation')} mm",
        f"Horário local: {cur.get('time')} ({data.get('timezone', '')})",
    ]
    return "\n".join(lines), False


def _get_weather_forecast(args: dict) -> tuple[str, bool]:
    lat = args.get("lat")
    lon = args.get("lon")
    if lat is None or lon is None:
        return "lat and lon are required", True
    days = min(int(args.get("days") or 3), 16)

    data, is_error = _get({
        "latitude": lat,
        "longitude": lon,
        "daily": "weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max",
        "timezone": "auto",
        "forecast_days": days,
    })
    if is_error:
        return f"Forecast lookup failed: {data.get('detail', data)}", True

    daily = data.get("daily") or {}
    dates = daily.get("time") or []
    if not dates:
        return "No forecast data returned.", False

    lines = [f"Previsão ({data.get('timezone', '')}):"]
    for i, date in enumerate(dates):
        code = (daily.get("weather_code") or [None] * len(dates))[i]
        tmax = (daily.get("temperature_2m_max") or [None] * len(dates))[i]
        tmin = (daily.get("temperature_2m_min") or [None] * len(dates))[i]
        pop = (daily.get("precipitation_probability_max") or [None] * len(dates))[i]
        lines.append(
            f"- {date}: {_weather_desc(code)}, {tmin}°C–{tmax}°C, "
            f"chance de chuva {pop}%"
        )
    return "\n".join(lines), False


TOOLS_SCHEMA = [
    {
        "name": "get_current_weather",
        "description": (
            "Get current weather conditions (temperature, feels-like, humidity, "
            "wind, precipitation) for a given latitude/longitude. Pair with "
            "get_location or geocode_address to resolve a place first."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude."},
                "lon": {"type": "number", "description": "Longitude."},
            },
            "required": ["lat", "lon"],
        },
    },
    {
        "name": "get_weather_forecast",
        "description": "Get a daily weather forecast (min/max temp, condition, rain chance) for a lat/lon, up to 16 days ahead.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "lat": {"type": "number", "description": "Latitude."},
                "lon": {"type": "number", "description": "Longitude."},
                "days": {"type": "integer", "description": "Number of days to forecast (default 3, max 16)."},
            },
            "required": ["lat", "lon"],
        },
    },
]

_DISPATCH = {
    "get_current_weather": _get_current_weather,
    "get_weather_forecast": _get_weather_forecast,
}


def _tool_result(req_id, text: str, is_error: bool) -> dict:
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "result": {
            "content": [{"type": "text", "text": text}],
            "isError": is_error,
        },
    }


def handle_request(request: dict) -> dict | None:
    method = request.get("method")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "aw-weather", "version": "1.0.0"},
            },
        }

    if method == "notifications/initialized":
        return None

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS_SCHEMA},
        }

    if method == "tools/call":
        params = request.get("params") or {}
        tool_name = params.get("name")
        tool_args = params.get("arguments") or {}
        handler = _DISPATCH.get(tool_name)
        if not handler:
            return _tool_result(req_id, f"Unknown tool: {tool_name}", True)
        text, is_error = handler(tool_args)
        return _tool_result(req_id, text, is_error)

    return None


def main() -> None:
    import sys
    for raw_line in sys.stdin:
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        try:
            request = json.loads(raw_line)
        except json.JSONDecodeError:
            continue
        response = handle_request(request)
        if response is not None:
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()


if __name__ == "__main__":
    main()
