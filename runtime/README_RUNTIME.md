# CompText Runtime

> RTK-style Output-Compression Layer für CompText-Termux-v2

## Was ist das?

`runtime/` ist eine Shell-Zwischenschicht, die CLI-Outputs (git, pytest, Logs, MedCodex)
**komprimiert bevor sie in den LLM-Kontext** (Claude Code, Groq etc.) gehen.

Inspiriert von:
- **RTK** – pro-Command Token-Reduktion via Shell-Proxy
- **Snip** – deklarative YAML-Filter-Pipelines
- **mcp-compressor** – Schema- und Response-Kompression

## Schnellstart

### Termux
```bash
bash scripts/install_hook_termux.sh
source ~/.bashrc

ctr git diff          # git diff → komprimiert
ctr pytest            # pytest → nur Fehler
ctr-log               # tail -n 100 → nur ERROR/WARNING
```

### Git Bash (Windows)
```bash
bash scripts/install_hook_gitbash.sh
source ~/.bashrc

ctr git status
ctr python -m pytest
```

### Manuell (stdin-Pipeline)
```bash
git diff | python -m runtime.cli --cmd "git diff"
git log --oneline -20 | python -m runtime.cli --profile repo

# Mit MCP-Server-Weiterleitung:
git diff | python -m runtime.cli --cmd "git diff" --mcp --mcp-url http://127.0.0.1:8100
```

## Profile

| Profil | Zuständig für              | Max Lines |
|--------|---------------------------|-----------|
| `dev`  | git, pytest, cargo, npm   | 200       |
| `med`  | MedCodex, Befunde, HL7    | 150       |
| `repo` | ls, find, sqlite3, JSON   | 100       |
| `log`  | tail, grep, journald      | 80        |

## Gain-Meter

Nach jeder Kompression in stderr:
```
╔══ comptext-runtime [dev]
║  Gain: [████████████░░░░░░░░] 62.3% gespart
╚══════════════════════════════════════
```

## MCP-Integration

Wenn `comptext-mcp-server` läuft:
```bash
git diff | python -m runtime.cli --cmd "git diff" --mcp
```

Der `mcp_client.py` spricht `/compress` deines bestehenden `comptext-mcp-server` an.

## Dateistruktur

```
runtime/
  __init__.py
  cli.py
  metrics.py
  mcp_client.py
  profiles/
    __init__.py
    dev.yml / med.yml / repo.yml / log.yml
  filters/
    dispatcher.py
    drop_lines.py / keep_section.py / collapse_repeats.py
    max_lines.py / keep_levels.py / abbreviate_medical.py / json_extract.py
hooks/
  comptext-rtx-hook.sh
scripts/
  install_hook_termux.sh
  install_hook_gitbash.sh
```
