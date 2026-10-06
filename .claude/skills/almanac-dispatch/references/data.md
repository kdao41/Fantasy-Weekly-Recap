# Data and definitions

## Sources

| What | Where | Read by |
|---|---|---|
| This season: league settings, rosters, weekly matchups with every player's points, transactions, draft picks, NFL state | Sleeper public API (`/league/<id>/…`, `/state/nfl`), ids in `data/leagues.json` | `fetch_live.py` saves it, `calc.js` reads it |
| Player names, positions, injury tags (as of the fetch) | Sleeper `/players/nfl` | `calc.js`, through the lib's `nameOf` / `positionOf` / `injuryOf` |
| Every past game, season finish, champion | `data/combined/<league>/all_weekly_scores.csv`, `manager_season_records.csv`, `league_history.csv` | `calc.js` (head-to-head) and `facts.py` (precedent, careers) |
| Who is who across Yahoo and Sleeper | `data/combined/<league>/managers.json` | the lib's `h2hRawFrom` in `calc.js`; `facts.py` builds the same alias map for history |

The current season is never saved in `data/` (see `data/README.md`), so it always comes from the fetch.
History labels can carry a real name ("wabaki (Lan Doan)"); the PDF shows the Sleeper handle.

## Definitions: `lib/almanac-core.js`

The lib is the definition; this table only says which function to read. Change a definition there, with a
test in `tests/almanac-core.test.js`, and the site and the next PDF both follow.

| Number | Function | In short |
|---|---|---|
| Record, PF, PA, all-play, scores, game log | `compute` | All-play: a win against every team you outscored that week |
| Luck | `luckWins` | Actual wins minus all-play % × games. "lucky" / "robbed" at a full win either way |
| Power order, movement | `byPower`, `powerMoves` | All-play %, then points; movement against the same board a week earlier |
| Standings order | `byRec` | Win %, then points |
| Ratings, win chance | `strengthThrough`, `CONF` | Blend of points per game and all-play; weekly score SD 27 |
| Matchup of the week | `matchupPairs`, `spotlight` | Highest combined all-play, minus the gap between the two |
| Next week's picks, the model's record | `upcomingPicks`, `pickRecord` | |
| Playoff, 1-seed, title odds | `playoffOdds` (`simulate`, `rng`) | 4,000 seeded simulations of the real remaining schedule |
| Coach ratings | `coachRows`, `rateCoaches`, `bestLineup` | Sleeper's own best-lineup points when present; efficiency = scored / best |
| Head-to-head, series line, rivalry chips | `h2h`, `seriesLine`, `rivalryChips`, `rivalsOf` | All meetings, playoffs included, consolation excluded |
| Season MVP, top performances, draft points | `seasonMvps`, `topPerformances`, `playerPoints` | Points while on a roster; top performances are started games of 30+ |
| Trades, adds, FAAB | `rosterMoves` | Completed transactions only |
| Injured | `INJURED` | Out, IR, Doubtful, PUP, Sus, NA; Questionable is not injured |

PDF-only analysis lives in `facts.py`: started points per roster, lineup calls that cost a game (a loss where a
benched player outscored an eligible starter by more than the margin, opponent's lineup unchanged), draft steals
(round 6 on) and busts (rounds 1 to 3), and the historical precedent (same start after the same week, careers,
all-time score ranks).

## Caveats

- Points are scored to the hundredth; write them that way.
- Aggtown passing TDs were 5 points through 2021, 4 after; playoffs went from 8 teams to 6 in 2022; the
  league was 10 teams in 2015. Compare old scores loosely.
- Aggtown has `--hidden--` (a 2015 Yahoo manager who hid their profile) and `bAnmly (Bryan)` (2024 only)
  in its history; neither is in the current league.
- Sober Gang's 2019 to 2023 seasons were played on Yahoo as "Nooblets".
- Chrome and Node can differ in the last bit of a floating-point result (a win chance of
  0.6692836162207201 vs …202). It never shows at display precision.

## League notes

- **Aggtown** (12 teams, 6 make the playoffs, history 2015 on). Stakes for last place in 2026: panhandle in
  public with an "I SUCK AT FANTASY FOOTBALL" sign until you've honestly earned $50, or one full day at a bar,
  open to close. The section is "The punishment standings" and whoever is last is "holding the sign".
- **Sober Gang** (10 teams, 6 make the playoffs, history 2019 on). No known last-place stakes: the section
  is "The cellar". Ask the user if they want stakes added.
