# /// script
# requires-python = ">=3.10"
# dependencies = ["playwright"]
# ///
"""Pull a Yahoo Fantasy Football league's full history using a logged-in browser session.

Yahoo stopped serving its Fantasy API to unapproved developer apps in 2026, but
its website reads the same v2 API from pub-api-ro.fantasysports.yahoo.com with
the browser's login cookies. This drives a dedicated Chromium profile (kept
outside the repo) through that endpoint, then reuses yahoo_export.py's parsers.

Usage:
  uv run scripts/yahoo_scrape.py check [NAME]         # is everything set up? each problem comes with its fix
  uv run scripts/yahoo_scrape.py login               # sign in once in the window, then close it
  uv run scripts/yahoo_scrape.py fetch [NAME]         # download every season (default NAME: aggtown)
  uv run scripts/yahoo_scrape.py fetch NAME --until 2023   # stop at a season, e.g. when the league moved
                                                        # platforms but Yahoo kept auto-renewing it
  uv run scripts/yahoo_scrape.py fetch NAME --add 314.l.829747   # include a season Yahoo doesn't link to the
                                                        # rest (the league was recreated under a new name)
  uv run scripts/yahoo_scrape.py leagues              # every league-season in the account, with its key
  uv run scripts/yahoo_scrape.py build [NAME]         # rebuild organized files from the download
  uv run scripts/yahoo_scrape.py archive [NAME]       # save Yahoo's complete responses, incl. lineups

`fetch` runs `build` at the end. After filling in real names in managers.json,
run `build` again; it does not touch Yahoo.

Output (data/yahoo/<league>/):
  managers.json            one entry per Yahoo account; fill in "real_name"
  league_history.json/csv  champion, runner-up, regular-season winner per season
  all_weekly_scores.csv    every team score of every week, one row per team
  weekly_standings.csv     everyone's record, rank, points and streak after every regular-season week
  weekly_highlights.csv    each week's high score, low score, closest game, biggest blowout
  manager_season_records.csv  each manager's regular-season, playoff and total record per season
  manager_career_records.csv  all-time totals: titles, playoff trips, records, points
  raw/<season>.json        the fields pulled from Yahoo, the source for `build`
  raw/yahoo_api/<season>/  `archive`: every API response exactly as Yahoo sent it (XML)
    league, settings, standings, teams, draftresults, game, stat_categories .xml
    scoreboard/week-NN.xml
    rosters/week-NN/team-NN.xml        that week's lineup with each player's points and stats
    transactions/page-NNN.xml          every add, drop and trade
    player_season_stats/batch-NNN.xml  season stats for every player rostered that year
  seasons/<season>/
    season.json            settings, final standings, playoff bracket results
    standings.csv
    records.csv            that season's manager records
    draft.json
    weekly_standings.csv, weekly_highlights.csv   that season's slice of the above
    weeks/week-NN.json     that week's matchups, scores, highlights, standings after the week
"""
import json
import re
import sys
import time
import xml.etree.ElementTree as ET
from contextlib import closing
from pathlib import Path

from playwright.sync_api import Error as PlaywrightError, sync_playwright

sys.path.insert(0, str(Path(__file__).resolve().parent))
from yahoo_export import export_league, list_leagues  # noqa: E402
from league_build import build_dir  # noqa: E402

PROFILE_DIR = Path.home() / ".yahoo-fantasy-browser"
HOME_URL = "https://football.fantasysports.yahoo.com/"
PUB_API = "https://pub-api-ro.fantasysports.yahoo.com/fantasy/v2"
DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "yahoo"


def open_browser(p, headless=True):
    return p.chromium.launch_persistent_context(str(PROFILE_DIR), headless=headless,
                                                viewport={"width": 1400, "height": 1000})


class BrowserClient:
    """Same interface as yahoo_export.Client, authenticated by the browser's cookies."""

    def __init__(self, ctx):
        self.ctx = ctx

    def get(self, path):
        for attempt in range(4):
            r = self.ctx.request.get(f"{PUB_API}/{path}", timeout=60000)
            if r.status in (429, 999) and attempt < 3:
                time.sleep(30 * (attempt + 1))
                continue
            if r.status != 200:
                raise RuntimeError(f"{path} -> HTTP {r.status}: {r.text()[:300]}")
            break
        root = ET.fromstring(r.body())
        for el in root.iter():
            el.tag = el.tag.split("}", 1)[-1]
        time.sleep(0.4)
        return root


def login():
    with sync_playwright() as p, closing(open_browser(p, headless=False)) as ctx:
        page = ctx.pages[0] if ctx.pages else ctx.new_page()
        page.goto(HOME_URL)
        print("Sign in to Yahoo in the window that opened, then close the window.")
        page.wait_for_event("close", timeout=0)
    print(f"Saved session to {PROFILE_DIR}")


def leagues():
    """Every league-season the signed-in account can read, to find a key for `fetch --add`."""
    with sync_playwright() as p, closing(open_browser(p)) as ctx:
        for l in list_leagues(BrowserClient(ctx)):
            print(f"{l['season']}  {l['league_key']:<16} {l['num_teams'] or '?':>2} teams  {l['name']}")


def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")


def league_chain(leagues, name, added=()):
    """Every season of the league matching `name` or listed in `added`, following Yahoo's
    season-to-season links so a renamed season is still included."""
    by_ref = {l["league_key"].replace(".l.", "_"): l for l in leagues}
    chain = {l["league_key"]: l for l in leagues if name.lower() in (l["name"] or "").lower() or l["league_key"] in added}
    frontier = list(chain.values())
    while frontier:
        l = frontier.pop()
        for ref in (l.get("renew"), l.get("renewed")):
            nxt = by_ref.get(ref or "")
            if nxt and nxt["league_key"] not in chain:
                chain[nxt["league_key"]] = nxt
                frontier.append(nxt)
    return sorted(chain.values(), key=lambda l: l["season"])


def load_config(out):
    path = out / "fetch_config.json"
    return json.loads(path.read_text()) if path.exists() else {}


def fetch(name, until=None, add=()):
    out = DATA_DIR / slugify(name)
    (out / "raw").mkdir(parents=True, exist_ok=True)
    # The cutoff and added seasons are remembered, so later fetches pull the same league.
    config = load_config(out)
    if until is not None:
        config["until"] = until
    if add:
        config["add"] = sorted(set(config.get("add", [])) | set(add))
    if until is not None or add:
        (out / "fetch_config.json").write_text(json.dumps(config, indent=1))
    until = config.get("until")
    with sync_playwright() as p, closing(open_browser(p)) as ctx:
        c = BrowserClient(ctx)
        try:
            leagues = league_chain(list_leagues(c), name, config.get("add", ()))
        except RuntimeError as e:
            sys.exit(f"Couldn't list leagues ({e}). Run `login` again if the session expired.")
        if until:
            skipped = [l["season"] for l in leagues if l["season"] > until]
            leagues = [l for l in leagues if l["season"] <= until]
            if skipped:
                print(f"Stopping at {until} (fetch_config.json); skipping {', '.join(map(str, skipped))}")
        if not leagues:
            sys.exit(f"No league matching '{name}' in this account.")
        for l in leagues:
            raw = out / "raw" / f"{l['season']}.json"
            # Finished seasons never change, so skip ones already downloaded.
            if raw.exists() and json.loads(raw.read_text()).get("is_finished"):
                print(f"{l['season']}  {l['name']}: already downloaded")
                continue
            print(f"{l['season']}  {l['name']} ({l['league_key']})...", end=" ", flush=True)
            try:
                data = export_league(c, l["league_key"])
            except RuntimeError as e:
                print(f"failed: {e}")
                continue
            raw.write_text(json.dumps(data, indent=1))
            print(f"{len(data['weeks'])} weeks, {len(data['draft'])} picks")
    build(name)


# ---------------- archive ----------------

class Archiver:
    def __init__(self, ctx):
        self.ctx, self.fetched, self.skipped = ctx, 0, 0

    def save(self, path, dest):
        """Store the response body verbatim. Existing files are kept, so a rerun resumes."""
        if dest.exists() and dest.stat().st_size:
            self.skipped += 1
            return dest.read_bytes()
        for attempt in range(6):
            r = self.ctx.request.get(f"{PUB_API}/{path}", timeout=60000)
            # Yahoo's 999 throttle lasts minutes, not seconds, so back off hard.
            if r.status in (429, 999) and attempt < 5:
                wait = 60 * 2 ** min(attempt, 3)
                print(f"  Yahoo is throttling (HTTP {r.status}); waiting {wait // 60} min", flush=True)
                time.sleep(wait)
                continue
            if r.status != 200:
                raise RuntimeError(f"{path} -> HTTP {r.status}: {r.text()[:200]}")
            break
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(r.body())
        self.fetched += 1
        time.sleep(0.3)
        return r.body()


def player_keys(xml_bytes):
    return re.findall(rb"<player_key>([^<]+)</player_key>", xml_bytes)


def archive(name):
    out = DATA_DIR / slugify(name)
    seasons = [json.loads(p.read_text()) for p in sorted((out / "raw").glob("*.json"))]
    if not seasons:
        sys.exit(f"Run `fetch` first; archive uses its season list from {out / 'raw'}.")
    with sync_playwright() as p, closing(open_browser(p)) as ctx:
        a = Archiver(ctx)
        for s in seasons:
            key, season = s["league_key"], s["season"]
            d = out / "raw" / "yahoo_api" / str(season)
            game = key.split(".")[0]
            print(f"{season} ({key})", flush=True)
            for fname, path in [("league", f"league/{key}"), ("settings", f"league/{key}/settings"),
                                ("standings", f"league/{key}/standings"), ("teams", f"league/{key}/teams"),
                                ("draftresults", f"league/{key}/draftresults"), ("game", f"game/{game}"),
                                ("stat_categories", f"game/{game}/stat_categories")]:
                a.save(path, d / f"{fname}.xml")

            start = 0
            while True:
                body = a.save(f"league/{key}/transactions;start={start};count=25",
                              d / "transactions" / f"page-{start // 25 + 1:03d}.xml")
                if body.count(b"<transaction>") < 25:
                    break
                start += 25

            rostered = set()
            weeks = sorted(int(w) for w in s["weeks"])
            team_ids = sorted(t["team_id"] for t in s["teams"])
            for w in weeks:
                a.save(f"league/{key}/scoreboard;week={w}", d / "scoreboard" / f"week-{w:02d}.xml")
                for tid in team_ids:
                    body = a.save(f"team/{key}.t.{tid}/roster;week={w}/players/stats;type=week;week={w}",
                                  d / "rosters" / f"week-{w:02d}" / f"team-{tid:02d}.xml")
                    rostered.update(player_keys(body))
                print(f"  week {w}: fetched {a.fetched}, already had {a.skipped}", flush=True)

            # Drafted players too, since some were cut before week 1.
            rostered.update(player_keys((d / "draftresults.xml").read_bytes()))
            keys = sorted(k.decode() for k in rostered)
            for i in range(0, len(keys), 25):
                a.save(f"league/{key}/players;player_keys={','.join(keys[i:i + 25])}/stats;type=season",
                       d / "player_season_stats" / f"batch-{i // 25 + 1:03d}.xml")
    print(f"\nDone: {a.fetched} downloaded, {a.skipped} already saved, in {out / 'raw' / 'yahoo_api'}")


# ---------------- organize ----------------

def build(name):
    out = DATA_DIR / slugify(name)
    seasons = [json.loads(p.read_text()) for p in sorted((out / "raw").glob("*.json"))]
    if not seasons:
        sys.exit(f"Nothing downloaded yet in {out / 'raw'}; run `fetch` first.")
    build_dir(out, seasons)


# ---------------- check ----------------

RUN = "uv run --python 3.12 scripts/yahoo_scrape.py"


def say(status, what, fix=None):
    print(f"{status:<4}  {what}" + (f"\n      fix: {fix}" if fix else ""))


def check_access(p):
    """The browser, the saved session and the account's leagues; later checks need all three."""
    if not Path(p.chromium.executable_path).exists():
        say("FAIL", "Chromium for Playwright isn't installed", "uv run --python 3.12 --with playwright playwright install chromium")
        sys.exit(1)
    say("ok", "Chromium for Playwright is installed")
    if not PROFILE_DIR.exists():
        say("FAIL", f"no Yahoo session saved in {PROFILE_DIR}", f"{RUN} login")
        sys.exit(1)
    try:
        ctx = open_browser(p)
    except PlaywrightError as e:
        say("FAIL", f"couldn't open the browser profile: {str(e).splitlines()[0]}",
            "another yahoo_scrape.py is probably running; wait for it, or close it")
        sys.exit(1)
    with closing(ctx):
        try:
            leagues = list_leagues(BrowserClient(ctx))
        except RuntimeError as e:
            say("FAIL", f"Yahoo refused the saved session ({str(e)[:80]})", f"{RUN} login")
            sys.exit(1)
    say("ok", f"signed in to Yahoo; the account has {len(leagues)} NFL league-seasons")
    return leagues


def check_league(leagues, name):
    """Which seasons `fetch` would pull for `name`, and which are already downloaded and archived."""
    out = DATA_DIR / slugify(name)
    config = load_config(out)
    chain = league_chain(leagues, name, config.get("add", ()))
    if not chain:
        say("FAIL", f"no league in this account matches '{name}'; its leagues: "
            + ", ".join(sorted({l["name"] for l in leagues})), "use part of one of those names")
        return False
    names = sorted({l["name"] for l in chain})
    say("ok", f"'{name}' matches {', '.join(names)}: {chain[0]['season']} to {chain[-1]['season']}")
    until = config.get("until")
    seasons = [l["season"] for l in chain if not until or l["season"] <= until]
    if until:
        say("note", f"fetch_config.json stops at {until}")
    raw = {s: json.loads((out / "raw" / f"{s}.json").read_text()) for s in seasons if (out / "raw" / f"{s}.json").exists()}
    todo = [s for s in seasons if not raw.get(s, {}).get("is_finished")]
    say("note", f"downloaded: {', '.join(map(str, sorted(raw))) or 'none'}"
        + (f"; `fetch {name}` would pull {', '.join(map(str, todo))}" if todo else ""))
    unarchived = [s for s in raw if not (out / "raw" / "yahoo_api" / str(s)).exists()]
    if unarchived:
        say("note", f"not archived yet: {', '.join(map(str, unarchived))} (`archive {name}`)")
    return True


def check_links(name):
    """That every Yahoo nickname in data/leagues.json exists, so the Sleeper stitch links everyone it lists."""
    folder = slugify(name)
    linked = [l for l in json.loads((DATA_DIR.parent / "leagues.json").read_text())["leagues"] if l.get("yahoo_folder") == folder]
    mgr_path = DATA_DIR / folder / "managers.json"
    if not linked:
        say("note", f"no league in data/leagues.json has yahoo_folder '{folder}' yet (README step 5)")
        return True
    if not mgr_path.exists():
        say("note", f"{mgr_path} doesn't exist until `fetch {name}` runs")
        return True
    managers = json.loads(mgr_path.read_text())
    nicks = {n for m in managers.values() for n in m["nicknames"]}
    ok = True
    for l in linked:
        missing = [g for p in l.get("same_person", []) for g in p["yahoo_accounts"] if g not in managers]
        if missing:
            ok = False
            say("FAIL", f"{l['id']}: same_person lists accounts that aren't in managers.json: {', '.join(missing)}",
                "copy the account ids (the keys) from managers.json")
        unknown = sorted(n for n in l["people"].values() if n not in nicks)
        if unknown:
            ok = False
            say("FAIL", f"{l['id']}: people lists Yahoo nicknames that aren't in managers.json: {', '.join(unknown)}",
                f"use one of: {', '.join(sorted(nicks))}")
        else:
            say("ok", f"{l['id']}: all {len(l['people'])} people match a Yahoo nickname")
        newest = {g: p["yahoo_accounts"][-1] for p in l.get("same_person", []) if "seasons" not in p for g in p["yahoo_accounts"]}
        for nick in sorted(set(l["people"].values())):
            accounts = [g for g, m in managers.items() if nick in m["nicknames"] and g not in newest]
            if len(accounts) > 1:
                say("note", f"{l['id']}: '{nick}' is on {len(accounts)} Yahoo accounts and the newest is linked; "
                    "if they're one person, list them under same_person in data/leagues.json")
        # an older account in a same_person entry is represented by the newest one
        yahoo_only = sorted({n for g, m in managers.items() if newest.get(g, g) == g for n in m["nicknames"]} - set(l["people"].values()))
        if yahoo_only:
            say("note", f"{l['id']}: Yahoo-only managers (fine if they never joined Sleeper): {', '.join(yahoo_only)}")
    return ok


def check(name):
    with sync_playwright() as p:
        leagues = check_access(p)
    found = check_league(leagues, name)
    linked = check_links(name)
    if not (found and linked):
        sys.exit(1)
    print("\nReady.")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(add_help=False)
    ap.add_argument("cmd", nargs="?", default="")
    ap.add_argument("league", nargs="?", default="aggtown")
    ap.add_argument("--until", type=int, help="last season to fetch")
    ap.add_argument("--add", action="append", default=[], metavar="LEAGUE_KEY", help="a season Yahoo doesn't link to the rest")
    args = ap.parse_args()
    cmd, league = args.cmd, args.league
    if cmd == "login":
        login()
    elif cmd == "fetch":
        fetch(league, args.until, args.add)
    elif cmd == "build":
        build(league)
    elif cmd == "archive":
        archive(league)
    elif cmd == "check":
        check(league)
    elif cmd == "leagues":
        leagues()
    else:
        print(__doc__)
