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


def impacket_agent(case: CaseData) -> List[Finding]:
    """Правила обнаружения Impacket-подобной активности по характерным строкам.

    Цель: показать воспроизводимую детекцию на основе телеметрии OSQuery.
    """

    out: List[Finding] = []

    proc_doc = _doc(case, "processes.json")
    ports_doc = _doc(case, "listening_ports.json")

    proc_rows = _as_rows(proc_doc.data) if proc_doc else []
    ports_rows = _as_rows(ports_doc.data) if ports_doc else []

    has_445 = any(str(r.get("port")) == "445" for r in ports_rows)

    for i, r in enumerate(proc_rows):
        cmd = r.get("cmdline") or r.get("command_line") or ""
        parent = r.get("parent") or r.get("parent_name") or r.get("parent_process") or ""
        lcmd = _lower(cmd)
        lparent = _lower(parent)

        # SMBExec-like: cmd.exe /Q /c echo ... ^> \\HOST\ADMIN$\... 2^>^&1
        smbexec = (
            "cmd.exe" in lcmd
            and "\\\\" in lcmd
            and "admin$" in lcmd
            and "echo" in lcmd
            and "2^>^&1" in lcmd
        )

        # WMIExec-like: wmiprvse.exe -> cmd.exe /Q /c ... 1> \\... 2>&1
        wmiexec = (
            "cmd.exe" in lcmd
            and "/q" in lcmd
            and "/c" in lcmd
            and "1> \\\\" in lcmd
            and "2>&1" in lcmd
        ) or ("wmiprvse.exe" in lparent and "cmd.exe" in lcmd)

        if smbexec or wmiexec:
            title = "Impacket-like Activity (SMBExec/WMIExec)" if (smbexec and wmiexec) else (
                "Impacket-like Activity (SMBExec)" if smbexec else "Impacket-like Activity (WMIExec)"
            )

            ev = [_ev("processes.json", f"$[{i}].cmdline", excerpt=str(cmd)[:220])]
            if ports_doc and has_445:
                # показываем наличие SMB-порта как дополнительный контекст
                # (в OSQuery listen-порты могут отображать локальные сервисы)
                # берём первую строку с 445
                for j, pr in enumerate(ports_rows):
                    if str(pr.get("port")) == "445":
                        ev.append(_ev("listening_ports.json", f"$[{j}].port", excerpt="445"))
                        break

            out.append({
                "category": "network",
                "title": title,
                "description": "Обнаружены характерные шаблоны командной строки, совпадающие с техникой удалённого выполнения команд через SMB/WMI (типично для Impacket).",
                "severity": "medium",
                "confidence": 0.8,
                "evidence": ev,
                "mitre": [{"tactic": "TA0008", "technique": "T1021"}],
                "recommendations": [
                    "Сопоставьте процесс с родительским процессом и учётной записью, от имени которой выполнялось действие.",
                    "Проверьте сетевые соединения на 445/135 и события аутентификации (LogonType=3) для корреляции.",
                ],
            })

    return out
