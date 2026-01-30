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
def processes_agent(case: CaseData) -> List[Finding]:
    out: List[Finding] = []
    d = _doc(case, "processes.json")
    if not d:
        return out
    rows = _as_rows(d.data)
    if not rows:
        return out

    bad_paths = ("\\temp\\", "\\appdata\\local\\temp\\", "\\users\\public\\", "\\programdata\\")
    for i, r in enumerate(rows):
        path = r.get("path") or r.get("exe") or ""
        name = r.get("name") or ""
        lp = _lower(path)
        if any(bp in lp for bp in bad_paths) and name:
            out.append({
                "category": "processes",
                "title": f"Process running from suspicious path: {name}",
                "description": f"Process path looks unusual: {path}",
                "confidence": 0.65,
                "severity": "medium",
                "evidence": [_ev(d.filename, f"$[{i}].path", excerpt=str(path)[:180])],
                "recommendations": ["Check file hash/signature, parent process, and persistence mechanisms."]
            })
    return out
