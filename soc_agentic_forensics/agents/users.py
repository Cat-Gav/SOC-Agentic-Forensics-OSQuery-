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
def users_agent(case: CaseData) -> List[Finding]:
    out: List[Finding] = []
    d = _doc(case, "users.json")
    if not d:
        return out
    rows = _as_rows(d.data)
    if not rows:
        return out

    for i, r in enumerate(rows):
        username = r.get("username") or r.get("name") or ""
        if re.search(r"(admin|support|helpdesk|svc|service)", _lower(username)):
            out.append({
                "category": "users",
                "title": f"Potential service/admin-like user: {username}",
                "description": "Account name matches a service/admin-like pattern (weak heuristic). Verify privileges and activity.",
                "confidence": 0.45,
                "severity": "low",
                "evidence": [_ev(d.filename, f"$[{i}]", excerpt=username)],
                "recommendations": ["Check group memberships, last logon, and whether the account is expected."]
            })
    return out
