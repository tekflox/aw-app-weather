"""Entrypoint referenced by aw-app.json's ``runtime.entrypoint``
("weather_app.plugin:WeatherAppPlugin").

There is nothing for this Tier-1 plugin to register through the framework's
``ctx`` facades: no routes, no CLIs, no config, no secret. All of this app's
value is its root ``mcp.json`` — a static file aw-mcp-gateway's app-scan reads
directly (see ``weather_app/mcp_server.py``'s module docstring) — and the
``aw-weather`` skill. Compare aw-app-mobile's ``mobile_app/plugin.py``, the
other app in this workspace that is deliberately almost empty for the same
reason.
"""
from __future__ import annotations

import logging

log = logging.getLogger("aw_apps.weather")


class WeatherAppPlugin:
    async def activate(self, ctx) -> None:
        self.ctx = ctx
        log.info("aw-app-weather activated: mcp server=weather (stdio, no config needed)")

    async def deactivate(self) -> None:
        log.info("aw-app-weather deactivated")
