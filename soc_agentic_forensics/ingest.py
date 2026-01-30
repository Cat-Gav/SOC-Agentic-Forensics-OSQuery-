from __future__ import annotations

import json
from pathlib import Path
from typing import Any, List
from .types import CaseData, OSQueryDoc

def _load_json(path: Path) -> Any:
    raw = path.read_text(encoding="utf-8", errors="ignore").strip()
    if not raw:
        return None
    return json.loads(raw)

def load_case(folder: str | Path, case_id: str | None = None) -> CaseData:
    folder = Path(folder)
    if not folder.exists() or not folder.is_dir():
        raise FileNotFoundError(f"Case folder not found: {folder}")

    cid = case_id or folder.name
    docs: List[OSQueryDoc] = []
    for p in sorted(folder.glob("*.json")):
        try:
            data = _load_json(p)
        except Exception as e:
            data = {"__parse_error__": str(e), "__raw_path__": str(p)}
        docs.append(OSQueryDoc(filename=p.name, data=data))

    if not docs:
        raise ValueError(f"No .json files found in {folder}")
    return CaseData(case_id=cid, docs=docs)
