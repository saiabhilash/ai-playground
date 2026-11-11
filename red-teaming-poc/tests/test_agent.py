import pytest
from pydantic import ValidationError

from support_demo.agent import Session, SupportAgent, ToolRequest
from support_demo.regression import CASES, run_regression


@pytest.mark.parametrize("mode", ["baseline", "hardened"])
@pytest.mark.parametrize("name,prompt,requests,adversarial", CASES)
def test_scenarios(mode, name, prompt, requests, adversarial):
    agent = SupportAgent(mode)
    outputs = [agent.execute(request) for request in requests]
    violation = any(item["policy_violation"] for item in agent.audit)
    assert violation == (mode == "baseline" and adversarial)
    if not adversarial:
        assert all(output["status"] == "ok" for output in outputs)


@pytest.mark.parametrize("amount", [0, 25_001])
def test_invalid_refund_does_not_mutate(amount):
    agent = SupportAgent("hardened")
    result = agent.execute(ToolRequest(action="refund", order_id="ORDER-A100", amount_cents=amount))
    assert result["status"] == "denied"
    assert agent.refunded == {}


def test_exact_budget_then_one_cent_over():
    agent = SupportAgent("hardened")
    assert agent.execute(ToolRequest(action="refund", order_id="ORDER-A100", amount_cents=10_000))["status"] == "ok"
    assert agent.execute(ToolRequest(action="refund", order_id="ORDER-A200", amount_cents=1))["status"] == "denied"
    assert sum(agent.refunded.values()) == 10_000


def test_denied_cross_tenant_refund_does_not_consume_budget():
    agent = SupportAgent("hardened")
    agent.execute(ToolRequest(action="refund", order_id="ORDER-B900", amount_cents=5_000))
    assert agent.refunded == {}
    assert agent.execute(ToolRequest(action="refund", order_id="ORDER-A100", amount_cents=10_000))["status"] == "ok"


def test_authenticated_identity_is_not_tool_input():
    with pytest.raises(ValidationError):
        ToolRequest(action="get_order", order_id="ORDER-B900", tenant_id="tenant_b")
    agent = SupportAgent("hardened", session=Session(tenant_id="tenant_b"))
    assert agent.execute(ToolRequest(action="get_order", order_id="ORDER-B900"))["status"] == "ok"
    assert agent.execute(ToolRequest(action="get_order", order_id="ORDER-A100"))["status"] == "denied"


@pytest.mark.parametrize("amount", [-1, True, 1.5, "100"])
def test_reject_invalid_amount_types(amount):
    with pytest.raises(ValidationError):
        ToolRequest(action="refund", order_id="ORDER-A100", amount_cents=amount)


def test_unknown_and_foreign_orders_have_same_response():
    agent = SupportAgent("hardened")
    missing = agent.execute(ToolRequest(action="get_order", order_id="NOT-AN-ORDER"))
    foreign = agent.execute(ToolRequest(action="get_order", order_id="ORDER-B900"))
    assert missing == foreign
    assert len(agent.audit) == 2


def test_baseline_still_rejects_over_refunding_order():
    agent = SupportAgent("baseline")
    agent.execute(ToolRequest(action="refund", order_id="ORDER-A100", amount_cents=20_000))
    assert agent.execute(ToolRequest(action="refund", order_id="ORDER-A100", amount_cents=6_000))["status"] == "denied"
    assert agent.refunded["ORDER-A100"] == 20_000


def test_regression_report(tmp_path):
    output = tmp_path / "report.json"
    report = run_regression(output)
    assert output.exists()
    assert report["summary"]["baseline"]["policy_violations"] == 5
    assert report["summary"]["hardened"]["policy_violations"] == 0
    for mode in ("baseline", "hardened"):
        assert report["summary"][mode]["benign_cases_allowed"] == 2
    assert "not_llm" in report["kind"]


def test_no_planner_is_explicit_error():
    with pytest.raises(RuntimeError, match="live planner"):
        SupportAgent("hardened").respond("Hello")
