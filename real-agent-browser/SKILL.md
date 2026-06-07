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
- If the chosen variant is already running with the expected profile and CDP port, attach to it and create/use additional tabs or windows inside that same browser.
- If the chosen variant is already running without the required CDP port or with the wrong profile, tell the user to close it and wait for explicit `OK` before launching.
- Multiple Chrome windows on one profile are allowed inside one running Chrome process. Do not launch multiple Chrome processes with the same `--user-data-dir` on different CDP ports.
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

## Platform Support Status

The macOS launch path is the tested path for this repository. Windows and Linux commands below are researched candidate commands, not confirmed support. When working on Windows or Linux:

- Warn the user that the command is untested in this repo.
- Ask the user to run or approve one candidate at a time.
- Verify the result with CDP and by asking the user whether the expected Chrome window/profile opened.
- Iterate until the user explicitly confirms which command works on that platform.
- Do not update scripts or claim platform support until user confirmation exists.
- After a user confirms a working Windows or Linux launch method, ask whether they want a pull request to this repo. If yes, create the PR only after tests and review.

Research basis:

- Chrome DevTools documents `start chrome --remote-debugging-port=PORT` for Windows and `google-chrome --remote-debugging-port=PORT` for Linux.
- Chrome 136+ ignores `--remote-debugging-port` on the default Chrome data directory; use a non-default `--user-data-dir`.
- Chromium documents `--user-data-dir` examples for Windows and Linux, and warns that two Chrome instances cannot share one user data directory.

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

Candidate stable Chrome on Windows, PowerShell:

```powershell
$profile = "$env:USERPROFILE\.real-agent-browser"
New-Item -ItemType Directory -Force $profile | Out-Null
$chrome = @(
  "$env:ProgramFiles\Google\Chrome\Application\chrome.exe",
  "${env:ProgramFiles(x86)}\Google\Chrome\Application\chrome.exe",
  "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
) | Where-Object { Test-Path $_ } | Select-Object -First 1
if (-not $chrome) { throw "Chrome executable not found; ask the user to locate chrome.exe." }
& $chrome --remote-debugging-port=9222 --user-data-dir="$profile" "https://www.booking.com"
```

Candidate stable Chrome on Windows, cmd.exe:

```bat
if not exist "%USERPROFILE%\.real-agent-browser" mkdir "%USERPROFILE%\.real-agent-browser"
"%ProgramFiles%\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="%USERPROFILE%\.real-agent-browser" "https://www.booking.com"
```

Candidate stable Chrome on Linux:

```bash
mkdir -p "$HOME/.real-agent-browser"
google-chrome --remote-debugging-port=9222 --user-data-dir="$HOME/.real-agent-browser" "https://www.booking.com"
```

If `google-chrome` is not present on Linux, ask the user to confirm the installed binary and try one candidate at a time, commonly `google-chrome-stable`, `chromium-browser`, or `chromium`.

Candidate Chrome Beta on Linux, if installed:

```bash
mkdir -p "$HOME/.real-agent-browser-beta"
google-chrome-beta --remote-debugging-port=9223 --user-data-dir="$HOME/.real-agent-browser-beta" "https://www.booking.com"
```

For any Windows or Linux candidate, verify:

```text
curl http://127.0.0.1:9222/json/version
agent-browser --debug --cdp 9222 get url
```

Also ask the user to inspect `chrome://version` and confirm the command line contains the expected `--remote-debugging-port` and `--user-data-dir`.

## Workflow

1. Run status:

```bash
python3 real-agent-browser/scripts/real_chrome.py status
```

2. Report detected processes. Include stable/Beta, PID, profile, and port.
3. Offer a stable-vs-Beta choice. Recommend stable with `$HOME/.real-agent-browser` unless the user asks for Beta.
4. If the chosen variant is already running with the expected profile and CDP port, attach to it. If it is running without the required CDP port or with the wrong profile, stop and ask the user to close it. Wait for `OK`.
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

## Windows/Linux Confirmation Workflow

For Windows or Linux, do not rely on the helper as proof of support. Use this loop:

1. State that Windows/Linux launch is untested in this repo.
2. Print one candidate command for the user's OS.
3. Ask the user to run or approve it.
4. Probe CDP and ask the user to confirm the visible Chrome result.
5. If it fails, collect the exact error and try the next candidate binary/path.
6. When the user says which command works, record the exact OS, Chrome channel, executable path, profile path, command, and verification output.
7. Ask: "Do you want me to create a pull request to add this Windows/Linux launch method to your repo?"
8. If the user says yes, create a branch, implement support, run tests and review, then create the PR.

## Helper

Use `scripts/real_chrome.py` for deterministic macOS checks. It does not call `agent-browser` and refuses to launch the selected Chrome variant while that variant is already running. Do not extend its platform claims until Windows or Linux commands have been verified by a user on that platform.
