from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Tuple
from jsonschema import Draft202012Validator, RefResolver

def _load_schema(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def validate_report(report: dict[str, Any], schema_dir: str | Path) -> Tuple[bool, list[str]]:
    schema_dir = Path(schema_dir)
    report_schema = _load_schema(schema_dir / "report.schema.json")
    finding_schema = _load_schema(schema_dir / "finding.schema.json")

    store = {
        str((schema_dir / "report.schema.json").resolve()): report_schema,
        str((schema_dir / "finding.schema.json").resolve()): finding_schema,
        "finding.schema.json": finding_schema,
    }
    resolver = RefResolver.from_schema(report_schema, store=store)
    v = Draft202012Validator(report_schema, resolver=resolver)

    errors = sorted(v.iter_errors(report), key=lambda e: e.path)
    if not errors:
        return True, []
    return False, [f"{list(e.path)}: {e.message}" for e in errors]

def validate_rules(report: dict[str, Any]) -> Tuple[bool, list[str]]:
    errs: list[str] = []
    if not report.get("hostname"):
        errs.append("hostname is empty")
    if report.get("overall_severity") not in {"low","medium","high","critical"}:
        errs.append("overall_severity invalid")
    for i, f in enumerate(report.get("findings", [])):
        if not (f.get("evidence") or []):
            errs.append(f"finding[{i}] has no evidence")
    return (len(errs) == 0), errs
