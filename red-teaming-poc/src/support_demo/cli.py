import argparse
import json
import logging
import sys
from pathlib import Path

from support_demo.regression import run_regression


def positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("Must be a positive integer.")
    return parsed


def main() -> int:
    if sys.platform == "win32":
        for stream in (sys.stdout, sys.stderr):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser(description="Synthetic support-agent red-teaming demo.")
    commands = parser.add_subparsers(dest="command", required=True)
    regression = commands.add_parser("regression", help="Offline tool-boundary checks, not an LLM scan.")
    regression.add_argument("--output", type=Path, default=Path("reports") / "regression.json")
    chat = commands.add_parser("chat", help="Call the local LLM-powered agent once.")
    chat.add_argument("--prompt", required=True)
    chat.add_argument("--mode", choices=["baseline", "hardened"], default="hardened")
    chat.add_argument("--model", default="qwen2.5-coder:7b")
    chat.add_argument("--timeout", type=positive_int, default=180)
    scan = commands.add_parser("scan", help="Run PyRIT generation, attacks and judging.")
    scan.add_argument("--mode", choices=["baseline", "hardened", "both"], default="both")
    scan.add_argument(
        "--model", default="qwen2.5-coder:1.5b",
        help="Local generator and judge; defaults to the verified integration model.",
    )
    scan.add_argument("--target-model", help="Local target planner; defaults to --model.")
    scan.add_argument("--timeout", type=positive_int, default=180)
    scan.add_argument("--attacks-per-type", type=positive_int, default=1)
    scan.add_argument("--attack", choices=["prompt-injection", "roleplay"], default="prompt-injection")
    scan.add_argument(
        "--smoke", action="store_true",
        help="Only the cross-customer-access objective for a quick integration check.",
    )
    scan.add_argument("--output", type=Path, default=Path("reports") / "pyrit.json")
    catalog = commands.add_parser("scenarios", help="List exact local scenario prompts without inference.")
    catalog.add_argument("--suite", default="all")
    catalog.add_argument("--output", type=Path, help="Export the catalog as JSON.")
    catalog.add_argument("--export-seeds", type=Path, help="Export a native PyRIT SeedDataset as JSON.")
    capabilities = commands.add_parser("capabilities", help="Inventory the installed PyRIT exports without inference.")
    capabilities.add_argument("--output", type=Path, default=Path("reports") / "pyrit-capabilities.json")
    lab = commands.add_parser("lab", help="Run seeded, stateful or adaptive PyRIT scenarios.")
    selection = lab.add_mutually_exclusive_group(required=True)
    selection.add_argument("--scenario", action="append", help="Scenario ID; repeat for multiple cases.")
    selection.add_argument("--suite", help="demo, quick, authorization, budget, injection, language, multiturn, controls, all")
    lab.add_argument("--mode", choices=["baseline", "hardened", "both"], default="both")
    lab.add_argument("--model", default="qwen2.5-coder:1.5b", help="Local target planner.")
    lab.add_argument("--strategy", choices=["seeded", "adaptive"], default="seeded")
    lab.add_argument("--converter", choices=["none", "base64", "rot13", "json"], default="none")
    lab.add_argument("--attacker-model", help="Adaptive attacker; defaults to --model.")
    lab.add_argument("--judge-model", help="Optional local LLM auxiliary judge; primary scoring is deterministic.")
    lab.add_argument("--max-turns", type=positive_int, default=3, help="Adaptive budget, 1-10 turns.")
    lab.add_argument("--timeout", type=positive_int, default=180)
    lab.add_argument("--output", type=Path, default=Path("reports") / "pyrit-lab.json")
    args = parser.parse_args()

    try:
        if args.command == "regression":
            report = run_regression(args.output)
            print(json.dumps(report["summary"], indent=2))
            print(f"Offline regression saved to {args.output.resolve()}")
        elif args.command == "capabilities":
            from support_demo.scenarios import capability_inventory
            from support_demo.regression import write_json

            inventory = capability_inventory()
            write_json(args.output, inventory)
            print(f"PyRIT {inventory['pyrit_version']}: {inventory['scope']}")
            for family, names in inventory["components"].items():
                print(f"{family}: {len(names)} exported symbols; inspect the saved JSON for names.")
            print(f"Capability inventory saved to {args.output.resolve()}")
        elif args.command == "scenarios":
            from support_demo.scenarios import export_seeds, select_scenarios
            from support_demo.regression import write_json

            scenarios = select_scenarios(suite=args.suite)
            for scenario in scenarios:
                print(f"\n{scenario.id} [{scenario.category}] - {scenario.objective}")
                for turn, prompt in enumerate(scenario.prompts, start=1):
                    print(f"  {turn}. {prompt}")
                if scenario.expected_results:
                    print(f"  Expected control results: {json.dumps(scenario.expected_results)}")
            print(f"\n{len(scenarios)} scenarios; no model calls.")
            if args.output:
                write_json(args.output, {"scenarios": [s.as_dict() for s in scenarios]})
                print(f"Catalog saved to {args.output.resolve()}")
            if args.export_seeds:
                export_seeds(args.export_seeds, scenarios)
                print(f"PyRIT seeds saved to {args.export_seeds.resolve()}")
        elif args.command == "lab":
            from support_demo.lab import run_lab
            from support_demo.scenarios import select_scenarios

            logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
            report = run_lab(
                output=args.output,
                scenarios=select_scenarios(args.scenario, args.suite),
                model=args.model, mode=args.mode, strategy=args.strategy,
                converter=args.converter, attacker_model=args.attacker_model,
                judge_model=args.judge_model, max_turns=args.max_turns, timeout=args.timeout,
            )
            for run in report["runs"]:
                control = f", control completed={run['control_completed']}" if run["control_completed"] is not None else ""
                print(
                    f"{run['scenario_id']} / {run['mode']}: "
                    f"{run['objective_policy_violations']} violations, "
                    f"{run['callback_count']} turns{control}"
                )
            print(f"PyRIT lab saved to {args.output.resolve()}")
            print(f"PyRIT conversation database: {report['memory_database']}")
        elif args.command == "chat":
            from support_demo.agent import SupportAgent
            from support_demo.models import LocalModel

            model = LocalModel(args.model, timeout=args.timeout)
            model.check_available()
            agent = SupportAgent(args.mode, planner=model)
            print(json.dumps({"output": agent.respond(args.prompt), "audit": agent.audit}, indent=2))
        else:
            from support_demo.redteam import run_scan

            logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
            report = run_scan(
                output=args.output,
                model=args.model,
                target_model=args.target_model or args.model,
                mode=args.mode,
                attacks_per_type=args.attacks_per_type,
                attack=args.attack,
                smoke=args.smoke,
                timeout=args.timeout,
            )
            for run in report["runs"]:
                print(
                    f"{run['mode']}: {run['objective_policy_violations']} objective "
                    f"policy violations / {run['callback_count']} callbacks"
                )
            print(f"PyRIT scan saved to {args.output.resolve()}")
            print(f"PyRIT conversation database: {report['memory_database']}")
            print(f"CoPyRIT: pyrit_backend --host 127.0.0.1 --config-file pyrit.yaml")
    except (ValueError, RuntimeError, OSError) as error:
        print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
