import asyncio

import pytest
import requests
from pydantic import ValidationError

from support_demo.agent import ToolRequest
from support_demo.models import LocalModel


class Response:
    def __init__(self, data):
        self.data = data

    def raise_for_status(self):
        pass

    def json(self):
        return self.data


def test_model_initialization():
    model = LocalModel("qwen2.5-coder:1.5b")
    assert model.model_name == "qwen2.5-coder:1.5b"
    assert model.get_model_name() == "ollama/qwen2.5-coder:1.5b"


def test_schema_and_loopback_only(monkeypatch):
    def post(url, json, timeout):
        assert url == "http://127.0.0.1:11434/api/generate"
        assert json["format"] == ToolRequest.model_json_schema()
        assert json["stream"] is False
        assert timeout == 180
        return Response({"response": '{"action":"get_order","order_id":"ORDER-A100","amount_cents":0}'})

    monkeypatch.setattr("support_demo.models.requests.post", post)
    result = LocalModel("local").plan("Check my order.")
    assert result.action == "get_order"
    assert result.order_id == "ORDER-A100"


def test_invalid_model_output_is_not_success(monkeypatch):
    monkeypatch.setattr(
        "support_demo.models.requests.post",
        lambda *args, **kwargs: Response({"response": '{"action":"refund","amount_cents":"100"}'}),
    )
    with pytest.raises(ValidationError):
        LocalModel("local").generate("prompt", schema=ToolRequest)


def test_http_failure_is_not_swallowed(monkeypatch):
    def post(*args, **kwargs):
        raise requests.ConnectionError("Local server unavailable")

    monkeypatch.setattr("support_demo.models.requests.post", post)
    with pytest.raises(requests.ConnectionError):
        LocalModel("local").generate("prompt")


def test_async_generation(monkeypatch):
    monkeypatch.setattr(
        "support_demo.models.requests.post",
        lambda *args, **kwargs: Response({"response": "hello"}),
    )
    assert asyncio.run(LocalModel("local").a_generate("prompt")) == "hello"


def test_model_presence_check(monkeypatch):
    monkeypatch.setattr(
        "support_demo.models.requests.get",
        lambda *args, **kwargs: Response({"models": [{"name": "local:latest"}]}),
    )
    LocalModel("local").check_available()
    with pytest.raises(ValueError, match="not installed"):
        LocalModel("absent").check_available()


def test_chat_preserves_roles_and_schema_on_loopback(monkeypatch):
    messages = [{"role": "system", "content": "Judge"}, {"role": "user", "content": "Evidence"}]
    schema = {"type": "object"}

    def post(url, json, timeout):
        assert url == "http://127.0.0.1:11434/api/chat"
        assert json["messages"] == messages
        assert json["format"] == schema
        assert json["stream"] is False
        assert timeout == 180
        return Response({"message": {"content": '{"score_value":false}'}})

    monkeypatch.setattr("support_demo.models.requests.post", post)
    assert asyncio.run(LocalModel("local").a_chat(messages, json_schema=schema)) == '{"score_value":false}'


@pytest.mark.parametrize("content", ["", "   ", None])
def test_empty_chat_response_is_explicit_error(monkeypatch, content):
    monkeypatch.setattr(
        "support_demo.models.requests.post",
        lambda *args, **kwargs: Response({"message": {"content": content}}),
    )
    with pytest.raises(ValueError, match="chat response"):
        LocalModel("local").chat([{"role": "user", "content": "prompt"}])


@pytest.mark.parametrize("data", [None, [], {}, {"message": "invalid"}, {"message": {}}])
def test_invalid_chat_envelope_is_explicit_error(monkeypatch, data):
    monkeypatch.setattr(
        "support_demo.models.requests.post",
        lambda *args, **kwargs: Response(data),
    )
    with pytest.raises(ValueError, match="chat response"):
        LocalModel("local").chat([{"role": "user", "content": "prompt"}])
