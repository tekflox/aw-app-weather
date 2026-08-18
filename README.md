# aw-app-weather

Current weather conditions and a daily forecast for every agent in this
workspace — no API key, no account.

Ports agentic-workspace's `aw-open-meteo` MCP server (`src/mcp/open_meteo.py`).
2 tools, gateway-prefixed `aw__weather__*`, backed by the free
[Open-Meteo](https://open-meteo.com) API.

| Monolith | This app |
|---|---|
| `agentic-workspace/src/mcp/open_meteo.py` (stdio MCP, hand-rolled JSON-RPC) | `weather_app/mcp_server.py` — same file, relocated into the app's own package, unchanged behavior |
| `src/config/mcp.json`'s `aw-open-meteo` entry | this repo's root `mcp.json` — a static, committed file (no secret, no per-install host/port to bake in) |
| *(no dedicated skill in the monolith)* | `skills/aw-weather/SKILL.md` — new, teaches an agent which tool answers which question and how to resolve a place name into coordinates first |

## Why no self-registration, no HTTP, no Settings page

Unlike `aw-app-google-maps` (needs an API key → secret store → self-registered
HTTP MCP endpoint with per-boot host/port baked in), Open-Meteo needs nothing
per-install. So this app follows the plainer `aw-app-code-server` /
`aw-app-mcp-tools` pattern instead: a static `mcp.json` committed to the repo,
spawned by `aw-mcp-gateway` as a stdio subprocess with `cwd` set to the
installed app directory. The Tier-1 plugin (`weather_app/plugin.py`) has
nothing to register through `ctx` — no routes, no CLIs, no config — so it's
close to a no-op, same as `aw-app-mobile`'s.

## Install

```bash
aw-workspace-cli marketplace install weather
```

That's it — both tools work immediately, no Settings step.

## Tools

| Tool | Answers |
|---|---|
| `get_current_weather(lat, lon)` | "what's it like outside right now" |
| `get_weather_forecast(lat, lon, days=3, max 16)` | "will it rain this week" |

Both need coordinates, not a place name — pair with `aw-google-maps`'s
`geocode_address` or a mobile companion app's `get_location` to resolve one
first. See `skills/aw-weather/SKILL.md` for the full contract.

## Tests

```bash
python3 tests/validate_manifest.py aw-app.json
python3 -m pytest tests -q
```
