---
name: real-agent-browser
description: Launch and attach to a user-owned real Google Chrome or Google Chrome Beta profile over Chrome DevTools Protocol without spawning Chrome for Testing or an agent-browser-managed browser. Use when Codex needs live browser access to sites that should run in the user's normal profile, when the user mentions real Chrome, Chrome Beta, CDP, debugging port, profile directories, Booking.com, Skyscanner, or avoiding agent-browser-launched test browsers.
---

# Real Agent Browser

## Overview

Use the user's real Chrome profile by launching Chrome directly with `--remote-debugging-port` and `--user-data-dir`, then attach tools to that existing CDP endpoint. Do not use this skill to bypass CAPTCHAs, access controls, or site security challenges; ask the user to handle those manually.

## Hard Rules

- Never run `agent-browser open`, `agent-browser --profile`, Playwright, Puppeteer, Chrome for Testing, or any command that launches an automation-owned browser.
- Use `agent-browser` only after real Chrome is already running, and only with `--cdp <port>`.
- Do not use named or test sessions for this workflow. Omit `--session`, `--session-name`, and `AGENT_BROWSER_SESSION`; attach with the default session plus the explicit CDP port.
- Always inspect running stable Chrome and Chrome Beta processes before choosing a launch command.
- Always tell the user what is currently running, including variant, PID, profile directory, and debugging port when detectable.
- Offer the user a choice between stable Chrome and Chrome Beta.
- If the chosen variant is already running, tell the user to close it and wait for explicit `OK` before launching.
- Warn before using Chrome Beta with a non-beta-looking profile directory, or stable Chrome with a beta-looking profile directory.
- Print the exact launch command before running it.
- Confirm CDP works after launch before reporting success.

## Known Profile

Default stable profile:

```bash
$HOME/.real-agent-browser
```

This profile may contain cookies, login state, and other private data. Do not print, copy, commit, or inspect secret-bearing profile contents.

Recommended beta profile:

```bash
$HOME/.real-agent-browser-beta
```

Do not use the stable profile for Beta unless the user explicitly accepts the warning.

## Launch Commands

Stable Chrome on macOS:

```bash
"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
  --remote-debugging-port=9222 \
  --user-data-dir="$HOME/.real-agent-browser" \
  "https://www.booking.com"
```

Chrome Beta on macOS:

```bash
"/Applications/Google Chrome Beta.app/Contents/MacOS/Google Chrome Beta" \
  --remote-debugging-port=9223 \
  --user-data-dir="$HOME/.real-agent-browser-beta" \
  "https://www.booking.com"
```

Attach after launch:

```bash
agent-browser --debug --cdp 9222 get url
```

Use the matching port for Beta if launched on `9223`.

## Workflow

1. Run status:

```bash
python3 real-agent-browser/scripts/real_chrome.py status
```

2. Report detected processes. Include stable/Beta, PID, profile, and port.
3. Offer a stable-vs-Beta choice. Recommend stable with `$HOME/.real-agent-browser` unless the user asks for Beta.
4. If the chosen variant is running, stop and ask the user to close it. Wait for `OK`.
5. Print the command:

```bash
python3 real-agent-browser/scripts/real_chrome.py command --variant stable --profile "$HOME/.real-agent-browser" --port 9222 --url https://www.booking.com
```

6. Ask for explicit `OK` before launch.
7. Launch only with the helper or the printed direct command:

```bash
python3 real-agent-browser/scripts/real_chrome.py launch --variant stable --profile "$HOME/.real-agent-browser" --port 9222 --url https://www.booking.com
```

8. Probe CDP:

```bash
python3 real-agent-browser/scripts/real_chrome.py probe --port 9222
```

9. Attach with agent-browser only through the default session and explicit CDP port:

```bash
agent-browser --debug --cdp 9222 get url
```

10. Report success only after CDP responds and the page URL/title can be read.

## Helper

Use `scripts/real_chrome.py` for deterministic checks. It does not call `agent-browser` and refuses to launch the selected Chrome variant while that variant is already running.
