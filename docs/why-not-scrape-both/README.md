# Why Not Scrape Both

Use `$why-not-scrape-both` when you want the same flight routes checked on both Skyscanner and eSky.com with verified logs.

## What It Uses

- `$real-agent-browser` for real Chrome/CDP.
- `$real-agent-browser-skyscanner` for Skyscanner-specific browser behavior.
- `$real-agent-browser-esky` for eSky-specific browser behavior.
- `$why-not-scrape-both` for orchestration, subagents, verifier rules, and merge policy.

The eSky portal in this workflow is only `https://www.esky.com`. There is no separate locale-specific eSky worker.

## Run Shape

Each run writes to:

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

Rows in portal logs keep evidence. Canonical `$HOME/flights.log` never keeps evidence columns.

## How To Start

Prompt example:

```text
Use $why-not-scrape-both.
Check these routes on Skyscanner and eSky.com:
ORIGIN ⇄ DEST — YYYY-MM-DD → YYYY-MM-DD
ORIGIN ⇄ DEST — YYYY-MM-DD → YYYY-MM-DD
2 adults, economy, direct only, exact airports, hotels off.
If prices appear in different currencies, ask me before converting.
```

The orchestrator should:

1. Confirm real Chrome/CDP.
2. Create the run directory.
3. Start one scraper worker.
4. Scrape route-first: `route -> skyscanner -> esky`.
5. Start two verifier workers after scraping.
6. Stop before merge and ask for model switch plus `OK MERGE`.

The orchestrator should ask whether the user wants to log in manually when portal login state is unclear or logged out. Currency conversion requires a user-selected target currency and rate.

## Verification Rules

Verifiers should be smart:

- Correct small price drift instead of failing.
- Use the user-provided currency rate.
- Accept stopover-to-direct improvements.
- Alarm on direct-to-stopover downgrade.
- Reject any visible airport-code mismatch unless nearby airports were explicitly allowed.
- Reject hotel prices, filter prices, loading placeholders, and date-strip prices.

## Merge

Merge only after all portal logs contain no `// PENDING` rows.

The merger reads only `// OK` rows, strips evidence, preserves old routes not covered by the new run, and refuses to silently replace old `DIRECT` with a stopover.
