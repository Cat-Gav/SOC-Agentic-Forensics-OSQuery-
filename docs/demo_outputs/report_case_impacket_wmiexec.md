# OSQuery Forensics Report — case_impacket_wmiexec

- **Generated at:** 2026-01-30T20:04:51Z
- **Hostname:** WS-ACCT-07
- **Overall severity:** medium

## Findings

### 1. Impacket-like Activity (WMIExec)
- **Category:** network
- **Severity:** medium
- **Confidence:** 0.8

Обнаружены характерные шаблоны командной строки, совпадающие с техникой удалённого выполнения команд через SMB/WMI (типично для Impacket).

**Evidence:**
- `processes.json` `$[0].cmdline`
  - Excerpt: `cmd.exe /Q /c dir 1> \\\\127.0.0.1\\ADMIN$\\__A1B2C3D4 2>&1`
- `listening_ports.json` `$[1].port`
  - Excerpt: `445`

**Recommendations:**
- Сопоставьте процесс с родительским процессом и учётной записью, от имени которой выполнялось действие.
- Проверьте сетевые соединения на 445/135 и события аутентификации (LogonType=3) для корреляции.
