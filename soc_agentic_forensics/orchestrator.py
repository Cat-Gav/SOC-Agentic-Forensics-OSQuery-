from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Callable, Dict, List
from .types import CaseData, Finding

AgentFn = Callable[[CaseData], List[Finding]]

@dataclass
class OrchestratorResult:
    findings: List[Finding]
    agents_run: List[str]
    latency_ms: int

def run_fanout(case: CaseData, agents: Dict[str, AgentFn]) -> OrchestratorResult:
    start = time.time()
    findings: List[Finding] = []
    ran: List[str] = []
    for name, fn in agents.items():
        ran.append(name)
        try:
            findings.extend(fn(case) or [])
        except Exception as e:
            findings.append({
                "category": "pipeline",
                "title": f"Agent '{name}' failed",
                "description": str(e),
                "confidence": 1.0,
                "severity": "medium",
                "evidence": [{"source_file": "__internal__", "json_path": "$", "excerpt": str(e)}],
                "recommendations": ["Inspect logs/stacktrace; treat as pipeline reliability issue."]
            })
    latency_ms = int((time.time() - start) * 1000)
    return OrchestratorResult(findings=findings, agents_run=ran, latency_ms=latency_ms)

def aggregate_findings(findings: List[Finding]) -> List[Finding]:
    seen = set()
    out: List[Finding] = []
    for f in findings:
        ev0 = (f.get("evidence") or [{}])[0]
        key = (f.get("category"), f.get("title"), ev0.get("source_file"), ev0.get("json_path"))
        if key in seen:
            continue
        seen.add(key)
        out.append(f)
    return out

def overall_severity(findings: List[Finding]) -> str:
    order = {"low":0,"medium":1,"high":2,"critical":3}
    sev = "low"
    for f in findings:
        s = f.get("severity") or "low"
        if order.get(s, 0) > order[sev]:
            sev = s
    return sev
