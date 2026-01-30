from __future__ import annotations
import json
from difflib import SequenceMatcher
from typing import Any

def report_similarity(a: dict[str, Any], b: dict[str, Any]) -> float:
    sa = json.dumps(a, ensure_ascii=False, sort_keys=True)
    sb = json.dumps(b, ensure_ascii=False, sort_keys=True)
    return SequenceMatcher(None, sa, sb).ratio()
