# Real Agent Browser

This repository stores Codex skills for using a user-owned, already-authenticated Chrome profile through Chrome DevTools Protocol (CDP), without spawning agent-browser-managed Chrome for Testing sessions.

## Skills

- `real-agent-browser/` - launch and verify stable Google Chrome or Google Chrome Beta with an explicit profile directory and debugging port.
- `real-agent-browser-skyscanner/` - Skyscanner workflows that must build on `real-agent-browser`.
- `real-agent-browser-esky/` - eSky workflows that must build on `real-agent-browser`.

## Runtime Profile

The reusable Chrome profile is stored outside this repository and is never part of the skill bundle:

```bash
$HOME/.real-agent-browser
```

Do not commit browser profiles, cookies, login data, HAR files, or local auth state.

## Important Commands

Check running Chrome processes and CDP status:

```bash
python3 real-agent-browser/scripts/real_chrome.py status
python3 real-agent-browser/scripts/real_chrome.py probe --port 9222
```

Print the stable Chrome launch command:

```bash
python3 real-agent-browser/scripts/real_chrome.py command --variant stable --profile "$HOME/.real-agent-browser" --port 9222 --url https://www.booking.com
```

Launch stable Chrome after explicit user confirmation:

```bash
python3 real-agent-browser/scripts/real_chrome.py launch --variant stable --profile "$HOME/.real-agent-browser" --port 9222 --url https://www.booking.com
```

Attach agent-browser only after Chrome is already running:

```bash
agent-browser --debug --cdp 9222 get url
```

Never use `agent-browser open`, `agent-browser --profile`, or any command that launches Chrome for Testing for these workflows.

## Verification

```bash
python3 -m py_compile real-agent-browser/scripts/real_chrome.py
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" real-agent-browser
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" real-agent-browser-skyscanner
python3 "$HOME/.codex/skills/.system/skill-creator/scripts/quick_validate.py" real-agent-browser-esky
```
