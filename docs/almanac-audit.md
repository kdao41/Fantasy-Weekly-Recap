# League Almanac calculation audit

Audit of every calculation in `lib/almanac-core.js` (plus the two that live elsewhere: the bold calls in
`index.html` and the history comparisons in the dispatch's `facts.py`), backtested against every saved season.
**Status:** findings 1 to 7 (Proposal B) run as the canary model, `AlmanacCore.canary`, behind the 🐤 switch
in the page header; the live model is unchanged until it's promoted. Finding 8 is fixed in the PDF.

## Bottom line

1. **The win probabilities are overconfident, and that is the main problem.** Over 1,255 past games the
   picks are right 53.1% of the time while claiming 60 to 85%. The Brier score (0.2585) is worse than saying
   50% for every game (0.2500). Fantasy matchups are close to coin flips: true differences between teams are
   4 to 9 points a week, while one team's score swings about 23 points from week to week. Four weeks of
   points per game says far less about a team than the model assumes.
2. **The fix is one shared rating, shrunk toward the league average by games played, with the measured
   weekly spread.** Used by the picks and the simulation alike, it is calibrated (when it says 57%, the
   favorite wins 57%), scores best of everything tested (Brier 0.2469), and improves Week 4 playoff, title
   and 1-seed odds. **Who gets picked doesn't change, only how sure the model is:** this week's "lock" goes
   from 74% to 55%.
3. **The simulated playoff bracket is the wrong shape.** Both Sleeper leagues use a fixed bracket; the
   simulation reseeds. It's a correctness fix (title odds move by at most 0.4 points today).
4. **The "bold calls" on the Picks tab are worse than a coin flip** (43.3% over 365 calls). They also
   live in `index.html`, outside the lib and its tests.
5. **The PDF's "teams that started 2-2 made the playoffs X of Y times" mixes the 8-team and 6-team
   playoff eras**, which overstates today's odds (Aggtown 2-2 starts: 23 of 30 with 8 spots, 7 of 15 with 6).

Everything else checked out or is a minor, optional change (list at the end).

## How it was tested

- **Data:** `data/combined/<league>/all_weekly_scores.csv`. All 11 Aggtown seasons (2015-2025) and all 7
  Sober Gang seasons (2019-2025): 18 league-seasons, 1,255 regular-season games from Week 2 on.
- **Replay:** each season is rebuilt into the same `CUR` shape `index.html` builds, and the lib functions are
  called unchanged. Picks for week *w* only see weeks before *w*. Odds are simulated as of Weeks 4, 8 and 11
  with the real remaining schedule, the real playoff spots and 4,000 runs, then compared with what happened.
  A parameterised copy of `simulate` reproduces the lib's output exactly before any variant is tested.
- **No peeking:** fitted constants were chosen leave-one-season-out (fit on 17 seasons, score the 18th,
  repeat 18 times), so no season is scored by a model that saw it.
- **Scores:** Brier score (mean squared error of the stated probability, lower is better; always saying 50%
  scores 0.2500), log loss, accuracy, and reliability tables (stated chance vs how often it happened).

### Eras

Every season used the same starting lineup (QB, 2 RB, 2 WR, TE, one flex, K, DEF; Aggtown 2015's flex
excluded TEs) and full PPR. What differs:

| Era | Seasons | Teams | Playoff teams | Pass TD | League avg | Weekly SD within a team | True-skill spread | Game margin SD |
|---|---|---|---|---|---|---|---|---|
| Aggtown 2015-2021 (Yahoo) | 7 | 10 in 2015, then 12 | 8 | 5 pts | 121.10 | 23.57 | 8.86 | 35.51 |
| Aggtown 2022-2025 | 4 | 12 | 6 | 4 pts | 116.74 | 23.05 | 5.06 | 33.52 |
| Sober Gang 2019-2025 | 7 | 10 | 6 | 4 pts | 121.77 | 22.86 | 4.17 | 32.82 |
| *Model assumes* | | | | | | *27.00* | | *38.18* |

"True-skill spread" is the standard deviation of teams' real season averages once week-to-week noise is
removed. Two consequences:

- Ratings are always measured against that season's league average, so the scoring level (5-point TDs,
  Yahoo's interceptions at 2 points) never makes one era's teams look stronger.
- The skill spread does differ by era, so I tested fitting separate constants per era. **Per-era constants
  did worse on held-out seasons in all three eras** (Aggtown 2015-2021: 0.2486 vs 0.2479 pooled; Aggtown
  2022-2025: 0.2510 vs 0.2489; Sober Gang: 0.2460 vs 0.2456). With 4 to 7 seasons per era the fitted value
  swings between 10 and 40 depending on which season is held out. One pooled set is the robust choice.

## Findings

### 1. Game picks are overconfident (leads 1, 2, 5)

**Where:** `strengthThrough` (lib:122-127) builds `0.62 × PPG + 0.38 × (league avg + (all-play% − 0.5) × 55)`
from the raw season so far; `CONF` (lib:134) turns the gap into a probability with SD 27.00 per team. Nothing
pulls an early-season rating toward the average.

**Evidence, all 1,255 games:**

| Model (held-out) | Accuracy | Brier | Log loss |
|---|---|---|---|
| Current | 53.1% | 0.2585 | 0.7151 |
| Current with the simulation's 18% shrink | 53.1% | 0.2541 | 0.7034 |
| Always 50% | | 0.2500 | 0.6931 |
| Current gap × 0.3 (one fitted scale) | 53.1% | 0.2481 | 0.6894 |
| Last season's PPG as a prior, plus shrinkage | 53.9% | 0.2479 | 0.6889 |
| PPG shrunk by games played | 53.5% | 0.2474 | 0.6880 |
| Blend shrunk by games played | 53.1% | 0.2473 | 0.6878 |
| All-play shrunk by games played | 53.5% | 0.2473 | 0.6877 |
| **Proposal A:** blend, 14-game prior, SD 23.30 | 53.1% | **0.2469** | 0.6869 |
| **Proposal B:** all-play, 14-game prior, SD 23.30 | 53.5% | **0.2469** | 0.6870 |

The current model is overconfident at every level:

| Current says | 52.5% | 57.6% | 62.4% | 67.2% | 72.1% | 77.3% | 84.7% |
|---|---|---|---|---|---|---|---|
| Favorite actually won | 47.5% | 53.2% | 54.3% | 52.9% | 58.6% | 62.1% | 58.8% |
| Games | 335 | 295 | 210 | 170 | 111 | 66 | 68 |

Proposal A is calibrated:

| Proposal says | 51.4% | 54.4% | 57.5% | 62.2% |
|---|---|---|---|---|
| Favorite actually won | 48.5% | 55.6% | 56.9% | 66.7% |
| Games | 588 | 394 | 204 | 69 |

The overconfidence is worst early: Weeks 2-5 Brier 0.2744 now, 0.2485 proposed. Late in the season
(Week 9 on) it is 0.2461 now, 0.2447 proposed.

**What the constants mean:**

- **Prior weight of 14 games.** A team's observed edge over the league average is multiplied by
  games / (games + 14): 22% of it counts after Week 4, 36% after Week 8, 48% after Week 13. That's the
  ratio of weekly noise to true-skill spread in the table above. Every held-out fold chose 10 to 20, mostly
  14 to 16.
- **Weekly SD 23.30** per team (game margin SD 32.95), measured, and stable across eras.
- **Proposal B's scale**, 58.40 points per unit of all-play (23.30 × √(2π)), is what normal score spreads
  imply: a team d points better than average beats about Φ(d / 23.30) of the league. The current 55 is close
  to this, so it wasn't arbitrary.
- **The 0.62 / 0.38 blend weights don't matter.** Pure PPG, pure all-play and the blend all land within
  0.0003 of each other once shrunk. They carry the same information.
- **No prior from last season.** A team's PPG relative to the league correlates 0.03 with its previous
  season (172 team-season pairs). Adding it didn't help.

**Proposal (pick one):**

- **A (smallest change):** keep the blend, shrink it: `rating = avg + (blend − avg) × g / (g + 14)`.
- **B (recommended):** `rating = avg + 58.40 × (all-play% − 0.5) × g / (g + 14)`. Same accuracy, fewer
  constants, and the picks always agree with the power board (finding 6).

Either way `CONF` becomes `Φ(gap / (23.30 × √2))`.

**What changes for readers:** the same teams are favored, with less certainty. In Week 5 every favorite
stays the same, and the top confidence drops from about 74% to 55%. The "Lock of the week" label will
read oddly at 55% (copy question for you). The PDF's per-team `rating` (facts.py:65) gets compressed
toward the league average early in the season.

### 2. The posted win chance and the simulation's win chance disagree (lead 3)

**Where:** `CONF` uses the raw rating gap with SD 27.00. `simulate` (lib:64-65) first shrinks the same
ratings 18% toward the mean and then also uses SD 27.00. So the 74% on the Picks tab is not the chance the
odds simulation itself uses for that game.

**Proposal:** `simulate` takes its ratings from the same function as the picks (finding 1) and uses the same
SD, and the separate 0.82 line goes away. One number per game everywhere on the page and in the PDF.

**Effect on odds, all 18 seasons (Brier, lower is better):**

| As of | Playoff odds, now → A | Title odds | 1-seed odds |
|---|---|---|---|
| Week 4 | 0.1673 → 0.1634 | 0.0816 → 0.0789 | 0.0897 → 0.0797 |
| Week 8 | 0.1214 → 0.1226 | 0.0754 → 0.0752 | 0.0590 → 0.0558 |
| Week 11 | 0.0688 → 0.0689 | 0.0726 → 0.0735 | 0.0320 → 0.0317 |
| *Equal odds for everyone* | *0.2320* | *0.0818* | *0.0818* |

- At Week 4 the current 1-seed odds score worse than giving every team an equal chance. The current model
  gave 30%+ title odds 9 times, and only 1 of those 9 teams won. When it said 90%+ to make the playoffs at
  Week 4 (51 teams, average stated 97%), 90% did.
- By Weeks 8 and 11 the record dominates, and both versions are the same within noise. Proposal B scores
  the same as A (Week 4: 0.1645, 0.0787, 0.0789).
- I also tested drawing each team's true strength fresh in every simulated season (adds rating uncertainty).
  It was a wash, so I left it out.

### 3. Weekly SD is a fixed 27.00 for every league and era (lead 4)

Measured within-team SD is 23.57, 23.05 and 22.86 across the three eras, and no single season exceeds
26.40. Changing only the SD to 23.30 **without** shrinkage makes things slightly worse (Week 4 playoff
Brier 0.1691), because the oversized SD was partly offsetting the missing shrinkage. So this goes in only
together with finding 1. One constant for all leagues is fine: the spread barely varies with era, league
size or scoring.

### 4. The simulated bracket reseeds; the real ones are fixed (lead 6)

**Where:** `simulate` (lib:87-97) re-sorts survivors by seed each round, so the 1 seed always meets the
lowest seed left.

**Evidence:** real round-two pairings against both shapes, in every season where they differ:

| Seasons | Real bracket |
|---|---|
| Aggtown 2023, 2024, 2025 and Sober Gang 2025 (Sleeper, `playoff_seed_type` 0) | Fixed: 1 seed plays the 4/5 winner, 2 seed plays the 3/6 winner |
| Aggtown 2015-2019 (Yahoo, 8 teams) | Fixed |
| Nooblets 2021 and 2023 (Yahoo) | Reseeded |

Both current leagues are Sleeper with `playoff_seed_type` 0.

**Proposal:** play a fixed bracket in standard slot order (1-8-4-5-2-7-3-6 for 6 or 8 teams, byes as empty
slots). Reseed only if `playoff_seed_type` is 1. I believe 1 means reseeding, but no league on file uses it,
so I can't confirm.

**Effect:** no measurable accuracy change in the backtest. Today's title odds move by at most 0.4 points.

**Not a bug:** the `active.length/2` loop can't see an odd field. Byes = next power of two − spots, so the
first round is always even and every later round is a power of two. Checked for 3 to 12 spots: every
simulated season crowns exactly one champion. The seeding tiebreak (wins, then points for) reproduces the
real seeds in all 18 seasons.

### 5. The bold calls are worse than a coin flip (new, `index.html:579-614`)

`boldReplay` / `boldUpcoming` call the luckiest team (luck ≥ +1 win) to lose next week and the unluckiest
(≤ −1) to win.

- Over all 18 seasons, "lucky team loses" hit 77 of 181 (42.5%) and "robbed team wins" hit 81 of 184
  (44.0%). Combined that's 43.3%, about 2.6 standard errors below 50%.
- Past luck doesn't make next week's result go the other way. Those teams' all-play was average (0.500 and
  0.522), so next week is close to a coin flip on its own.
- The logic is also in the page rather than the lib, with no tests, which breaks the single-source rule.

**Proposal:** drop the predictive "takes an L / bounces back with a W" calls and their graded record. Keep
luck as a descriptive stat (the luck chart already does this). If you want a second pick feature, it should
come from the same rating, in the lib.

### 6. The power board and the picks use different strength orders (lead 7)

`byPower` (lib:319) ranks by all-play %, then points for. The picks use the blend rating.

- They disagree on 5.0% of team pairs at Weeks 4 and 8 (103 of 2,040).
- On next week's games, the higher team on the power board is not the pick's favorite 12 times in 200.
- Proposal B removes this completely: shrinking by games played keeps the all-play order, so the board
  and the picks always agree. Under Proposal A, I'd leave it and accept the occasional mismatch.

### 7. Matchup of the week (lead 9)

`spotlight` (lib:339) scores `(A + B all-play) × 2 − |A − B|`. Over 226 past weeks, compared with that
week's average game:

| | Spotlight game | Average game |
|---|---|---|
| Both teams made the playoffs | 62% | 35% |
| Final margin | 25.16 | 27.04 |
| Combined points | 248.96 | 240.68 |
| Playoff leverage (how much the result moved both teams' playoff odds) | 0.27 | 0.34 |

- It does what it says: good teams, slightly closer games.
- It favors games whose playoff stakes are lower than average, because top teams are already safe.
- It repeats itself: the same team was featured in 5 to 9 of a season's 13 or 14 weeks (9 in Sober Gang
  2021 and 2025).

**Options (editorial, your call):** (a) keep it; (b) add playoff leverage to the score, which the simulation
can produce with little extra work; (c) skip teams featured the week before when another game scores
nearly as well. I'd do (c) at minimum.

### 8. "Teams that started like this" mixes playoff formats (new, PDF only, `facts.py:161-191`)

The precedent line compares this season's start with every saved season, including Aggtown's 8-team-playoff
years:

| Aggtown start through Week 4 | 8 playoff spots | 6 playoff spots |
|---|---|---|
| 1-3 | 8 of 22 made it | 3 of 11 |
| 2-2 | 23 of 30 | 7 of 15 |
| 3-1 | 21 of 22 | 10 of 13 |

**Proposal:** compare only seasons with the same playoff spots and team count, and always print the sample
size. This also argues for moving the calculation into the lib (finding 10).

## Checked and fine (no change proposed)

- **Lineups and coach ratings (lead 8).**
  - Sleeper's "best possible points" match a rebuild from `players_points` exactly for all 22 rosters in
    2026. The greedy `bestLineup` is correct for these leagues' single FLEX, and `coachRows` never needs the
    fallback because Sleeper always sends `ppts`.
  - Two latent issues only matter if a league adds a second flex type or loses `ppts`. With FLEX plus
    SUPER_FLEX, filling the wider slot first can miss the best lineup, so narrower flexes should fill first.
    `positionOf` takes the first listed position, so Travis Hunter (DB/WR) shows as DB and would be
    ineligible at WR in the fallback.
  - Whether Sleeper counts IR players in `ppts` can't be checked from the API: matchups don't record which
    players were on IR that week.
- **Rivalry thresholds (lead 10).** The smallest sample behind any current nemesis or punching-bag label is
  8 games, and smoothing the win rates changes none of the 44 labels.
- **The 30-point top-performance cutoff and leaving Questionable out of the injury list** are editorial
  choices with no data problem.
- **Consolation games** are excluded consistently in the lib, the saved standings and `facts.py`.

## Smaller items

- **Moving PDF-only facts into the lib (lead 11).** The history precedent, lineup calls that cost a game, and
  draft steals/busts are untested Python. I'd move "starts like these" into the lib with tests as part of
  finding 8. The other two only if you want them on the site.
- **The win chance on the scoreboard** is computed inline at `index.html:959-978`. It uses the lib's
  `strengthThrough` and `CONF`, so it follows any change automatically, but it duplicates `matchupPairs`.
- **The footer's "4,000-season simulation"** stays accurate under every proposal.

## What it does to 2026 right now (Proposal B, live data through Week 4)

Pick record so far, current → B. Aggtown: 7 of 18, Brier 0.324 → 0.259. Sober Gang: 11 of 15,
Brier 0.208 → 0.240. Same picks, so the same record. Sober Gang scores worse this year because the
overconfident picks happened to hit. 15 games is noise next to the 1,255-game backtest.

**Week 5 picks** (same favorites; current → B):

| Aggtown | | Sober Gang | |
|---|---|---|---|
| bvincenttt over kholabear | 74.1% → 55.0% | keveezy over Abadahh | 74.0% → 55.2% |
| jimbo817 over keveezy | 71.7% → 56.0% | lmphm over yckyb | 71.7% → 53.9% |
| oooEcho over PutItOnYa | 69.6% → 54.6% | donblood over anth0nyng | 66.9% → 53.5% |
| DVTV over donblood | 59.6% → 53.2% | jasonle over PutItOnYa | 64.5% → 53.9% |
| wabaki over lmphm | 59.0% → 52.5% | jigri over dexclusive | 63.1% → 52.6% |
| anth0nyng over Odeh1121 | 56.5% → 52.1% | | |

**Aggtown odds** (current → B, includes the fixed bracket):

| Team | Record | PPG | Playoffs | 1 seed | Title |
|---|---|---|---|---|---|
| DVTV | 3-1 | 134.07 | 92.1 → 82.7 | 30.8 → 22.5 | 24.5 → 19.4 |
| lmphm | 4-0 | 127.52 | 91.7 → 87.6 | 32.1 → 30.6 | 16.4 → 16.5 |
| oooEcho | 3-1 | 123.13 | 70.2 → 71.9 | 9.8 → 14.4 | 9.7 → 11.5 |
| jimbo817 | 2-2 | 126.52 | 66.1 → 59.4 | 7.1 → 7.2 | 10.1 → 9.5 |
| bvincenttt | 2-2 | 127.90 | 62.5 → 54.1 | 5.3 → 5.6 | 8.7 → 8.3 |
| wabaki | 1-3 | 136.13 | 61.6 → 43.0 | 5.4 → 3.4 | 13.9 → 7.6 |
| donblood | 2-2 | 126.03 | 57.3 → 52.5 | 4.8 → 5.4 | 7.9 → 8.1 |
| anth0nyng | 2-2 | 121.41 | 52.4 → 53.6 | 3.5 → 5.9 | 5.7 → 8.7 |
| Odeh1121 | 2-2 | 115.95 | 32.3 → 42.7 | 1.2 → 3.2 | 2.5 → 5.3 |
| PutItOnYa | 2-2 | 101.54 | 10.3 → 31.9 | 0.1 → 1.7 | 0.4 → 2.9 |
| kholabear | 1-3 | 98.77 | 2.3 → 14.3 | 0.0 → 0.3 | 0.1 → 1.8 |
| keveezy | 0-4 | 104.18 | 1.1 → 6.4 | 0.0 → 0.1 | 0.1 → 0.5 |

**Sober Gang odds** (current → B):

| Team | Record | PPG | Playoffs | 1 seed | Title |
|---|---|---|---|---|---|
| donblood | 3-1 | 141.68 | 96.3 → 87.1 | 31.6 → 24.2 | 23.4 → 18.7 |
| jasonle | 2-2 | 147.94 | 94.3 → 78.2 | 27.4 → 15.2 | 30.3 → 16.2 |
| jigri | 3-1 | 133.57 | 91.3 → 82.9 | 14.5 → 17.6 | 12.8 → 14.7 |
| PutItOnYa | 3-1 | 133.40 | 88.3 → 82.3 | 13.0 → 17.3 | 12.0 → 13.5 |
| lmphm | 3-1 | 130.19 | 86.5 → 80.3 | 10.3 → 14.9 | 9.4 → 13.2 |
| keveezy | 1-3 | 133.25 | 62.0 → 46.4 | 2.1 → 2.7 | 7.8 → 6.7 |
| dexclusive | 2-2 | 118.63 | 38.4 → 52.9 | 0.7 → 3.8 | 2.6 → 6.3 |
| anth0nyng | 1-3 | 122.20 | 26.9 → 35.6 | 0.3 → 1.2 | 1.4 → 4.2 |
| Abadahh | 2-2 | 104.87 | 14.7 → 43.9 | 0.2 → 3.1 | 0.4 → 5.1 |
| yckyb | 0-4 | 103.22 | 1.4 → 10.4 | 0.0 → 0.1 | 0.1 → 1.4 |

The pattern: four games of points per game count for much less. High-scoring teams with poor records
(wabaki, jasonle, keveezy in Sober Gang) lose the most. Low scorers at 2-2 gain the most. Records
already banked still count in full.

## Decisions needed

| # | Change | Where | Recommendation |
|---|---|---|---|
| 1-3 | One shrunk rating for the picks and the simulation, SD 23.30. Proposal A (blend) or B (all-play) | lib `strengthThrough`, `CONF`, `simulate` | **Yes, B** |
| 4 | Fixed bracket, honoring `playoff_seed_type` | lib `simulate` | Yes |
| 5 | Drop the bold calls' predictions | `index.html` | Yes |
| 6 | Power board / picks agreement | (comes with B) | |
| 7 | Matchup of the week: keep / add leverage / avoid repeats | lib `spotlight` | Your call; at least avoid repeats |
| 8 | Same-format precedent in the PDF, moved into the lib | `facts.py` → lib | Yes |
| | "Lock of the week" wording at about 55% | `index.html` | Your call |
| | Narrow-first flex filling, all fantasy positions in `bestLineup` | lib | Optional, latent only |
