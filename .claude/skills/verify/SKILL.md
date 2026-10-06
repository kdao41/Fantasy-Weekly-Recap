---
name: verify
description: How to run and drive index.html (the Almanac) / history.html locally to check a change in a real browser.
---

# Verifying the pages

The pages are static HTML. index.html (the Almanac) pulls live data from Sleeper's public API; its History tab
and history.html read `data/` with fetch, so they need a server (opening from disk fails).

1. Serve the repo root: `python3 -m http.server 8765` (run in the background).
2. Drive it with Playwright through uv (Chromium is already installed for scripts/yahoo_scrape.py):
   `uv run -q --python 3.12 --with playwright python <script.py>`
3. Open `http://localhost:8765/index.html?lg=<sleeper id>#<tab>`. League ids are in `data/leagues.json`
   (Aggtown 1389331035040260096, Sober Gang 1389735540009500672) plus Sea Squad 1377490959020855296
   (the only league with the Shotgun tab).

Gotchas:
- Only the open tab is visible; wait with `state="attached"` for content in other tabs.
- `locator.screenshot()` scrolls the page, which can leave a stale hover tooltip in the capture.
- Collect `pageerror` and console errors; late async renders after a league switch are the usual source.

Flows worth driving: the "I am" picker (persists per league), tab hash plus arrow keys, Standings sort
toggle, Luck plot/bars toggle, clicking a scatter dot or any team name to open the team card (Esc and
backdrop close it), Scores heatmap hover, rapid league switching, a bogus `?lg=` id, 390px mobile width.
