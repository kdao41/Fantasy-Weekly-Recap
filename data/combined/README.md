# Combined league history (Yahoo + Sleeper)

One history per league, with each person's Yahoo and Sleeper seasons merged into one career.
Built by `python3 scripts/sleeper_export.py combine <league>` from:

- `data/yahoo/<yahoo_folder>/raw/<season>.json` (finished, played Yahoo seasons)
- `data/sleeper/<league>/raw/<season>.json` (finished Sleeper seasons)
- `data/leagues.json` (which Yahoo folder belongs to which Sleeper league, and who is who)

| Folder | Seasons | From Yahoo | From Sleeper |
|---|---|---|---|
| `aggtown/` | 11 | 2015 to 2022 | 2023 to 2025 |
| `sobergang/` | 7 | 2019 to 2023 (as "Nooblets") | 2024 to 2025 |

If a year exists on both platforms (Yahoo auto-renews leagues nobody plays), the Sleeper season
wins and the Yahoo one is dropped. Unplayed seasons are never included.

## Files

Same files and fields as every summary folder; the full reference is
[../yahoo/aggtown/README.md](../yahoo/aggtown/README.md#file-reference). There is no `raw/` here:
the inputs live in `data/yahoo/` and `data/sleeper/`.

To tell which platform a season came from, use the season's `settings.league_key` in
`seasons/<year>/season.json`: Yahoo keys look like `414.l.219555`, Sleeper keys are long numbers
like `1257116455862808576`.

## Identity

`managers.json` is keyed by one id per person:

- Yahoo-era people: their Yahoo guid (e.g. `4O3C5BHIQCYX5O7EKHWFWKINKU`). Their Sleeper seasons
  are attached to the same guid through `leagues.json` `people`.
- Sleeper-only people: `sleeper:<user_id>` (e.g. Aggtown's `bAnmly`, Bryan, 2024 only).
- A Yahoo manager who hid their profile: `unknown-<season>-team<id>`.

`nicknames` lists every name the person used, Yahoo names first, so the display label is their
current Sleeper name, plus `(Real Name)` once `real_name` is filled in. Real names typed into the
Yahoo folder's `managers.json` are copied in on the next `combine`; you can also type them here.
After editing, run `combine` again to relabel every file.

## How results are defined across platforms

Both platforms are normalized to the same meanings (details in the Yahoo README):

- `final_rank` is the finish after the playoffs. Yahoo reports it; for Sleeper it comes from the
  winners bracket placement games (1st to 6th) and the toilet bowl (7th and below). In the toilet
  bowl the team that loses a game moves on, so whoever loses the final finishes last.
- `playoff_seed`: Yahoo reports it; for Sleeper it is the regular-season order by win %, then
  points for, checked against Sleeper's bracket every season.
- Placement games (3rd, 5th) count as playoff games; consolation-bracket games don't count toward
  `total_record`.
- `projected` points exist for Yahoo seasons only (Sleeper doesn't store projections); it is
  `null` in Sleeper weeks.

## What is NOT in the combined data

The summaries cover results: standings, weekly team scores, records, brackets and drafts. Everything
below exists only in the raw archives. All of it is saved, so none of it needs re-downloading.

### From Yahoo (`data/yahoo/<folder>/raw/yahoo_api/<season>/`, XML)

| Data | File | Notes |
|---|---|---|
| Weekly lineups: every rostered player, the slot used (`BN` bench, `IR`, or a starting slot), fantasy points and full stat line | `rosters/week-NN/team-NN.xml` | Starters' points sum exactly to the team score. Enough for bench points / coach ratings and player MVPs. |
| Transactions: adds, drops, trades, commissioner moves, with timestamps and teams | `transactions/page-NNN.xml` | 25 per page, newest first. |
| Season stat lines for every player rostered or drafted that year | `player_season_stats/batch-NNN.xml` | Stat ids named in `stat_categories.xml`. |
| League rules: scoring values per stat (`stat_modifiers`), roster slots, playoff and waiver settings, trade deadline | `settings.xml` | Use this to compare scoring eras. |
| Team and manager extras: logos, number of moves and trades, waiver priority, clinched flags, manager image and Yahoo rating (felo) | `standings.xml`, `teams.xml` | |
| Player injury status during a given week | `rosters/week-NN/team-NN.xml` | `status`, `injury_note` as of that week. |
| The unplayed 2023 Aggtown Yahoo league | `data/yahoo/aggtown/raw/yahoo_api/2023/` | League shell only, no games. |

Reading tips (namespace stripping, key formats) are in the Yahoo README's
[Raw data](../yahoo/aggtown/README.md#raw-data) section.

### From Sleeper (`data/sleeper/<league>/raw/sleeper_api/<season>/`, JSON)

| Data | File | Notes |
|---|---|---|
| Weekly lineups: `starters` (in roster-slot order), `players`, `players_points` for everyone, `starters_points` | `matchups/week-NN.json` | Bench points = `players_points` of non-starters. |
| Transactions: free-agent adds, waiver claims with FAAB bids, trades (players and draft picks) | `transactions/week-NN.json` | |
| Traded future draft picks | `traded_picks.json` | |
| Full playoff and consolation bracket structure | `winners_bracket.json`, `losers_bracket.json` | |
| End-of-season rosters, keepers, taxi, IR; moves made and FAAB spent; `ppts` (Sleeper's max potential points) | `rosters.json` | `ppts` is a ready-made "best possible lineup" total. |
| Scoring rules (42 settings) and roster slots | `league.json` | |
| Team names and avatars per season | `users.json` | |
| Player names, positions, ages, etc. | `data/sleeper/players_nfl.json` | A **current** snapshot: a player's team is where he plays now, not then. Use draft pick `metadata` for the team at draft time. |

See [../sleeper/README.md](../sleeper/README.md) for field details.
