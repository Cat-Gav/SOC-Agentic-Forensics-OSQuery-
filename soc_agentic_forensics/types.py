from __future__ import annotations
from dataclasses import dataclass
from typing import Any, List, TypedDict

class Evidence(TypedDict, total=False):
    source_file: str
    json_path: str
    excerpt: str

class Mitre(TypedDict, total=False):
    tactic: str
    technique: str
    subtechnique: str

class Finding(TypedDict, total=False):
    category: str
    title: str
    description: str
    confidence: float
    severity: str
    mitre: List[Mitre]
    evidence: List[Evidence]
    recommendations: List[str]

@dataclass(frozen=True)
class OSQueryDoc:
    filename: str
    data: Any

@dataclass
class CaseData:
    case_id: str
    docs: List[OSQueryDoc]
