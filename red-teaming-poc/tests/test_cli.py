import json

import pytest

from support_demo.agent import ToolRequest
from support_demo.cli import main


def test_chat_defaults_to_hardened(monkeypatch, capsys):
    class Planner:
        def __init__(self, *args, **kwargs):
            pass

        def check_available(self):
            pass

        def plan(self, prompt):
            return ToolRequest(action="get_order", order_id="ORDER-B900")

    monkeypatch.setattr("support_demo.models.LocalModel", Planner)
    monkeypatch.setattr("sys.argv", ["support-demo", "chat", "--prompt", "Check ORDER-B900."])
    assert main() == 0
    response = json.loads(capsys.readouterr().out)
    assert response["output"]["status"] == "denied"
    assert response["audit"][0]["policy_violation"] is False


def test_regression_cli_persists_report(monkeypatch, capsys, tmp_path):
    output = tmp_path / "regression.json"
    monkeypatch.setattr("sys.argv", ["support-demo", "regression", "--output", str(output)])
    assert main() == 0
    assert output.exists()
    assert "Offline regression" in capsys.readouterr().out


def test_scan_error_has_nonzero_exit(monkeypatch, capsys):
    def fail(**kwargs):
        raise RuntimeError("Incomplete judge assessment")

    monkeypatch.setattr("support_demo.redteam.run_scan", fail)
    monkeypatch.setattr("sys.argv", ["support-demo", "scan"])
    assert main() == 1
    assert "ERROR: Incomplete judge assessment" in capsys.readouterr().err


def test_scan_defaults_to_verified_local_model(monkeypatch, capsys, tmp_path):
    def scan(**kwargs):
        assert kwargs["model"] == kwargs["target_model"] == "qwen2.5-coder:1.5b"
        return {"runs": [], "memory_database": str(tmp_path / "pyrit.db")}

    monkeypatch.setattr("support_demo.redteam.run_scan", scan)
    monkeypatch.setattr("sys.argv", ["support-demo", "scan", "--smoke"])
    assert main() == 0
    assert "PyRIT scan saved" in capsys.readouterr().out


@pytest.mark.parametrize("count", ["0", "-1"])
def test_scan_rejects_invalid_counts(monkeypatch, count):
    monkeypatch.setattr("sys.argv", ["support-demo", "scan", "--attacks-per-type", count])
    with pytest.raises(SystemExit) as error:
        main()
    assert error.value.code == 2
