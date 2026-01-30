from __future__ import annotations
from typing import Any

def render_markdown(report: dict[str, Any]) -> str:
    lines: list[str] = []
    lines.append(f"# OSQuery Forensics Report — {report.get('case_id','')}")
    lines.append("")
    lines.append(f"- **Generated at:** {report.get('generated_at','')}")
    lines.append(f"- **Hostname:** {report.get('hostname','')}")
    lines.append(f"- **Overall severity:** {report.get('overall_severity','')}")
    lines.append("")

    findings = report.get("findings", [])
    lines.append("## Findings")
    lines.append("")
    if not findings:
        lines.append("_No findings produced by the current ruleset._")
        return "\n".join(lines)

    for idx, f in enumerate(findings, 1):
        lines.append(f"### {idx}. {f.get('title','')}")
        lines.append(f"- **Category:** {f.get('category','')}")
        if f.get("severity"):
            lines.append(f"- **Severity:** {f.get('severity')}")
        lines.append(f"- **Confidence:** {f.get('confidence')}")
        if f.get("description"):
            lines.append("")
            lines.append(f.get("description"))
        lines.append("")
        lines.append("**Evidence:**")
        for ev in f.get("evidence", []):
            lines.append(f"- `{ev.get('source_file','')}` `{ev.get('json_path','')}`")
            if ev.get("excerpt"):
                lines.append(f"  - Excerpt: `{ev.get('excerpt')}`")
        if f.get("recommendations"):
            lines.append("")
            lines.append("**Recommendations:**")
            for r in f["recommendations"]:
                lines.append(f"- {r}")
        lines.append("")
    return "\n".join(lines)
