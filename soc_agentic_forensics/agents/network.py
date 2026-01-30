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
def network_agent(case: CaseData) -> List[Finding]:
    out: List[Finding] = []
    d = _doc(case, "listening_ports.json")
    if not d:
        return out
    rows = _as_rows(d.data)
    if not rows:
        return out

    for i, r in enumerate(rows):
        port = str(r.get("port") or "")
        addr = r.get("address") or ""
        proto = r.get("protocol") or ""
        proc = r.get("process") or r.get("name") or ""
        try:
            pnum = int(port)
        except:
            continue
        if pnum >= 49152 and proc and proc.lower() not in {"svchost.exe","system","services.exe"}:
            out.append({
                "category": "network",
                "title": f"High ephemeral listening port: {pnum} ({proc})",
                "description": f"Process listens on high port at {addr}/{proto}. Verify ownership and need.",
                "confidence": 0.55,
                "severity": "low",
                "evidence": [_ev(d.filename, f"$[{i}]", excerpt=f"{proc} {addr}:{pnum}/{proto}")],
                "recommendations": ["Correlate with process path/signature and external connections; check if expected service."]
            })
    return out
