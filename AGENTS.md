# AGENTS.md

This file is the operating contract for autonomous agents working in this workspace. Read it before any other project work.

## Project Purpose

This repository preserves skills for controlling a real user-owned Chrome or Chrome Beta profile over CDP. The core safety rule is simple: do not let automation tools spawn their own browser for these workflows.

## Source Of Truth

- `README.md` - repo overview, runtime profile location, and verification commands.
- `real-agent-browser/SKILL.md` - required workflow for launching real Chrome with an explicit profile and CDP port.
- `real-agent-browser/scripts/real_chrome.py` - deterministic helper for status, command printing, CDP probing, and approved launches.
- `real-agent-browser-skyscanner/SKILL.md` - Skyscanner-specific follow-up skill.
- `real-agent-browser-esky/SKILL.md` - eSky-specific follow-up skill.
- `$HOME/.real-agent-browser` - private runtime Chrome profile. This is not part of the repository.

## Core Rules

- Never commit browser profiles, cookies, login databases, HAR files, credentials, or local auth state.
- Never launch Chrome for these workflows through `agent-browser open`, `agent-browser --profile`, Playwright, Puppeteer, or Chrome for Testing.
- The only allowed browser launch path is the direct macOS Chrome executable command with an explicit `--remote-debugging-port` and `--user-data-dir`.
- Use `agent-browser` only after the real Chrome process is already running, and only with `--cdp <port>` to attach to that existing browser.
- Before launch, inspect running Chrome and Chrome Beta processes and report which profile directory and debugging port they use.
- If the selected Chrome variant is already running, ask the user to close it and wait for explicit `OK` before launching.
- Warn before using a beta-looking profile with stable Chrome or a stable-looking profile with Chrome Beta.
- Print the exact launch command before running it.
- Do not bypass CAPTCHAs, access controls, or site security challenges. Stop and ask the user to handle those manually.

## Verification Commands

```bash
python3 -m py_compile real-agent-browser/scripts/real_chrome.py
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" real-agent-browser
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" real-agent-browser-skyscanner
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" real-agent-browser-esky
python3 real-agent-browser/scripts/real_chrome.py status
```

## Project Map

```text
.
|-- AGENTS.md
|-- README.md
|-- .gitignore
|-- real-agent-browser/
|   |-- SKILL.md
|   |-- agents/openai.yaml
|   `-- scripts/real_chrome.py
|-- real-agent-browser-skyscanner/
|   |-- SKILL.md
|   `-- agents/openai.yaml
`-- real-agent-browser-esky/
    |-- SKILL.md
    `-- agents/openai.yaml
```
