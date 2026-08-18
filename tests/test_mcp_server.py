"""Unit tests for weather_app/mcp_server.py's dispatch and formatting — no
network calls, no running workspace."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from weather_app import mcp_server  # noqa: E402


def test_weather_desc_known_code():
    assert mcp_server._weather_desc(0) == "céu limpo"


def test_weather_desc_unknown_code():
    assert mcp_server._weather_desc(123) == "código 123"


def test_weather_desc_bad_input():
    assert mcp_server._weather_desc(None) == "desconhecido"


def test_current_weather_requires_lat_lon():
    text, is_error = mcp_server._get_current_weather({})
    assert is_error is True
    assert "required" in text


def test_forecast_requires_lat_lon():
    text, is_error = mcp_server._get_weather_forecast({"lat": 1})
    assert is_error is True
    assert "required" in text


def test_forecast_days_cap(monkeypatch):
    captured = {}

    def fake_get(params):
        captured.update(params)
        return {"daily": {}, "timezone": "UTC"}, False

    monkeypatch.setattr(mcp_server, "_get", fake_get)
    mcp_server._get_weather_forecast({"lat": 1, "lon": 2, "days": 30})
    assert captured["forecast_days"] == 16


def test_tools_list_exposes_both_tools():
    result = mcp_server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "tools/list"})
    names = [t["name"] for t in result["result"]["tools"]]
    assert names == ["get_current_weather", "get_weather_forecast"]


def test_unknown_tool_call_is_an_error():
    result = mcp_server.handle_request({
        "jsonrpc": "2.0", "id": 1, "method": "tools/call",
        "params": {"name": "nope", "arguments": {}},
    })
    assert result["result"]["isError"] is True


def test_initialize_reports_server_name():
    result = mcp_server.handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize"})
    assert result["result"]["serverInfo"]["name"] == "aw-weather"
