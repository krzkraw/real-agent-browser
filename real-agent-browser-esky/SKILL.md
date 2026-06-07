---
name: real-agent-browser-esky
description: Use when Codex needs to search eSky, compare eSky flight results, inspect eSky flight options, or preserve eSky state through the user's real Chrome profile without launching Chrome for Testing or an agent-browser-managed browser.
---

# Real Agent Browser eSky

## Overview

Use this skill only after `$real-agent-browser` has launched or attached to the user's real Chrome profile. Keep eSky work in that real browser over CDP, with the default agent-browser session and explicit CDP port.

## Required Browser Path

1. Use `$real-agent-browser` first.
2. Confirm real stable Chrome or Chrome Beta is running with the expected profile and CDP port.
3. Attach with `agent-browser --debug --cdp <port>`.
4. Do not use `--session`, `--session-name`, or `AGENT_BROWSER_SESSION`.
5. Do not run `agent-browser open`, `agent-browser --profile`, Playwright, Puppeteer, or Chrome for Testing.

## User Defaults

Ask only for values not covered by defaults, but always tell the user these defaults can be overridden:

- Trip type: round trip.
- Cabin: economy.
- Stops: direct flights only.
- Nearby airports: off by choosing exact airports when possible.
- Hotels: off.
- Extra filters: none unless the user asks.

Ask for origin, destination, dates, and travelers unless already provided. Say the defaults before searching, for example: "I will use round trip, economy, direct only, exact airports, no hotel search, and no extra filters unless you want to override any of those."

## Site State

- If a cookie banner appears, accept all cookies.
- Check login state from the header/account UI. On eSky, `My account` can open a login modal with email/password fields when the user is not logged in.
- If the user is not logged in or the state is unclear, ask whether they want to log in manually. If they choose to log in, wait for `OK`; do not automate credentials.
- If eSky presents CAPTCHA or an access challenge, stop and ask the user to solve it manually. Do not bypass or automate the challenge.

## Search Flow

- Navigate in the existing real Chrome tab or create a CDP tab; do not use `agent-browser open`.
- eSky can default the origin from location, so always verify and clear the origin field before entering a requested airport.
- Prefer exact airport choices over city/country choices. For `Krakow`, choose `(KRK) Balice`; for Albania direct flights, choose `(TIA) Mother Teresa`.
- The home form does not expose direct-only. Submit first, then apply `Stops -> Direct` on the results page.
- Before submitting, verify origin, destination, dates, travelers, cabin, and hotel state.

## Date Picker Notes

- The eSky date picker may expose only month-level text in accessibility snapshots.
- Use the visible calendar's next-month arrow to move from June/July 2026 to August/September 2026 for September dates.
- If individual day cells are not exposed as refs, locate visible calendar day cells in DOM and click the center of the target day with pointer/mouse events.
- Confirm dates from input values after selection, e.g. `dates_from = 16 Sep 2026`, `dates_to = 30 Sep 2026`.

## Learned KRK-Albania Example

For Krakow to Albania, September 16-30, 2026, two adults:

- Origin: choose `(KRK) Balice`.
- Destination: eSky does not offer `Albania` as a useful country target in the flight form; choose `(TIA) Mother Teresa`.
- Dates: outbound `16 Sep 2026`, return `30 Sep 2026`.
- Travelers: `2 people`.
- Defaults used: round trip, economy, exact airports, hotel search off, no extra filters before results.
- Results route observed:

```text
https://www.esky.com/flights/search/ap/KRK/ap/TIA?pa=2&sc=economy&departureDate=2026-09-16&returnDate=2026-09-30
```

- Direct-only filter observed:

```text
&filters=%7B%22Transfers%22:%5B%22None%22%5D%7D
```

Observed direct results included Wizz Air and Ryanair KRK-TIA outbound/return combinations. Report prices with "observed now" wording and remind the user that eSky availability and prices can change.
