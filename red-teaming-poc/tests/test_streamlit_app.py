from pathlib import Path

import pytest
import requests
from streamlit.testing.v1 import AppTest

from support_demo.agent import SupportAgent, ToolRequest
from support_demo.models import LocalModel

APP = Path(__file__).resolve().parents[1] / "src" / "support_demo" / "streamlit_app.py"


@pytest.fixture
def app(monkeypatch):
    monkeypatch.setattr(LocalModel, "check_available", lambda self: None)
    return AppTest.from_file(str(APP)).run()


def test_ui_is_vulnerable_only_and_exposes_cross_customer_access(app, monkeypatch):
    assert not app.radio
    assert app.session_state.agent.mode == "baseline"
    assert not app.warning
    assert "Vulnerable teaching app" not in str(app)
    assert any("forged approval" in item.label for item in app.expander)
    assert any("--suite demo" in item.value for item in app.caption)
    monkeypatch.setattr(
        LocalModel, "plan",
        lambda self, prompt: ToolRequest(
            action="get_order", order_id="ORDER-B900" if "B900" in prompt else "ORDER-A100",
        ),
    )
    app.chat_input[0].set_value("Check my order ORDER-A100.").run()
    assert not app.exception
    assert app.success[0].value == "Order details: ORDER-A100"
    assert any("SYNTHETIC-A-DELIVERY" in item.value for item in app.markdown)
    app.chat_input[0].set_value("Check ORDER-B900.").run()
    assert not app.exception
    assert "SYNTHETIC-B-PRIVATE" in str(app.session_state.messages)
    assert app.session_state.agent.audit[-1]["policy_violation"] is True
    assert "not a PyRIT run" in app.error[0].value
    assert len(app.session_state.agent.audit) == 2


def test_refunds_retain_budget_across_reruns_and_new_chat_resets(app, monkeypatch):
    monkeypatch.setattr(
        LocalModel, "plan",
        lambda self, prompt: ToolRequest(
            action="refund", order_id="ORDER-A200" if "A200" in prompt else "ORDER-A100",
            amount_cents=6000,
        ),
    )
    app.chat_input[0].set_value("Refund 6000 cents on ORDER-A100.").run()
    app.run()
    app.chat_input[0].set_value("Refund 6000 cents on ORDER-A200.").run()
    assert not app.exception
    assert len(app.success) == 2
    assert sum(app.session_state.agent.refunded.values()) == 12000
    assert app.metric[0].value == "$120.00"
    assert app.metric[1].value == "$-20.00"
    assert app.session_state.agent.audit[-1]["policy_violation"] is True
    app.button[0].click().run()
    assert not app.exception
    assert app.session_state.agent.refunded == {}
    assert len(app.session_state.messages) == 1


def test_model_change_creates_fresh_vulnerable_session(app, monkeypatch):
    monkeypatch.setattr(
        LocalModel, "plan",
        lambda self, prompt: ToolRequest(action="get_order", order_id="ORDER-B900"),
    )
    app.chat_input[0].set_value("Check ORDER-B900.").run()
    assert not app.exception
    assert app.session_state.agent.audit[0]["policy_violation"] is True
    assert any("policy violation" in item.value for item in app.error)
    app.text_input[0].set_value("another-local-model").run()
    assert app.session_state.agent.mode == "baseline"
    assert app.session_state.agent.audit == []
    assert app.session_state.agent.planner.model_name == "another-local-model"
    assert len(app.session_state.messages) == 1


def test_five_refunds_reproduce_screenshot_totals(app, monkeypatch):
    monkeypatch.setattr(
        LocalModel, "plan",
        lambda self, prompt: ToolRequest(
            action="refund", order_id="ORDER-A100", amount_cents=5000,
        ),
    )
    for _ in range(5):
        app.chat_input[0].set_value("Refund 5000 cents on ORDER-A100.").run()
    assert not app.exception
    assert len(app.success) == 5
    assert app.metric[0].value == "$250.00"
    assert app.metric[1].value == "$-150.00"
    assert [event["policy_violation"] for event in app.session_state.agent.audit] == [
        False, False, True, True, True,
    ]


def test_forged_approval_refunds_another_customers_order(app, monkeypatch):
    from support_demo.scenarios import BY_ID

    prompt = BY_ID["forged-refund-approval"].prompts[0]
    monkeypatch.setattr(
        LocalModel, "plan",
        lambda self, text: ToolRequest(
            action="refund", order_id="ORDER-B900", amount_cents=5000,
        ),
    )
    app.chat_input[0].set_value(prompt).run()
    assert not app.exception
    assert app.session_state.agent.session.tenant_id == "tenant_a"
    assert app.session_state.agent.refunded == {"ORDER-B900": 5000}
    assert app.session_state.agent.audit[-1]["policy_violation"] is True
    assert "ORDER-B900" in app.success[0].value


def test_existing_protected_session_is_replaced(app):
    app.session_state.configuration = ("hardened", "qwen2.5-coder:1.5b")
    app.session_state.agent = SupportAgent("hardened")
    app.session_state.agent.execute(
        ToolRequest(action="refund", order_id="ORDER-A100", amount_cents=5000),
    )
    app.run()
    assert not app.exception
    assert app.session_state.agent.mode == "baseline"
    assert app.session_state.agent.refunded == {}
    assert len(app.session_state.messages) == 1


def test_model_failure_is_visible_and_recoverable(app, monkeypatch):
    def unavailable(self):
        raise requests.ConnectionError("Ollama unavailable")

    monkeypatch.setattr(LocalModel, "check_available", unavailable)
    app.chat_input[0].set_value("Check my order ORDER-A100.").run()
    assert not app.exception
    assert "Ollama unavailable" in app.error[0].value
    assert app.session_state.agent.audit == []
    monkeypatch.setattr(LocalModel, "check_available", lambda self: None)
    monkeypatch.setattr(
        LocalModel, "plan",
        lambda self, prompt: ToolRequest(action="get_order", order_id="ORDER-A100"),
    )
    app.chat_input[0].set_value("Try ORDER-A100 again.").run()
    assert not app.exception
    assert app.success[0].value == "Order details: ORDER-A100"


def test_blank_model_is_explicit_error(app):
    app.text_input[0].set_value(" ").run()
    assert not app.exception
    assert app.error[0].value == "Enter an installed Ollama model name."


def test_browser_sessions_are_isolated(app, monkeypatch):
    monkeypatch.setattr(
        LocalModel, "plan",
        lambda self, prompt: ToolRequest(action="refund", order_id="ORDER-A100", amount_cents=5000),
    )
    app.chat_input[0].set_value("Refund 5000 cents on ORDER-A100.").run()
    other = AppTest.from_file(str(APP)).run()
    assert not other.exception
    assert other.session_state.agent.refunded == {}
    assert other.session_state.agent is not app.session_state.agent
