from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

import requests


@dataclass
class OpenRouterClient:
    api_key: str
    model: str
    temperature: float = 0.2
    max_tokens: int = 800
    timeout_s: float = 60.0

    def chat_completion(self, messages: List[Dict[str, Any]]) -> str:
        """Выполнить запрос к OpenRouter /chat/completions.

        Возвращает текст ответа (content). Бросает исключение при ошибках сети/HTTP.
        """
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        resp = requests.post(url, headers=headers, json=payload, timeout=self.timeout_s)
        resp.raise_for_status()

        # OpenRouter возвращает JSON; если провайдер вернул HTML/пустой ответ,
        # пробуем дать понятную ошибку.
        try:
            data = resp.json()
        except Exception:
            txt = (resp.text or "").strip()
            raise ValueError(f"Non-JSON response from OpenRouter: {txt[:200]}")

        try:
            return data["choices"][0]["message"]["content"]
        except Exception:
            raise ValueError(f"Unexpected OpenRouter response shape: {json.dumps(data)[:400]}")
