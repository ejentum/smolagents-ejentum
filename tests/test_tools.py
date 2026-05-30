"""Unit tests for smolagents-ejentum."""

from unittest.mock import MagicMock, patch

import pytest
from smolagents import Tool

from smolagents_ejentum import (
    EjentumAdaptiveAntiDeceptionTool,
    EjentumAdaptiveCodeTool,
    EjentumAdaptiveMemoryTool,
    EjentumAdaptiveReasoningTool,
    EjentumAntiDeceptionTool,
    EjentumCodeTool,
    EjentumMemoryTool,
    EjentumReasoningTool,
    ejentum_tools,
)
from smolagents_ejentum._api import call_logic_api


def _mock_response(
    status_code: int = 200, json_data=None, text: str = ""
) -> MagicMock:
    resp = MagicMock()
    resp.status_code = status_code
    resp.text = text or (str(json_data) if json_data else "")
    resp.json.return_value = json_data if json_data is not None else []
    return resp


# ---------------------------------------------------------------------------
# Tool identity surface
# ---------------------------------------------------------------------------


_ALL_TOOL_CLASSES = (
    EjentumReasoningTool,
    EjentumCodeTool,
    EjentumAntiDeceptionTool,
    EjentumMemoryTool,
    EjentumAdaptiveReasoningTool,
    EjentumAdaptiveCodeTool,
    EjentumAdaptiveAntiDeceptionTool,
    EjentumAdaptiveMemoryTool,
)


def test_each_tool_is_smolagents_tool_subclass():
    for cls in _ALL_TOOL_CLASSES:
        assert issubclass(cls, Tool), f"{cls.__name__} must subclass smolagents.Tool"


def test_each_tool_has_required_smolagents_class_attributes():
    for cls in _ALL_TOOL_CLASSES:
        # smolagents requires tool name to be a valid Python identifier
        # (no hyphens). The on-wire `mode` is the canonical hyphenated form.
        assert isinstance(cls.name, str) and cls.name.isidentifier()
        assert isinstance(cls.description, str) and len(cls.description) > 50
        assert isinstance(cls.inputs, dict) and "query" in cls.inputs
        assert cls.inputs["query"]["type"] == "string"
        assert cls.output_type == "string"


def test_tool_names_are_unique():
    names = {cls.name for cls in _ALL_TOOL_CLASSES}
    assert len(names) == 8


# ---------------------------------------------------------------------------
# ejentum_tools factory
# ---------------------------------------------------------------------------


def test_factory_returns_eight_tools():
    tools = ejentum_tools()
    assert len(tools) == 8
    assert all(isinstance(t, Tool) for t in tools)
    assert {t.name for t in tools} == {
        "reasoning",
        "code",
        "anti_deception",
        "memory",
        "adaptive_reasoning",
        "adaptive_code",
        "adaptive_anti_deception",
        "adaptive_memory",
    }


def test_factory_propagates_shared_config():
    tools = ejentum_tools(
        api_key="shared-key",
        api_url="https://example.com/api/",
        timeout_seconds=42.0,
    )
    for t in tools:
        assert t.api_key == "shared-key"
        assert t.api_url == "https://example.com/api/"
        assert t.timeout_seconds == 42.0


# ---------------------------------------------------------------------------
# Forward behavior
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cls,mode",
    [
        (EjentumReasoningTool, "reasoning"),
        (EjentumCodeTool, "code"),
        (EjentumAntiDeceptionTool, "anti-deception"),
        (EjentumMemoryTool, "memory"),
        (EjentumAdaptiveReasoningTool, "adaptive-reasoning"),
        (EjentumAdaptiveCodeTool, "adaptive-code"),
        (EjentumAdaptiveAntiDeceptionTool, "adaptive-anti-deception"),
        (EjentumAdaptiveMemoryTool, "adaptive-memory"),
    ],
)
@patch("smolagents_ejentum._api.requests.post")
def test_each_tool_dispatches_correct_mode(mock_post, cls, mode, monkeypatch):
    monkeypatch.setenv("EJENTUM_API_KEY", "test-key")
    mock_post.return_value = _mock_response(
        status_code=200,
        json_data=[{mode: f"[NEGATIVE GATE] sample {mode} scaffold"}],
    )

    tool = cls()
    query = (
        "I noticed drift. This might mean Y. Sharpen: Z."
        if "memory" in mode
        else "sample task"
    )
    result = tool.forward(query)

    assert f"sample {mode} scaffold" in result
    mock_post.assert_called_once()
    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer test-key"
    assert kwargs["json"]["mode"] == mode
    assert kwargs["json"]["query"] == query


@patch("smolagents_ejentum._api.requests.post")
def test_explicit_api_key_arg_overrides_env(mock_post, monkeypatch):
    monkeypatch.setenv("EJENTUM_API_KEY", "env-key")
    mock_post.return_value = _mock_response(
        status_code=200,
        json_data=[{"reasoning": "scaffold"}],
    )

    tool = EjentumReasoningTool(api_key="explicit-key")
    tool.forward("anything")

    _, kwargs = mock_post.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer explicit-key"


# ---------------------------------------------------------------------------
# call_logic_api: failure surface (the helper every Tool.forward delegates to)
# ---------------------------------------------------------------------------


def test_call_logic_api_empty_query_returns_validation_error(monkeypatch):
    monkeypatch.setenv("EJENTUM_API_KEY", "test-key")
    with patch("smolagents_ejentum._api.requests.post") as mock_post:
        result = call_logic_api(
            mode="reasoning",
            query="",
            api_key=None,
            api_url="https://example.com",
            timeout_seconds=10.0,
        )
    assert "query" in result.lower()
    assert "required" in result.lower()
    mock_post.assert_not_called()


def test_call_logic_api_whitespace_query_returns_validation_error(monkeypatch):
    """Whitespace-only input must NOT trigger a paid external request."""
    monkeypatch.setenv("EJENTUM_API_KEY", "test-key")
    with patch("smolagents_ejentum._api.requests.post") as mock_post:
        result = call_logic_api(
            mode="reasoning",
            query="   \t\n  ",
            api_key=None,
            api_url="https://example.com",
            timeout_seconds=10.0,
        )
    assert "query" in result.lower()
    assert "required" in result.lower()
    mock_post.assert_not_called()


def test_call_logic_api_non_string_query_returns_validation_error(monkeypatch):
    monkeypatch.setenv("EJENTUM_API_KEY", "test-key")
    with patch("smolagents_ejentum._api.requests.post") as mock_post:
        result = call_logic_api(
            mode="reasoning",
            query=None,
            api_key=None,
            api_url="https://example.com",
            timeout_seconds=10.0,
        )
    assert "query" in result.lower()
    mock_post.assert_not_called()


def test_call_logic_api_invalid_mode_returns_validation_error():
    result = call_logic_api(
        mode="not-a-mode",
        query="anything",
        api_key="test-key",
        api_url="https://example.com",
        timeout_seconds=10.0,
    )
    assert "mode" in result.lower()
    assert "reasoning" in result.lower()


def test_call_logic_api_missing_api_key_returns_actionable_error(monkeypatch):
    monkeypatch.delenv("EJENTUM_API_KEY", raising=False)
    result = call_logic_api(
        mode="reasoning",
        query="diagnose 503s under load",
        api_key=None,
        api_url="https://example.com",
        timeout_seconds=10.0,
    )
    assert "EJENTUM_API_KEY" in result
    assert "ejentum.com/pricing" in result


@patch("smolagents_ejentum._api.requests.post")
def test_call_logic_api_401_returns_actionable_error(mock_post):
    mock_post.return_value = _mock_response(status_code=401, text="Unauthorized")
    result = call_logic_api(
        mode="anti-deception",
        query="anything",
        api_key="bad-key",
        api_url="https://example.com",
        timeout_seconds=10.0,
    )
    assert "401" in result
    assert "EJENTUM_API_KEY" in result


@patch("smolagents_ejentum._api.requests.post")
def test_call_logic_api_non_200_returns_status_and_body(mock_post):
    mock_post.return_value = _mock_response(status_code=500, text="boom")
    result = call_logic_api(
        mode="code",
        query="anything",
        api_key="test-key",
        api_url="https://example.com",
        timeout_seconds=10.0,
    )
    assert "500" in result
    assert "boom" in result


@patch("smolagents_ejentum._api.requests.post")
def test_call_logic_api_invalid_json_response_is_handled(mock_post):
    resp = MagicMock()
    resp.status_code = 200
    resp.text = "<html>not json</html>"
    resp.json.side_effect = ValueError("not json")
    mock_post.return_value = resp
    result = call_logic_api(
        mode="reasoning",
        query="anything",
        api_key="test-key",
        api_url="https://example.com",
        timeout_seconds=10.0,
    )
    assert "not valid json" in result.lower()


@patch("smolagents_ejentum._api.requests.post")
def test_call_logic_api_unexpected_response_shape_is_handled(mock_post):
    mock_post.return_value = _mock_response(
        status_code=200, json_data={"wrong": "shape"}
    )
    result = call_logic_api(
        mode="code",
        query="anything",
        api_key="test-key",
        api_url="https://example.com",
        timeout_seconds=10.0,
    )
    assert "unexpected response shape" in result.lower()


@patch("smolagents_ejentum._api.requests.post")
def test_call_logic_api_non_string_scaffold_is_handled(mock_post):
    mock_post.return_value = _mock_response(
        status_code=200,
        json_data=[{"reasoning": ["not", "a", "string"]}],
    )
    result = call_logic_api(
        mode="reasoning",
        query="anything",
        api_key="test-key",
        api_url="https://example.com",
        timeout_seconds=10.0,
    )
    assert "unexpected response shape" in result.lower()


@patch("smolagents_ejentum._api.requests.post")
def test_call_logic_api_network_error_is_caught(mock_post):
    import requests

    mock_post.side_effect = requests.ConnectionError("simulated")
    result = call_logic_api(
        mode="memory",
        query="I noticed drift. This might mean Y. Sharpen: Z.",
        api_key="test-key",
        api_url="https://example.com",
        timeout_seconds=10.0,
    )
    assert "network error" in result.lower()
    assert "simulated" in result
