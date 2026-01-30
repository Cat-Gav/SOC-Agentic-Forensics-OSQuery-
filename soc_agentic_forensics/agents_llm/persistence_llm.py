from __future__ import annotations

import json
from typing import Any, Dict, List

from ..types import CaseData, Finding
from .openrouter_client import OpenRouterClient


def _summarize_doc(data: Any, max_rows: int = 5) -> Any:
    """Сжато представляет OSQuery-документ для передачи в LLM.

    Важно: мы не отправляем «весь мир» в модель, а ограничиваемся
    небольшим числом строк/полей для демонстрации концепции.
    """
    if data is None:
        return None
    if isinstance(data, list):
        return data[:max_rows]
    if isinstance(data, dict):
        # некоторые форматы OSQuery могут иметь ключ "data"
        if isinstance(data.get("data"), list):
            return {**{k: v for k, v in data.items() if k != "data"}, "data": data["data"][:max_rows]}
        return data
    return str(data)[:400]


def persistence_llm_agent(case: CaseData, client: OpenRouterClient, finding_schema: Dict[str, Any]) -> List[Finding]:
    """LLM-агент для контекстной интерпретации.

    Контракт: вернуть список Finding (каждый соответствует finding.schema.json).
    В случае ошибок/невалидного JSON должно быть выброшено исключение, которое
    обработает CLI (graceful degradation).
    """

    case_payload = {
        "case_id": case.case_id,
        "docs": {d.filename: _summarize_doc(d.data) for d in case.docs},
    }

    system = (
        "Вы — ассистент SOC-аналитика. Ваша задача — по телеметрии OSQuery "
        "предложить 1-3 структурированных вывода (findings) о возможной вредоносной "
        "активности и/или закреплении. "
        "Запрещено выдумывать факты: каждый вывод должен ссылаться на evidence из входных данных. "
        "Ответ верните СТРОГО как JSON-массив объектов Finding без дополнительных пояснений."
    )

    user = (
        "Входные данные (обрезанные):\n"
        + json.dumps(case_payload, ensure_ascii=False)
        + "\n\n"
        "Схема Finding (для ориентира полей):\n"
        + json.dumps(finding_schema, ensure_ascii=False)[:2000]
    )

    content = client.chat_completion([
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ])

    parsed = json.loads(content)
    if not isinstance(parsed, list):
        raise ValueError("LLM output is not a JSON array")
    # лёгкая нормализация: гарантируем, что элементы — dict
    out: List[Finding] = []
    for i, item in enumerate(parsed[:3]):
        if isinstance(item, dict):
            out.append(item)  # type: ignore[return-value]
        else:
            raise ValueError(f"LLM output item #{i} is not an object")
    return out
