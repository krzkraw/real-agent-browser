# AGENTS.md

This file is the operating contract for autonomous agents working in this workspace. Read it before any other project work.

## Project Purpose

This repository preserves skills for controlling a real user-owned Chrome or Chrome Beta profile over CDP. The core safety rule is simple: do not let automation tools spawn their own browser for these workflows.

## Source Of Truth

- `README.md` - repo overview, runtime profile location, and verification commands.
- `real-agent-browser/SKILL.md` - required workflow for launching real Chrome with an explicit profile and CDP port.
- `real-agent-browser/scripts/real_chrome.py` - deterministic macOS helper for status, command printing, CDP probing, and approved launches.
- `real-agent-browser-skyscanner/SKILL.md` - Skyscanner-specific follow-up skill.
- `real-agent-browser-esky/SKILL.md` - eSky-specific follow-up skill.
- `why-not-scrape-both/SKILL.md` - orchestration skill for checking the same routes on Skyscanner and eSky.com, with scraper/verifier/merger workflow.
- `docs/why-not-scrape-both/README.md` - concise usage guide for the orchestrated flow.
- `$HOME/.real-agent-browser` - private runtime Chrome profile. This is not part of the repository.

## Core Rules

- Never commit browser profiles, cookies, login databases, HAR files, credentials, or local auth state.
- Never launch Chrome for these workflows through `agent-browser open`, `agent-browser --profile`, Playwright, Puppeteer, or Chrome for Testing.
- The only allowed browser launch path is a direct Chrome executable command with an explicit `--remote-debugging-port` and `--user-data-dir`; macOS is the tested implementation in this repo.
- Use `agent-browser` only after the real Chrome process is already running, and only with `--cdp <port>` to attach to that existing browser.
- Before launch, inspect running Chrome and Chrome Beta processes and report which profile directory and debugging port they use.
- If the selected Chrome variant is already running with the expected profile and CDP port, attach to it and create/use additional tabs or windows inside that same browser.
- If the selected Chrome variant is already running without the required CDP port or with the wrong profile, ask the user to close it and wait for explicit `OK` before launching.
- Multiple Chrome windows on one profile are allowed inside one running Chrome process. Do not launch multiple Chrome processes with the same `--user-data-dir` on different CDP ports.
- Warn before using a beta-looking profile with stable Chrome or a stable-looking profile with Chrome Beta.
- Print the exact launch command before running it.
- Do not bypass CAPTCHAs, access controls, or site security challenges. Stop and ask the user to handle those manually.
- macOS Chrome launch is tested here. Windows and Linux launch commands are candidate-only until a user verifies them on that platform.
- For Windows/Linux, warn that support is untested, try one candidate command at a time, verify CDP plus visible browser behavior, and ask whether to create a PR only after the user confirms the working command.

## Verification Commands

```bash
python3 -m py_compile real-agent-browser/scripts/real_chrome.py
npx skills use . --skill real-agent-browser >/dev/null
npx skills use . --skill real-agent-browser-skyscanner >/dev/null
npx skills use . --skill real-agent-browser-esky >/dev/null
npx skills use . --skill why-not-scrape-both >/dev/null
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
|-- real-agent-browser-esky/
|   |-- SKILL.md
|   `-- agents/openai.yaml
|-- why-not-scrape-both/
|   |-- SKILL.md
|   |-- agents/openai.yaml
|   `-- references/subagents.md
`-- docs/why-not-scrape-both/
    `-- README.md
```
