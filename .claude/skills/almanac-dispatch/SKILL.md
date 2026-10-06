---
name: almanac-dispatch
description: Write and render the weekly PDF Almanac dispatch ("The Aggtown Almanac", "The Sober Gang Almanac") for a league's current Sleeper season, joined to the full Yahoo + Sleeper history in data/. Use when asked for a week's almanac, dispatch, recap PDF, or to redo or extend one.
---

# The weekly Almanac dispatch

A dispatch is an editorial PDF, one per league per week, written in the voice of the legacy issues: a lede,
the standings and luck map, a precedent feature, power rankings, the matchup of the week, hardware, coach
ratings, the cellar, rivalries, odds, odds and ends. Numbers come from scripts; prose is written by you
from those numbers. Output goes to `almanac/<league>/<season>/week-NN.pdf` (week zero-padded, as in `data/`),
and the copy file that produced it to `almanac/<league>/<season>/src/week-NN.py`, so the issue can be fixed and
re-rendered.

The week is the upcoming one: after Weeks 1 to 4 are final, the issue is the Week 5 dispatch, `week-05.pdf`.

## Where the numbers come from

`lib/almanac-core.js` is the single source of truth for every calculation the site shows. index.html loads
it with `<script src>`; `scripts/calc.js` loads the same file in Node. So the PDF always shows the site's
numbers, and a change to a calculation is made once, in the lib, with a test in `tests/` (`npm test`).
Never re-implement one of those calculations in Python. `facts.py` only adds what the site doesn't have:
started points per roster, lineup calls that cost games, draft steals and busts by round, and history.

## Steps

Work in the session scratchpad (`$S` below); only the PDF and its copy file go in the repo.
`$K` is this skill's directory, `$R` the repo root. Run Python with `-I`.

1. **Fetch.** `python3 -I $K/scripts/fetch_live.py $R $S/live [aggtown sobergang]`
   Saves the league files plus Sleeper's NFL state. Completed weeks are the ones before `week`. If the last
   of them still has zero points, Monday night isn't over: ask before writing.
2. **Calculate.** `node $K/scripts/calc.js $R $S/live <league> > $S/<league>.site.json`
3. **Facts.** `python3 -I $K/scripts/facts.py $S/live $R <league> $S/<league>.site.json > $S/<league>.json`
4. **Read the digest, not the JSON.** `python3 -I $K/scripts/digest.py $S/<league>.json` prints about
   120 bounded lines: every team's line, history comps, careers, rivalries, hardware with all-time ranks,
   next week's matchups (the matchup of the week is flagged, the same pick the site makes), lineup calls that
   cost games, draft, moves. Pull a single field from the JSON with a one-off `python3 -c` only when the
   digest doesn't carry it.
5. **Find the stories.** See `references/voice.md`. Lead with the history angle the live site can't give:
   how teams with this start have finished, records being chased, rivalries the full archive changes. Check
   the previous issue (`almanac/<league>/<season>/src/`) for claims the data now contradicts, and correct them out loud.
6. **Write the copy file.** Start from the most recent `almanac/<league>/<season>/src/week-*.py`, or from
   `references/examples/` for a league's first issue. Every key is described in `references/sections.md`.
   The Matchup of the Week section covers the digest's flagged game.
7. **Render.** `python3 -I $K/scripts/build.py $S/<league>.json <copy.py> <out.pdf>` writes the PDF and an
   HTML file beside it, through headless Chrome (it can hang after writing; the script handles that).
8. **Look at it.** `pdftoppm -r 45 -png <out.pdf> $S/pg` and read every page image: headings stranded at a
   page bottom, overlapping luck-map labels, any number in the prose that disagrees with a table.
9. **Verify claims.** Every number, rank, streak and "first/never/most" claim must trace to the digest.
   Points are written to two decimals, as Sleeper scores them (161.62, not 161.6), from the exact value.
   `grep -c "—"` on the copy file must be 0 (no em dashes, see voice.md).
10. Copy the PDF to `almanac/<league>/<season>/week-NN.pdf` and the copy file to `almanac/<league>/<season>/src/week-NN.py`.

**Done** when the PDFs asked for are in `almanac/<league>/<season>/`, every page has been looked at, and every claim
traces to the digest. Don't commit unless asked.

## When to stop and ask

- The week isn't final, or a league's Sleeper id in `data/leagues.json` no longer points at this season.
- A manager has no history label (they show under their Sleeper name with no career): a new manager, or a
  missing `people` entry in `data/leagues.json`. Ask which.
- League stakes or traditions you don't know (the Aggtown punishment is in `references/data.md`; Sober Gang's
  is unknown, so its cellar section has none). Never invent stakes.
- A number you need isn't in the digest and would take new logic: if the site should show it too, it belongs
  in `lib/almanac-core.js` with a test; ask before adding it.

## References

- `references/voice.md`: tone, structure of a good paragraph, phrases from the legacy issues, hard rules.
- `references/sections.md`: every section, what drives it, and the copy-file keys.
- `references/data.md`: where each number comes from (which lib function), history caveats, per-league
  notes and stakes.
- `references/examples/`: the Week 5 2026 copy files for both leagues, the first issues with full history.
