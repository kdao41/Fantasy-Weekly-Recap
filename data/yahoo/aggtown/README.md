# Aggtown FFL: Yahoo league history

Complete history of the Aggtown FFL fantasy football league from its Yahoo years,
**2015 through 2022** (8 played seasons). The league moved to Sleeper afterwards: its
Sleeper seasons are in `data/sleeper/aggtown/`, and `data/combined/aggtown/` merges both into
one 2015 to 2025 history (start there unless you need Yahoo only). See `data/README.md` for the
whole data folder.

This README is also the **file and field reference for every summary folder** (`data/yahoo/*`,
`data/sleeper/*`, `data/combined/*`); they all share the same files and definitions.

Everything here was pulled by `scripts/yahoo_scrape.py` from Yahoo's Fantasy v2 API
(through a logged-in browser session, since Yahoo no longer serves unapproved apps).

## Start here

| Question | File |
|---|---|
| Who won each season? | `league_history.csv` |
| A manager's record in a given season | `manager_season_records.csv` |
| All-time / career stats per manager | `manager_career_records.csv` |
| Every score of every week | `all_weekly_scores.csv` |
| Standings as they stood after week N | `weekly_standings.csv` |
| Weekly high/low scores, closest game, blowout | `weekly_highlights.csv` |
| One season in full (standings, bracket, settings) | `seasons/<year>/season.json` |
| One week in full | `seasons/<year>/weeks/week-NN.json` |
| Who drafted whom | `seasons/<year>/draft.json` |
| Lineups, player points, transactions, anything else | `raw/yahoo_api/<year>/` (XML) |

## Coverage and gaps

- **Seasons:** 2015 to 2022. 2015 had 10 teams; 2016 onward had 12.
- **Weeks:** 16 per season through 2020 (weeks 1 to 13 regular season, 14 to 16 playoffs);
  17 in 2021 and 2022 (weeks 1 to 14 regular season, 15 to 17 playoffs). The real value is
  `settings.playoff_week_start` in each `season.json`; don't hardcode it.
- **2014 and earlier:** not available. The 2015 league renews from a 2014 Yahoo league
  (`331.l.982878`), but this account wasn't in it and Yahoo refuses access.
- **2023:** a Yahoo league was created but no games or draft happened. It is in `raw/2023.json`
  and `managers.json`, but deliberately excluded from every built file.

## Managers and names

Yahoo exposes only a **nickname** and a permanent account id (**guid**) per manager, never real
names. Nicknames and team names change between seasons; the guid doesn't.

`managers.json` is the identity map, keyed by guid:

```json
"4O3C5BHIQCYX5O7EKHWFWKINKU": {
  "real_name": "",
  "nicknames": ["Ramzi"],
  "teams": {"2015": "Charizarkandrick", "2016": "Gordon Ramzi", "...": "..."}
}
```

- Every `manager` field in the built files is a display label: the latest nickname, or
  `"Nickname (Real Name)"` once `real_name` is filled in. Treat it as the join key across
  seasons; it's consistent across every built file.
- `real_name` is filled in by hand. After editing, run `build` (below) to relabel everything.
- One 2015 manager hid their Yahoo profile: nickname `--hidden--`, no guid. Their key is
  `unknown-2015-team10` (team "DuuuuuhhhhhHelloooo"), and they only appear in 2015.
- Team names contain emoji and curly quotes; files are UTF-8.

## How the results are defined

- **`final_rank`** is Yahoo's final standing **after the playoffs**: 1 = champion, 2 = runner-up,
  3 = third-place game winner, and so on down to last.
- **`playoff_seed`** is the seed entering the playoffs. It is empty for teams that missed them.
  Seed 1 is the `regular_season_winner`.
- **`championship_game`** is the champion's game in the final playoff week. It has been checked
  every season: the winner is always `final_rank` 1 and the loser `final_rank` 2.
- **Playoff vs consolation:** Yahoo flags each game `is_playoffs` and `is_consolation`. The
  championship bracket also contains placement games (3rd, 5th place), so a team eliminated
  early still plays more "playoff" games. `playoff_results` and `playoff_record` include those
  placement games; consolation-bracket games are counted separately.
- **`total_record`** = regular season + championship-bracket playoff games. Consolation games
  are excluded.
- **`weekly_standings`** covers regular-season weeks only, ranked by win % then points for
  (Yahoo's default tiebreak). The final regular-season week's ranks match Yahoo's official
  playoff seeds in every season.
- **Points for/against** in `standings` and the records files are **regular season only**
  (Yahoo's definition). Playoff scores are in the weekly files.
- `result` is `W`, `L` or `T`. Booleans in CSVs are the strings `True` / `False`.

## File reference

### `league_history.csv` / `.json`
One row per season: `season, league, champion, champion_team, championship_score
("109.18 - 78.16"), runner_up, third_place, regular_season_winner, most_points, last_place`.
The JSON version holds full team objects (team, manager, rank, record, points) for each slot,
plus the `championship_game` object.

### `manager_season_records.csv` (also `seasons/<year>/records.csv`)
One row per manager per season: `final_rank, playoff_seed, made_playoffs`, records as
strings (`regular_season_record`, `playoff_record`, `consolation_record`, `total_record`,
for example `"9-5"`, with a third number only when there are ties), the same counts as
integer columns (`total_wins`, `regular_losses`, ...), and regular-season `points_for` /
`points_against`.

### `manager_career_records.csv`
One row per manager: `seasons, championships, championship_seasons` (space-separated years),
`runner_ups, playoff_appearances, total_record, win_pct` (ties count as half a win),
`regular_season_record, playoff_record, points_for, points_against`. Sorted by
championships, then win %.

### `all_weekly_scores.csv`
One row per team per game (so every game appears twice, once from each side):
`season, week, is_playoffs, is_consolation, manager, team, points, opponent_manager,
opponent_team, opponent_points, result`.

### `weekly_standings.csv` (also per season)
`season, week, rank, manager, team, record, points_for, points_against, streak` (e.g. `W3`),
plus that week's `week_points, week_result, opponent`. All values are "after this week".

### `weekly_highlights.csv` (also per season)
`season, week, is_playoffs, high_score_manager, high_score, low_score_manager, low_score,
closest_game, biggest_blowout`. The last two are text like `"Don over Ramzi by 0.44"`.
The structured form is in each week file's `highlights`.

### `seasons/<year>/season.json`
```
season, league, finished
champion, runner_up, third_place, last_place, regular_season_winner, most_points
    -> {team_id, team, manager, final_rank, playoff_seed, wins, losses, ties, points_for, points_against}
championship_game
    -> {week, winner, winner_team, winner_points, loser, loser_team, loser_points}
settings
    -> {league_key, num_teams, start_week, end_week, playoff_week_start, num_playoff_teams,
        scoring_type, draft_type, roster_positions: [{position, count}]}
standings        -> [team objects as above, sorted by final_rank]
playoff_results  -> [{week, is_playoffs, is_consolation, teams: [...], winner}]  (championship bracket only)
```

### `seasons/<year>/weeks/week-NN.json`
```
season, week, is_playoffs
matchups: [{is_playoffs, is_consolation, winner,
            teams: [{team_id, team, manager, points, projected, won}, {...}]}]
highlights: {high_score, low_score, closest_game, biggest_blowout}
standings_after_week: [...]   regular-season weeks only; same fields as weekly_standings.csv
```

### `seasons/<year>/draft.json`
`[{team_id, team, manager, round, pick, cost, player, position, nfl_team}]`, in pick order.
`cost` is only set for auction drafts (null otherwise).

### `seasons/<year>/standings.csv`
Yahoo's final standings: `team_id, team, manager, final_rank, playoff_seed, wins, losses,
ties, points_for, points_against`.

## Raw data

### `raw/<year>.json`
The fields `fetch` extracted from Yahoo, and the only input to `build`. Teams are referenced
by Yahoo `team_id`; weekly rows use `roster_id` (the same team_id, named to mirror Sleeper's
matchup shape).

### `raw/yahoo_api/<year>/`: complete Yahoo responses
Saved byte-for-byte as Yahoo returned them, so nothing has to be re-downloaded (1,933 files,
about 100 MB; every lineup, transaction page and season-stat batch is present for 2015 to 2022). Contains
fields the built files don't use (logos, move/trade counts, injury tags, every stat line).

```
league.xml, settings.xml, standings.xml, teams.xml, draftresults.xml
game.xml, stat_categories.xml        stat_id -> stat name for this season's NFL game
scoreboard/week-NN.xml               every matchup that week
rosters/week-NN/team-NN.xml          that team's lineup that week, with each player's points and stats
transactions/page-NNN.xml            25 per page, newest first (page-001 = end of season)
player_season_stats/batch-NNN.xml    season stat lines for every player rostered or drafted that year
```

Reading the XML:

- Every element is in the namespace `http://fantasysports.yahooapis.com/fantasy/v2/base.rng`.
  Strip it first (`el.tag = el.tag.split("}", 1)[-1]` in Python's ElementTree) or every
  lookup fails silently.
- Keys: league `348.l.597497` (game id `348` = the 2015 NFL game), team `<league>.t.<id>`,
  player `<game>.p.<id>`. Player ids are stable across seasons; the game prefix changes yearly.
- **Lineups** (`rosters/.../team-NN.xml`): `fantasy_content/team/roster/players/player`. Per
  player: `name/full`, `display_position`, `editorial_team_abbr`,
  `selected_position/position` (the slot used that week; `BN` = bench, `IR` = injured
  reserve, anything else started), `player_points/total` (fantasy points that week) and
  `player_stats/stats/stat` (`stat_id` + `value`, names in `stat_categories.xml`).
  The starters' `player_points` add up exactly to the team's score in the scoreboard.
- **Transactions**: each `transaction` has `type` (`add`, `drop`, `add/drop`, `trade`,
  `commish`), `status`, `timestamp` (Unix seconds), and for player moves
  `players/player/transaction_data` with `type`, `source_type`, `destination_type` and the
  source/destination team key and name. `commish` entries are commissioner actions and carry
  no players.
- Scoreboard matchups: `status` is `postevent` for completed games; `winner_team_key`,
  `is_playoffs`, `is_consolation`, and per team `team_points/total` and
  `team_projected_points/total`.

## Regenerating

From the repo root (needs `uv`; first time, `login` opens a browser to sign in to Yahoo):

```
uv run --python 3.12 scripts/yahoo_scrape.py build aggtown     # rebuild every non-raw file from raw/, offline
uv run --python 3.12 scripts/yahoo_scrape.py fetch aggtown     # re-download raw/<year>.json, then build
uv run --python 3.12 scripts/yahoo_scrape.py archive aggtown   # (re)fill raw/yahoo_api/, resumes, skips files it has
```

The summaries are written by `scripts/league_build.py`, shared with the Sleeper exporter.
After changing anything here, also run `python3 scripts/sleeper_export.py combine aggtown` so the
combined history picks it up.

Everything outside `raw/` is generated: edit `managers.json` (only `real_name`) or the
scripts, never the generated files by hand.
