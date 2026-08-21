---
repo: architecture
path: docs/architecture/aw-app-weather.md
source: generated
edited: false
checksum: sha256:b3ff883ab0c7839ba9bdec6048d6c797602aa917815998c4ce9455c5448c28bf
---
# Weather

- **repo**: aw-app-weather
- **layer**: app
- **technologies**: python
- **health** (derived): planned

Current conditions and a daily forecast for any place on Earth, by latitude/longitude — through Open-Meteo, a free API with no key and no account. Ports agentic-workspace's aw-open-meteo MCP into aw-workspace. Pair with aw-google-maps' geocode_address, or a mobile companion app's get_location, to resolve a place name into coordinates first.

## Connections
- `stdio-mcp` → **mcp-gateway** — MCP surface aggregated by the gateway

## MCP tools
- `get_current_weather`
- `get_weather_forecast`

## Requirements
_none documented_
