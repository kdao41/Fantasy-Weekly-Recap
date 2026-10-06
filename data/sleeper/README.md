# Sleeper league history

Finished Sleeper seasons, archived by `python3 scripts/sleeper_export.py fetch [league]` from
Sleeper's public API (no login). Leagues and their Sleeper ids come from `data/leagues.json`.

| Folder | League | Seasons | Not included |
|---|---|---|---|
| `aggtown/` | AGGTOWN FANTASY LEAGUE, 12 teams | 2023, 2024, 2025 | 2026 (in progress, shown live by the Almanac) |
| `sobergang/` | Sober Gang, 10 teams | 2024, 2025 | 2026 (in progress) |

The years before Sleeper are on Yahoo (`data/yahoo/`); `data/combined/` merges the two. Most
readers want `data/combined/`, see [../combined/README.md](../combined/README.md).

## Layout

```
players_nfl.json                     Sleeper's player directory, shared (about 12,000 players, 14 MB)
<league>/
  managers.json, league_history.*, manager_*_records.csv, all_weekly_scores.csv,
  weekly_standings.csv, weekly_highlights.csv, seasons/<year>/...   Sleeper-only summaries
  raw/<season>.json                  normalized season (platform-neutral; input to the builders)
  raw/sleeper_api/<season>/          every API response exactly as Sleeper sent it
    league.json                      settings, scoring_settings, roster_positions, previous_league_id
    users.json                       members: user_id, display_name, metadata.team_name, avatar
    rosters.json                     roster_id <-> owner_id, record, points, end-of-season players
    matchups/week-NN.json            one row per team per week
    winners_bracket.json             playoff bracket
    losers_bracket.json              consolation bracket
    drafts.json, draft-<id>-picks.json
    transactions/week-NN.json        all moves that week
    traded_picks.json
```

The summary files have the same format as every other summary folder; the reference is
[../yahoo/aggtown/README.md](../yahoo/aggtown/README.md#file-reference).

## Reading the raw JSON

- **Ids:** teams are `roster_id` (1 to N, stable within a season); people are `owner_id` /
  `user_id`. Join `rosters.owner_id` to `users.user_id` for names. `roster_id` is reused across
  seasons for different people, so always go through `owner_id` across years.
- **Seasons chain** through `league.previous_league_id`; each season has its own `league_id`.
- **`matchups/week-NN.json`:** `points` is the team score. Two rows with the same `matchup_id`
  played each other. `matchup_id: null` means no game that week (a playoff bye, or eliminated).
  `starters` lists player ids in the order of `league.roster_positions`; `players_points` covers
  every rostered player, so bench points are the non-starters' entries.
- **Brackets:** each game has `r` (round; week = `settings.playoff_week_start + r - 1`), `m`
  (game id), `t1`/`t2` (roster ids), `w`/`l` (winner/loser), and `p` on placement games
  (`p: 1` championship, `p: 3` third place, `p: 5` fifth). `t1_from: {"w": m}` means "winner of
  game m". In `losers_bracket.json` these Aggtown and Sober Gang brackets advance winners, so its
  `p: 1` winner finishes just below the playoff teams (7th of 12).
- **`rosters.settings`:** `wins`/`losses`/`ties` are regular season only. Points are split into
  whole and hundredths: `fpts + fpts_decimal / 100` (same for `fpts_against` and `ppts`, the max
  potential points).
- **Transactions:** `type` is `free_agent`, `waiver` or `trade`; `adds`/`drops` map player id to
  roster id; `settings.waiver_bid` is the FAAB bid; `draft_picks` lists picks moved in trades;
  `leg` is the week; `created` is a Unix time in milliseconds.
- **Players:** `players_nfl.json` maps player id to `full_name`, `position`, `team`, and more.
  It is today's snapshot, so `team` is a player's current team. Team defenses use the team code
  as the id (`"KC"`).

## How raw/<season>.json is derived

`sleeper_export.py` `normalize()`:

- **Records:** from `rosters.settings` (checked against the weekly games on every build).
- **Seeds:** regular-season order by win %, then points for; the top `settings.playoff_teams` are
  seeded and checked against the teams in the winners bracket.
- **Final rank:** winners bracket placement games give 1st to 6th, the consolation bracket 7th
  to 12th; anyone left unplaced is filled in by regular-season order.
- **Weeks:** games are paired by `matchup_id`. In playoff weeks a game is `is_consolation` unless
  its pair is in the winners bracket for that round (playoff-week games outside both brackets are
  treated as consolation).
- **Draft:** player name, position and team from the pick's `metadata` (the team at draft time).
- **Managers:** `manager_guid` is `sleeper:<owner_id>`; `combine` swaps in the Yahoo guid for
  people linked in `leagues.json`.
