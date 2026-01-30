from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

from .ingest import load_case
from .orchestrator import run_fanout, aggregate_findings, overall_severity
from .validate import validate_report, validate_rules
from .render import render_markdown
from .drift import report_similarity
from .agents import (
    system_agent,
    users_agent,
    processes_agent,
    network_agent,
    persistence_agent,
    impacket_agent,
)


def load_api_config(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def _infer_hostname(case_docs) -> str:
    for d in case_docs:
        if d.filename.lower() == "system_info.json":
            data = d.data
            if isinstance(data, list) and data and isinstance(data[0], dict):
                return str(data[0].get("hostname") or data[0].get("computer_name") or "").strip() or "UNKNOWN"
            if isinstance(data, dict):
                return str(data.get("hostname") or data.get("computer_name") or "").strip() or "UNKNOWN"
    return "UNKNOWN"

def cmd_analyze(args: argparse.Namespace) -> int:
    t0 = time.time()
    case = load_case(args.case_dir, case_id=args.case_id)
    hostname = _infer_hostname(case.docs)

    agents = {
        "system": system_agent,
        "users": users_agent,
        "processes": processes_agent,
        "network": network_agent,
        "persistence": persistence_agent,
        "impacket": impacket_agent,
    }

    # Optional LLM-agent
    if getattr(args, "use_api", False):
        if not args.api_config:
            raise SystemExit("--api-config is required when --use-api is set")

        from .agents_llm.openrouter_client import OpenRouterClient
        from .agents_llm.persistence_llm import persistence_llm_agent

        cfg = load_api_config(args.api_config)
        client = OpenRouterClient(
            api_key=cfg["api_key"],
            model=cfg["model"],
            temperature=cfg.get("temperature", 0.2),
            max_tokens=cfg.get("max_tokens", 800),
        )

        finding_schema = json.loads((Path(args.schema_dir) / "finding.schema.json").read_text(encoding="utf-8"))

        agents["persistence_llm"] = lambda case: persistence_llm_agent(case, client, finding_schema)

    res = run_fanout(case, agents)
    findings = aggregate_findings(res.findings)
    sev = overall_severity(findings)

    report = {
        "case_id": case.case_id,
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "hostname": hostname,
        "overall_severity": sev,
        "findings": findings,
        "notes_for_analyst": [
            "Working concept baseline: deterministic rules. Replace/extend agents with LLM reasoning while keeping schema + validators."
        ],
        "run_metadata": {"latency_ms": res.latency_ms, "schema_pass": False, "agents_run": res.agents_run},
    }

    schema_ok, schema_errs = validate_report(report, args.schema_dir)
    rules_ok, rule_errs = validate_rules(report)
    report["run_metadata"]["schema_pass"] = bool(schema_ok and rules_ok)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "report.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    (out_dir / "report.md").write_text(render_markdown(report), encoding="utf-8")

    if args.baseline:
        baseline = json.loads(Path(args.baseline).read_text(encoding="utf-8"))
        sim = report_similarity(baseline, report)
        (out_dir / "drift.txt").write_text(f"similarity={sim:.4f}\n", encoding="utf-8")
        if sim < args.drift_threshold:
            print(f"[DRIFT] similarity={sim:.4f} < {args.drift_threshold} => escalate to human review")
        else:
            print(f"[DRIFT] similarity={sim:.4f} OK")

    if not schema_ok:
        print("[SCHEMA] FAIL")
        for e in schema_errs[:50]:
            print(" -", e)
    if not rules_ok:
        print("[RULES] FAIL")
        for e in rule_errs[:50]:
            print(" -", e)

    dt = int((time.time() - t0) * 1000)
    print(f"Done in {dt} ms. Output: {out_dir}")
    return 0

def cmd_validate(args: argparse.Namespace) -> int:
    report = json.loads(Path(args.report).read_text(encoding="utf-8"))
    schema_ok, schema_errs = validate_report(report, args.schema_dir)
    rules_ok, rule_errs = validate_rules(report)
    ok = schema_ok and rules_ok
    print("OK" if ok else "FAIL")
    if not schema_ok:
        print("Schema errors:")
        for e in schema_errs:
            print(" -", e)
    if not rules_ok:
        print("Rule errors:")
        for e in rule_errs:
            print(" -", e)
    return 0 if ok else 2

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="soc-af", description="Disciplined agentic OSQuery endpoint forensics (working concept)")
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("analyze", help="Analyze a case folder with OSQuery JSON")
    a.add_argument("case_dir", help="Path to case folder with *.json")
    a.add_argument("--case-id", default=None)
    a.add_argument("--out", default="out/case")
    a.add_argument("--schema-dir", default="schemas")
    a.add_argument("--use-api", action="store_true", help="Enable LLM-agent via OpenRouter")
    a.add_argument("--api-config", default=None, help="Path to OpenRouter config JSON")
    a.add_argument("--baseline", default=None)
    a.add_argument("--drift-threshold", type=float, default=0.80)
    a.set_defaults(func=cmd_analyze)

    v = sub.add_parser("validate", help="Validate a report.json against schema and deterministic rules")
    v.add_argument("report")
    v.add_argument("--schema-dir", default="schemas")
    v.set_defaults(func=cmd_validate)

    return p

def main() -> None:
    args = build_parser().parse_args()
    raise SystemExit(args.func(args))
