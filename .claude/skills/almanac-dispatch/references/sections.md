# Sections and the copy file

`build.py` renders tables, the luck map, the power-ranking order and the odds table from the facts JSON.
Everything else is a string in the copy file's `COPY` dict. Strings may contain inline HTML
(`<b>`, `<span class="inj">` for injuries, `<span class="good">` for a highlighted good number). A value
shown as "paras" can be a string or a list of strings (one `<p>` each).

| Order | Section | Generated from facts | Copy keys |
|---|---|---|---|
| 1 | Masthead | | `doc_title`, `kicker` ("WEEK 5 DISPATCH · FOUR WEEKS IN · …"), `title` (`<br>` before "Almanac"), `subtitle` |
| 2 | Lede | | `lede` (drop cap on the first letter) |
| 3 | The standings, and what history says | table: record, PF, PA (two decimals), all-play, luck word, same-start playoff rate | `standings_intro` (paras), `standings_cap`, `standings_after` (paras) |
| 4 | The luck map | SVG scatter, all-play % vs win %, tied teams share a dot | `luck_intro`, `luck_title`, `luck_after` (paras) |
| 5 | Precedent feature | | `feature_title`, `feature_intro` (paras), `cards`: list of `dict(cls, tag, big, hl, body)` with `cls` in `lucky` / `robbed` / `good` (border color), `feature_after` (paras) |
| 6 | Power rankings | order, number and movement arrows | `power`: `{handle: blurb}` for every team |
| 7 | Matchup of the week | | `motw_head`, `motw_body` (paras), `motw_series` (one line), `elsewhere` (paras, the other notable games) |
| 8 | The hardware | | `hardware`: list of `(LABEL, text)`; usual labels: HIGH SCORE OF THE SEASON, LOW SCORE, BIGGEST BLOWOUT, MOST POINTS IN A LOSS, CLOSEST GAME, DRAFT STEAL / BUST, TOP PERFORMANCE |
| 9 | Coach ratings | table sorted by efficiency, benched points | `coach_intro` (paras), `coach`: `{handle: short verdict}`, `coach_after` (paras, usually the lineup calls that cost games) |
| 10 | The cellar | | `cellar_title` ("The punishment standings" when the league has stakes, else "The cellar"), `cellar_intro` (paras), `cellar_items` (bullets) |
| 11 | Rivalry spotlight & milestone watch | | `rivalry_items` (bullets) |
| 12 | Playoff & title odds | table sorted by title odds | `odds_intro`, `odds_after` (paras) |
| 13 | Odds & ends | | `ends` (bullets), `closer` (boxed), `footer` (sources and caveats) |

The section order and headings live in `build.py`'s `body` template. Add or drop a section there, not by
leaving a key empty. Late-season issues can swap the precedent feature for a playoff-picture feature using
the same `cards` format.

The footer should always state: what came live from Sleeper and through which week, the injury date, the
history span (seasons, games, consolation excluded), the scoring-era caveat for Aggtown, and that odds are
from the live Almanac's 4,000 simulated rest-of-seasons (the same seeded run as the site).
