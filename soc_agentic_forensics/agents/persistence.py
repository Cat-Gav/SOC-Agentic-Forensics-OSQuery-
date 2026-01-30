from __future__ import annotations
import re
from typing import Any, Dict, List
from ..types import CaseData, Finding, OSQueryDoc

def _doc(case: CaseData, name: str) -> OSQueryDoc | None:
    for d in case.docs:
        if d.filename.lower() == name.lower():
            return d
    return None

def _as_rows(data: Any) -> List[Dict[str, Any]]:
    if data is None:
        return []
    if isinstance(data, list):
        return [r for r in data if isinstance(r, dict)]
    if isinstance(data, dict):
        if "data" in data and isinstance(data["data"], list):
            return [r for r in data["data"] if isinstance(r, dict)]
        return [data]
    return []

def _ev(source_file: str, json_path: str, excerpt: str | None = None):
    e = {"source_file": source_file, "json_path": json_path}
    if excerpt:
        e["excerpt"] = excerpt
    return e

def _lower(s: Any) -> str:
    return str(s or "").lower()
def persistence_agent(case: CaseData) -> List[Finding]:
    out: List[Finding] = []

    d = _doc(case, "startup_items.json")
    if d:
        rows = _as_rows(d.data)
        for i, r in enumerate(rows):
            path = r.get("path") or r.get("value") or ""
            name = r.get("name") or r.get("caption") or "startup_item"
            lp = _lower(path)
            if any(x in lp for x in ["\\appdata\\", "\\temp\\", "\\users\\public\\"]):
                out.append({
                    "category": "persistence",
                    "title": f"Startup item from user-writable location: {name}",
                    "description": f"Startup entry points to user-writable location: {path}",
                    "confidence": 0.7,
                    "severity": "high",
                    "evidence": [_ev(d.filename, f"$[{i}]", excerpt=str(path)[:180])],
                    "mitre": [{"tactic":"TA0003","technique":"T1547"}],
                    "recommendations": ["Check binary reputation/signature and whether the startup entry is expected."]
                })
    return out
