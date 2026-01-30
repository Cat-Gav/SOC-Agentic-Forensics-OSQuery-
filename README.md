# SOC Agentic Forensics (OSQuery) — рабочий прототип

Ключевая идея: заменить «свободный» LLM-чат на дисциплинированный конвейер:

- несколько узкоспециализированных агентов анализируют один и тот же кейс (fan-out / fan-in);
- каждый агент возвращает **структурированные Findings**;
- итоговый отчёт валидируется по **JSON Schema**;
- по умолчанию используются **детерминированные правила** (работает оффлайн);
- при необходимости можно подключить **LLM-агента** через OpenRouter (без изменения схем и тестов) или использовать локальную модель.

> Проект предназначен для демонстрации методологии и прототипирования.

## 1) Быстрый старт

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
# source .venv/bin/activate

pip install -r requirements.txt

# Базовый запуск (оффлайн)
python -m soc_agentic_forensics analyze samples/case01 --out out/case01
python -m soc_agentic_forensics validate out/case01/report.json
```

Результат:

- `out/<case>/report.json` — машиночитаемый отчёт
- `out/<case>/report.md` — человекочитаемый отчёт

## 2) Демонстрационные кейсы Impacket

В репозитории есть минимальные примеры, иллюстрирующие Impacket-подобные шаблоны:

```bash
python -m soc_agentic_forensics analyze samples/case_impacket_smbexec --out out/impacket_smbexec
python -m soc_agentic_forensics analyze samples/case_impacket_wmiexec --out out/impacket_wmiexec
```

Ожидаемо: в `report.md` будет Finding уровня **medium** с признаком SMBExec/WMIExec.

## 3) Подключение LLM-агента (OpenRouter)

LLM не обязателен. Если хотите включить **LLM-агента**, выполните шаги из `config/README.md`.

Коротко:

```bash
cp config/openrouter.example.json config/openrouter.json

python -m soc_agentic_forensics analyze samples/case_impacket_smbexec \
  --use-api --api-config config/openrouter.json \
  --out out/impacket_smbexec_llm
```

## 4) Формат входных данных

На вход подаётся папка с JSON-файлами OSQuery (каждый файл — JSON-массив или JSON-объект).

Пример:

```text
case_x/
  system_info.json
  users.json
  processes.json
  listening_ports.json
  startup_items.json
```

## 5) Структура проекта

```text
schemas/                 # JSON Schema (report + finding)
soc_agentic_forensics/   # Python-пакет
  cli.py                 # CLI
  ingest.py              # загрузка/нормализация OSQuery JSON
  orchestrator.py        # fan-out/fan-in
  validate.py            # schema + детерминированные проверки
  render.py              # рендер отчёта в Markdown
  drift.py               # простая проверка дрейфа (similarity)
  agents/                # rule-based агенты
  agents_llm/            # LLM-агенты (опционально)
samples/                 # демонстрационные кейсы
tests/                   # smoke-тесты
config/                  # пример конфигурации LLM
```


