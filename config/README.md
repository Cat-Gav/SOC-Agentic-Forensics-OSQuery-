# Конфигурация LLM (OpenRouter)

По умолчанию проект работает **без LLM**: выполняются детерминированные агенты и валидация отчёта по JSON Schema.

## Подключение LLM-агента

1) Скопируйте пример конфигурации:

```bash
cp config/openrouter.example.json config/openrouter.json
```

2) Откройте `config/openrouter.json` и замените `YOUR_API_KEY` на ваш ключ.

> `config/openrouter.json` намеренно добавлен в `.gitignore`, чтобы ключи не попадали в публичный репозиторий.

3) Запустите анализ с флагом `--use-api`:

```bash
python -m soc_agentic_forensics analyze samples/case_impacket_smbexec \
  --use-api --api-config config/openrouter.json \
  --out out/impacket_smbexec
```

## Примечания по безопасности

- Не коммитьте файлы с секретами.
- Для публичной демонстрации используйте пример конфигурации и передавайте реальные ключи приватно.
