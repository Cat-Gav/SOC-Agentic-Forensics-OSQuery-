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
def system_agent(case: CaseData) -> List[Finding]:
    out: List[Finding] = []
    d = _doc(case, "system_info.json")
    if not d:
        return out
    rows = _as_rows(d.data)
    if not rows:
        return out

    r0 = rows[0]
    hostname = r0.get("hostname") or r0.get("computer_name") or ""
    if not hostname:
        out.append({
            "category": "system",
            "title": "Hostname missing in system_info",
            "description": "system_info.json does not contain hostname/computer_name field.",
            "confidence": 1.0,
            "severity": "medium",
            "evidence": [_ev(d.filename, "$[0]", excerpt=str(r0)[:180])],
            "recommendations": ["Verify OSQuery pack includes system_info; ensure agent collected full snapshot."]
        })
    return out
