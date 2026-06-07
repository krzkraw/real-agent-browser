---
name: why-not-scrape-both
description: Use when Codex needs to compare the same flight routes on Skyscanner and eSky.com, coordinate scraper/verifier subagents, produce verified flight logs, or merge verified portal results into the canonical flights log.
---

# Why Not Scrape Both

## Overview

Use this skill to run a two-portal flight scrape with one real Chrome profile: Skyscanner plus eSky.com. This skill orchestrates the workflow; it depends on the generic browser and portal skills instead of embedding portal-specific browser mechanics in them.

## Required Skills

Read and follow these before browser work:

- `$real-agent-browser`
- `$real-agent-browser-skyscanner`
- `$real-agent-browser-esky`

## Portal Scope

Only two portals participate:

- `skyscanner`: Skyscanner site.
- `esky`: `https://www.esky.com` only.

Do not split eSky by locale. Do not create locale-specific eSky workers or directories unless the user explicitly changes this skill's scope.

## Output Shape

Create a run directory:

```text
$HOME/flights_runs/YYYYMMDD_HHMMSS/
  skyscanner/
    flights.log
    fails.log
    raw.jsonl
    screens/
  esky/
    flights.log
    fails.log
    raw.jsonl
    screens/
```

Initialize every `flights.log` and `fails.log` with:

```text
| PATH | DATES | PRICE | INFO | SOURCE | EVIDENCE |
```

Portal rows use:

```text
| PATH | DATES | PRICE | INFO | SOURCE | // PENDING|OK|NIE OK - reason | screen: /absolute/card.png | page: /absolute/page.png |
```

Canonical `$HOME/flights.log` rows use exactly:

```text
| PATH | DATES | PRICE | INFO | SOURCE |
```

`SOURCE` is always `skyscanner` or `esky`.

## Browser Rules

- Use user-owned real Chrome over CDP only.
- One Chrome profile, one CDP port, two fixed portal tabs/windows.
- No test browser, Playwright, Puppeteer, Chrome for Testing, `agent-browser open`, `agent-browser --profile`, named sessions, or test sessions.
- Attach only after Chrome is running: `agent-browser --debug --cdp <port> ...`.
- Multiple Chrome windows are allowed inside the same running Chrome process/profile.
- CAPTCHA/access challenge stops only the active scraper step. Ask the user to solve it manually, wait for `OK`, then resume the same route and portal.

## Worker Plan

Use low-cost workers where available:

- scraper/verifier agents: `GPT-5.4-mini`
- merger/review: stronger model; do not run merger on a low-cost model

Workers:

- `flight_master`: orchestrator in the current thread.
- `flight_scraper`: the only browser worker.
- `verifier_skyscanner`: verifies Skyscanner screenshots/log rows.
- `verifier_esky`: verifies eSky.com screenshots/log rows.
- `flight_merger`: optional later merge step.

The orchestrator must not scrape or verify in-band. If a worker cannot start, close completed workers and retry once; if still blocked, stop with pending rows reported.

## Scrape Order

Use route-first order:

```text
route 1 -> skyscanner -> esky
route 2 -> skyscanner -> esky
...
```

The single scraper owns all browser actions and may switch the active portal tab/window before taking screenshots.

## Verification Policy

Verifiers compare the pending row, screenshot evidence, and current canonical `$HOME/flights.log` baseline for the same `PATH + DATES + SOURCE`.

They should update obvious current values instead of failing exact-string mismatches:

- Same route/date/source and visible price differs slightly: update price and mark `// OK`.
- Price drift tolerance: `100 PLN` after conversion or `30 USD` before conversion.
- If user provided a currency rate, use that exact rate. For this travel run, `1 USD = 3.68 PLN`.
- Baseline stopover becoming current `DIRECT`: accept as an improvement, update `INFO` to `DIRECT`, update price, mark `// OK`.
- Baseline `DIRECT` becoming current stopover: fail with `// NIE OK - prior DIRECT became stopover; user review required`, unless another verified current direct row exists for that route/date/source.
- Any visible airport code mismatch with requested origin/destination is not normal drift. Fail or escalate unless the user explicitly allowed nearby airports.
- Hotels, filter-sidebar prices, loading placeholders, date strips, and nearby-date teasers are not flight-card prices.
- A no-results row is valid only when an explicit no-results state is visible under the active filters.

## Merge Policy

Merge only after all portal `flights.log` files have no `// PENDING` rows and the user explicitly approves the merge.

Before merge, say:

```text
STOP. Switch model to 5.5, then type OK MERGE.
```

Merge reads only `// OK` rows from portal logs. It strips evidence/comment columns before writing canonical `$HOME/flights.log`.

Canonical key:

```text
PATH + DATES + INFO + SOURCE
```

Smart replacement:

- For the same `PATH + DATES + SOURCE`, current verified `DIRECT` replaces stale stopover rows unless the current run also has a distinct verified stopover option.
- Current stopover must not silently replace old `DIRECT`; report a downgrade conflict.
- Preserve old canonical rows for routes not covered by the current run unless the user explicitly asked for stale deletion.
- If any row still contains `USD`, `PENDING`, or evidence columns, stop and fix before writing canonical output.

## Subagent Prompts

When spawning subagents, load:

```text
why-not-scrape-both/references/subagents.md
```

Use only the relevant section for that worker to keep context small.
