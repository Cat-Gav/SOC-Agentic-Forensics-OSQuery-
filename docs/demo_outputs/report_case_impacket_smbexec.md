# OSQuery Forensics Report — case_impacket_smbexec

- **Generated at:** 2026-01-30T20:04:35Z
- **Hostname:** WS-FIN-12
- **Overall severity:** medium

## Findings

### 1. Impacket-like Activity (SMBExec)
- **Category:** network
- **Severity:** medium
- **Confidence:** 0.8

Обнаружены характерные шаблоны командной строки, совпадающие с техникой удалённого выполнения команд через SMB/WMI (типично для Impacket).

**Evidence:**
- `processes.json` `$[0].cmdline`
  - Excerpt: `cmd.exe /Q /c echo whoami ^> \\\\127.0.0.1\\ADMIN$\\__E7F3A9B1 2^>^&1`
- `listening_ports.json` `$[0].port`
  - Excerpt: `445`

**Recommendations:**
- Сопоставьте процесс с родительским процессом и учётной записью, от имени которой выполнялось действие.
- Проверьте сетевые соединения на 445/135 и события аутентификации (LogonType=3) для корреляции.
