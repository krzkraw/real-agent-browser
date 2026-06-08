# Real Agent Browser

This repository stores Codex skills for using a user-owned, already-authenticated Chrome profile through Chrome DevTools Protocol (CDP), without spawning agent-browser-managed Chrome for Testing sessions.

## Skills

- `real-agent-browser/` - launch and verify stable Google Chrome or Google Chrome Beta with an explicit profile directory and debugging port.
- `real-agent-browser-skyscanner/` - Skyscanner workflows that must build on `real-agent-browser`.
- `real-agent-browser-esky/` - eSky workflows that must build on `real-agent-browser`.
- `why-not-scrape-both/` - orchestrated Skyscanner + eSky.com scrape/verify/merge workflow built on the three skills above.

## Why Not Scrape Both

Use this when the same route/date set should be checked on Skyscanner and eSky.com with verifier subagents:

```text
Use $why-not-scrape-both.
Check these routes on Skyscanner and eSky.com:
ORIGIN ⇄ DEST — YYYY-MM-DD → YYYY-MM-DD
2 adults, economy, direct only, exact airports, hotels off.
If prices appear in different currencies, ask me before converting.
```

Runtime output:

```text
$HOME/flights_runs/YYYYMMDD_HHMMSS/
  skyscanner/{flights.log,fails.log,raw.jsonl,screens/}
  esky/{flights.log,fails.log,raw.jsonl,screens/}
```

The flow uses one scraper worker, then two verifier workers. The canonical `$HOME/flights.log` is updated only by the later merger step after explicit user approval. See `docs/why-not-scrape-both/README.md` for the short usage guide.

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

## Windows And Linux

macOS launch is the tested path in this repo. Windows and Linux launch commands are documented in `real-agent-browser/SKILL.md` as untested candidates based on Chrome/Chromium documentation. Agents must warn the user, test one candidate at a time, verify CDP plus visible browser behavior, and ask whether to create a PR only after the user confirms a working command.

## Verification

```bash
python3 -m py_compile real-agent-browser/scripts/real_chrome.py
npx skills use . --skill real-agent-browser >/dev/null
npx skills use . --skill real-agent-browser-skyscanner >/dev/null
npx skills use . --skill real-agent-browser-esky >/dev/null
npx skills use . --skill why-not-scrape-both >/dev/null
```
