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

## Демонстрация результата

Ниже приведены воспроизводимые примеры отчётов, сформированных прототипом по данным OSQuery.
Кейсы моделируют реальные техники атак и показывают как детерминированную часть анализа, так и (опционально) работу LLM-агента.

### Набор демонстрационных кейсов

| Кейс | Инструмент/сценарий | MITRE ATT&CK | Что демонстрируется | Отчёт |
|---|---|---|---|---|
| Impacket SMBExec | Админ-шары SMB, удалённое выполнение | T1021.002 | Признаки lateral movement по командной строке и сетевым портам | [`impacket_smbexec_report.md`](docs/demo_outputs/impacket_smbexec_report.md) |
| Impacket WMIExec | Выполнение через WMI | T1047 | Исполнение через WMI и характерные артефакты процесса | [`impacket_wmiexec_report.md`](docs/demo_outputs/impacket_wmiexec_report.md) |
| Отказ LLM API | 503 / невалидный JSON | — | Корректная деградация: ошибка фиксируется как pipeline-issue, базовый анализ не ломается | [`llm_failure_report.md`](docs/demo_outputs/llm_failure_report.md) |

