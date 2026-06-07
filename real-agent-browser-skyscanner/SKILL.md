---
name: real-agent-browser-skyscanner
description: Use when Codex needs to search Skyscanner, compare flight results, inspect flight options, or preserve Skyscanner state through the user's real Chrome profile without launching Chrome for Testing or an agent-browser-managed browser.
---

# Real Agent Browser Skyscanner

## Overview

Use this skill only after `$real-agent-browser` has launched or attached to the user's real Chrome profile. Keep Skyscanner work in that real browser over CDP, and avoid automation patterns that look like a fresh bot session.

## Required Browser Path

1. Use `$real-agent-browser` first.
2. Confirm real stable Chrome or Chrome Beta is running with the expected profile and CDP port.
3. Attach with the default agent-browser session and explicit port: `agent-browser --debug --cdp <port>`.
4. Do not use `--session`, `--session-name`, or `AGENT_BROWSER_SESSION`.
5. Do not run `agent-browser open`, `agent-browser --profile`, Playwright, Puppeteer, or Chrome for Testing.

## User Defaults

When collecting requirements, ask only for values not covered by defaults, but always tell the user these defaults can be overridden:

- Trip type: round trip.
- Cabin: economy.
- Stops: direct flights only.
- Nearby airports: off for origin and destination.
- Hotels: off.
- Extra filters: none unless the user asks.

Ask for origin, destination, dates, and travelers unless already provided. Mention the default block in plain language before searching, for example: "I will use round trip, economy, direct only, no nearby airports, no hotel search, and no extra filters unless you want to override any of those."

## Site State

- If a cookie banner appears, accept all cookies.
- Check login state from the header/profile UI, not footer links. A footer `Sign in`/`Zaloguj sie` link can exist even when the header shows profile access.
- If the user is not logged in or the state is unclear, ask whether they want to log in manually. If they choose to log in, wait for `OK`; do not automate credentials.
- If Skyscanner presents CAPTCHA or an access challenge, stop and ask the user to solve it manually. Do not bypass or automate the challenge.

## Safer Search Flow

- Prefer normal UI setup for fields and filters, but keep actions human-paced where possible.
- Before submitting, re-snapshot and verify origin, destination, dates, travelers, cabin, direct-only, nearby-airport, and hotel settings.
- If submitting the form triggers CAPTCHA and the user solves it manually, continue in the same real Chrome tab and CDP port.
- After CAPTCHA is solved, direct navigation to the results URL can be used when the route is known. For KRK to Tirana:

```text
https://www.skyscanner.pl/transport/loty/krk/tira/260916/260930/?adultsv2=2&cabinclass=economy&rtn=1&preferdirects=true
```

Always re-check live page state after navigation because prices, filters, and availability change.

## Learned KRK-Albania Example

For Krakow to Albania, September 16-30, 2026, two adults:

- Origin: `Krakow (KRK)`.
- Destination: choose `Albania (AL)` when requested, then verify results resolve to Tirana for direct KRK flights.
- Dates: outbound `16.09.2026`, return `30.09.2026`.
- Travelers: `2 adults`.
- Defaults used: round trip, economy, direct flights only, nearby airports off, hotel search off, no extra filters.
- Results route observed: `/transport/loty/krk/tira/260916/260930/`.

Observed direct result types included Wizz Air and Buzz KRK-TIA outbound/return combinations. Report prices with "observed now" wording and remind the user that Skyscanner availability and prices can change.
