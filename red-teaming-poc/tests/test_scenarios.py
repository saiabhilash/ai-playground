import json

import pytest
from pyrit.models import AttackSeedGroup, SeedDataset

from support_demo.cli import main
from support_demo.scenarios import BY_ID, SCENARIOS, capability_inventory, export_seeds, select_scenarios


def test_catalog_has_distinct_substantial_scenarios():
    assert len(SCENARIOS) >= 30
    assert len(BY_ID) == len(SCENARIOS)
    assert all(s.objective and all(s.prompts) for s in SCENARIOS)
    assert all(not s.expected_results or len(s.expected_results) == len(s.prompts) for s in SCENARIOS)
    assert len(select_scenarios(suite="multiturn")) >= 5
    assert len(select_scenarios(suite="controls")) >= 5


def test_demo_suite_focuses_on_three_vulnerabilities_and_controls():
    scenarios = select_scenarios(suite="demo")
    assert [s.id for s in scenarios] == [
        "own-order", "own-refund", "oversized-refund", "five-part-refund",
        "cross-customer-read", "forged-refund-approval",
    ]
    assert len(BY_ID["five-part-refund"].prompts) == 5
    assert BY_ID["forged-refund-approval"].category == "injection"


@pytest.mark.parametrize("ids,suite", [
    (None, None), (["own-order"], "all"), (["unknown"], None),
    (["own-order", "own-order"], None), (None, "unknown"),
])
def test_invalid_selection_is_explicit(ids, suite):
    with pytest.raises(ValueError):
        select_scenarios(ids, suite)


def test_native_seed_export_round_trips_and_retains_order(tmp_path):
    output = tmp_path / "seeds.json"
    scenarios = select_scenarios(suite="all")
    export_seeds(output, scenarios)
    dataset = SeedDataset.model_validate_json(output.read_text())
    grouped = {}
    for seed in dataset.seeds:
        grouped.setdefault(seed.prompt_group_id, []).append(seed)
    assert len(grouped) == len(scenarios)
    for seeds in grouped.values():
        group = AttackSeedGroup(seeds=seeds)
        scenario = BY_ID[seeds[0].metadata["scenario_id"]]
        assert group.objective.value == scenario.objective
        assert [message.get_value() for message in group.user_messages] == list(scenario.prompts)


def test_catalog_cli_does_not_require_model_server(monkeypatch, capsys, tmp_path):
    output = tmp_path / "catalog.json"
    monkeypatch.setattr(
        "sys.argv", ["support-demo", "scenarios", "--suite", "quick", "--output", str(output)],
    )
    assert main() == 0
    assert len(json.loads(output.read_text())["scenarios"]) == 3
    assert "no model calls" in capsys.readouterr().out


def test_unknown_scenario_cli_fails(monkeypatch, capsys):
    monkeypatch.setattr("sys.argv", ["support-demo", "lab", "--scenario", "unknown"])
    assert main() == 1
    assert "Unknown scenarios" in capsys.readouterr().err


def test_capability_inventory_matches_installed_exports(monkeypatch, tmp_path, capsys):
    inventory = capability_inventory()
    assert "PromptSendingAttack" in inventory["components"]["attacks"]
    assert "CrescendoAttack" in inventory["components"]["attacks"]
    assert "Base64Converter" in inventory["components"]["converters"]
    assert "SelfAskLikertScorer" in inventory["components"]["scorers"]
    assert "OpenAIChatTarget" in inventory["components"]["targets"]
    output = tmp_path / "capabilities.json"
    monkeypatch.setattr("sys.argv", ["support-demo", "capabilities", "--output", str(output)])
    assert main() == 0
    assert json.loads(output.read_text())["components"] == inventory["components"]
