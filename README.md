# Fantasy Weekly Recap

Static web pages for our fantasy football leagues: a live weekly almanac pulled from Sleeper,
plus each league's full history going back to its Yahoo years. No build step and no server code;
everything is plain HTML reading public APIs and the saved data in `data/`.

## Pages

| Page | What it is |
|---|---|
| `index.html` | **The League Almanac.** Live from Sleeper on every load: weekly dispatch, standings, luck map, a scores heatmap, power rankings, playoff odds, awards, matchups, picks, coach ratings, draft and moves, plus a **History** tab with every champion and career standings across Yahoo and Sleeper. Click any team for its card; pick your team in "I am…" to highlight it everywhere. |
| `history.html` | **Hall of Records.** One tab per season: champion, podium, awards, final standings and playoff bracket. League picker in the corner; `?league=aggtown` or `?league=sobergang`. |
| `almanac/issues.json` | Which PDF issues exist, written by the dispatch skill, so the Almanac's header can link each league's newest one. |
| `almanac/<league>/<year>/week-NN.pdf` | **The weekly PDF dispatch**, one per league per week, written from the same numbers as the Almanac plus the full history. Each issue's copy is in `src/` beside it; the `almanac-dispatch` Claude skill makes them. |
| `deprecated/almanac-original.html` | The Almanac before the redesign, kept for reference. |
| `deprecated/index.html` | An earlier Almanac version, kept for reference. |

Links into a specific league: `index.html?lg=<Sleeper league id>#<tab>`, `history.html?league=<id>#2019`.

### Leagues

| League | Sleeper id | History |
|---|---|---|
| Aggtown Fantasy League | `1389331035040260096` | 2015 to 2022 on Yahoo, 2023 on Sleeper |
| Sober Gang | `1389735540009500672` | 2019 to 2023 on Yahoo (as "Nooblets"), 2024 on Sleeper |
| Goodell Haters, 12 Guys 1 Cup, Sea Squad | see `PRESETS` in the Almanac | Sleeper live only |

## Running locally

The pages fetch files from `data/`, which browsers block for pages opened straight from disk.
Serve the folder instead:

```
python3 -m http.server        # then open http://localhost:8000/
```

In VS Code, the Live Server or Live Preview extension works too. On GitHub Pages everything works
as is.

## Calculations and tests

Every number the Almanac computes (records, all-play, luck, power, odds, the matchup of the week, coach
ratings, head-to-head, MVPs, moves) lives in `lib/almanac-core.js`. index.html loads it with a plain
`<script src>`, so it must be committed alongside index.html; there is still no build step. The PDF
dispatch runs the same file in Node, so the site and the PDF can't disagree. Change a calculation there,
not in index.html, and cover it in `tests/almanac-core.test.js`.

`AlmanacCore.canary` is the same code with the proposed settings (`MODELS.canary` at the top of the file).
The 🐤 Canary model switch in the page header, or `&model=canary` in the link, shows it, with a Canary vs live
tab comparing the two. To promote it, swap the settings in `MODELS.live`. `docs/almanac-audit.md` has the
backtest behind it.


```
npm install       # once: installs Vitest (dev only; GitHub Pages never sees node_modules)
npm test
```

## Weekly and yearly upkeep

- **Commissioner's Note:** edit the `COMMISSIONER_NOTE` text near the top of the Almanac's script
  and commit; it shows for everyone.
- **Add a league to the Almanac:** add `{name, id}` to `PRESETS`, or use the page's "add a league"
  box (saved only in that browser).
- **After a season ends:** `python3 scripts/sleeper_export.py all` saves the finished Sleeper
  season and rebuilds the combined histories. Commit `data/`.
- **Real names:** fill in `real_name` in `data/combined/<league>/managers.json`, then
  `python3 scripts/sleeper_export.py combine`. Names then show as "nickname (Real Name)".

## Data and scripts

`data/` holds every saved season, summarized and in raw form; start with
[data/README.md](data/README.md). The scripts:

| Script | Does | Needs |
|---|---|---|
| `scripts/sleeper_export.py` | Archives finished Sleeper seasons and builds the combined Yahoo + Sleeper history | Python 3, no login |
| `scripts/yahoo_scrape.py` | Pulls Yahoo seasons through a logged-in browser session (`login`, `fetch`, `archive`, `build`) | `uv`, a Yahoo login once |
| `scripts/league_build.py` | Shared builder: turns normalized seasons into the summary files | used by both above |
| `scripts/yahoo_export.py` | Yahoo's official OAuth API client. Yahoo blocks unapproved apps since 2026, so it only works if Yahoo approves our app; its parsers are reused by `yahoo_scrape.py` | Yahoo app keys in the macOS Keychain |

`data/leagues.json` ties each Sleeper league to its Yahoo past and links each person's Sleeper
account to their Yahoo nickname. Edit it when someone joins or a league is added.

## Notes

- Not affiliated with Sleeper, Yahoo or the NFL.
- Scoring rules changed over the years (for example, passing TDs went from 5 to 4 points in 2022),
  so all-time point totals compare loosely; records and titles compare cleanly.
