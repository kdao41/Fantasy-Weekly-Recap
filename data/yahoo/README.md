# Yahoo league history

Yahoo Fantasy seasons, pulled by `scripts/yahoo_scrape.py` through a logged-in browser session.
(Yahoo stopped serving its Fantasy API to unapproved developer apps in 2026; its website still
reads the same API with the browser's login.)

| Folder | League on Yahoo | Seasons | Continues on Sleeper as |
|---|---|---|---|
| `aggtown/` | Aggtown FFL | 2015 to 2022 played (2023 created but never played) | Aggtown (2023 on) |
| `nooblets/` | Nooblets (2019), Nooblets Season 2 (2020 to 2022), Nooblets Season 5 (2023) | 2019 to 2023 | Sober Gang (2024 on) |

**The full reference for every file, field and definition is
[aggtown/README.md](aggtown/README.md).** `nooblets/` has exactly the same structure; only the
league and years differ. The combined Yahoo + Sleeper history is in `data/combined/`.

## Nooblets specifics

- One continuous league under three names; `fetch` follows Yahoo's season-to-season links.
- Yahoo kept auto-renewing it after the group moved to Sleeper, so 2024 to 2026 Yahoo seasons
  exist but are not this league's history. `nooblets/fetch_config.json` (`"until": 2023`) makes
  every `fetch` and `archive` stop at 2023.
- 10 teams every season, 6-team playoffs with byes for seeds 1 and 2.
- Raw archive: `nooblets/raw/yahoo_api/` has the same files as Aggtown's (lineups, transactions,
  player season stats). If a season folder looks short, the archive was interrupted by Yahoo's
  rate limit; rerun `uv run --python 3.12 scripts/yahoo_scrape.py archive nooblets` and it
  resumes, skipping files it already has.

## Access limits

- Only leagues and seasons the logged-in account was a member of are readable. Aggtown 2014
  (`331.l.982878`) is refused for that reason.
- Yahoo throttles bursts with HTTP 999; the archiver backs off for up to 8 minutes per request.
- The login lives in a dedicated Chromium profile at `~/.yahoo-fantasy-browser` (outside the repo).
  Only one script can use it at a time. Run `yahoo_scrape.py login` again if it expires.
