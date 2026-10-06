#!/usr/bin/env python3
"""Export historical Yahoo Fantasy Football leagues to JSON for the Almanac.

Finds every Yahoo NFL league the logged-in account belonged to (all seasons)
and writes one file per league-season to data/yahoo/, plus data/yahoo/index.json.

Each file's "weeks" uses the same shape as Sleeper's /matchups/{week}
(a list of {roster_id, matchup_id, points}) so the page can reuse its
existing compute code; roster_id is the Yahoo team_id.

Setup (once):
  1. Create an app at https://developer.yahoo.com/apps/create/
     - Redirect URI: https://localhost:8080
     - API Permissions: Fantasy Sports (Read)
  2. Store the app's keys in the macOS Keychain (each command prompts, nothing
     lands in shell history):
       security add-generic-password -s yahoo-fantasy -a client_id -w
       security add-generic-password -s yahoo-fantasy -a client_secret -w
     YAHOO_CLIENT_ID / YAHOO_CLIENT_SECRET env vars also work and take precedence.
  3. python3 scripts/yahoo_export.py
     The first run prints a login URL. After you approve, the browser lands on a
     localhost page that won't load; copy that page's full URL and paste it back.

Options:
  --list              only list your leagues, export nothing
  --name SUBSTRING    only export leagues whose name contains this (case-insensitive)
  --season YEAR       only export this season (repeatable)
  --code URL_OR_CODE  finish the first login non-interactively with the URL the
                      browser landed on (quote it: it contains '&')
"""
import argparse
import base64
import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

AUTH_URL = "https://api.login.yahoo.com/oauth2/request_auth"
TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"
# Must match the app's registered redirect URI exactly. Nothing needs to listen
# there: the code is read from the URL the browser is sent to.
REDIRECT_URI = os.environ.get("YAHOO_REDIRECT_URI", "https://localhost:8080")
API = "https://fantasysports.yahooapis.com/fantasy/v2"
# Kept outside the repo so the refresh token can't be committed by accident.
TOKEN_FILE = Path.home() / ".yahoo_fantasy_token.json"
KEYCHAIN_SERVICE = "yahoo-fantasy"
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "yahoo"


# ---------------- auth ----------------

def _keychain(account):
    try:
        r = subprocess.run(["security", "find-generic-password", "-s", KEYCHAIN_SERVICE, "-a", account, "-w"],
                           capture_output=True, text=True)
    except FileNotFoundError:
        return None
    return r.stdout.strip() or None if r.returncode == 0 else None


def _creds():
    cid = os.environ.get("YAHOO_CLIENT_ID") or _keychain("client_id")
    secret = os.environ.get("YAHOO_CLIENT_SECRET") or _keychain("client_secret")
    if not cid or not secret:
        sys.exit("No Yahoo app keys found in the Keychain or environment (see the top of this file).")
    return cid, secret


def _token_request(form):
    cid, secret = _creds()
    basic = base64.b64encode(f"{cid}:{secret}".encode()).decode()
    req = urllib.request.Request(
        TOKEN_URL,
        data=urllib.parse.urlencode(form).encode(),
        headers={"Authorization": f"Basic {basic}", "Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(req) as r:
            tok = json.load(r)
    except urllib.error.HTTPError as e:
        sys.exit(f"Yahoo token request failed ({e.code}): {e.read().decode(errors='replace')}")
    tok["expires_at"] = time.time() + int(tok.get("expires_in", 3600)) - 60
    TOKEN_FILE.write_text(json.dumps(tok))
    TOKEN_FILE.chmod(0o600)
    return tok


def _login(pasted=None):
    if not pasted:
        cid, _ = _creds()
        url = AUTH_URL + "?" + urllib.parse.urlencode(
            {"client_id": cid, "redirect_uri": REDIRECT_URI, "response_type": "code", "scope": "fspt-r"})
        print("Open this URL, sign in to Yahoo, and approve access:\n\n  " + url + "\n")
        try:
            pasted = input("Paste the URL your browser ended up on (or just the code): ")
        except EOFError:
            sys.exit("\nNo input available. Rerun with: --code '<the URL your browser landed on>'")
    pasted = pasted.strip()
    code = urllib.parse.parse_qs(urllib.parse.urlparse(pasted).query).get("code", [pasted])[0]
    return _token_request({"grant_type": "authorization_code", "redirect_uri": REDIRECT_URI, "code": code})


class Client:
    def __init__(self, code=None):
        self.tok = json.loads(TOKEN_FILE.read_text()) if TOKEN_FILE.exists() and not code else _login(code)

    def _access_token(self):
        if time.time() >= self.tok.get("expires_at", 0):
            self.tok = _token_request({
                "grant_type": "refresh_token",
                "redirect_uri": REDIRECT_URI,
                "refresh_token": self.tok["refresh_token"],
            })
        return self.tok["access_token"]

    def get(self, path):
        """GET an API path and return the parsed XML root with namespaces stripped."""
        for attempt in range(5):
            req = urllib.request.Request(f"{API}/{path}",
                                         headers={"Authorization": f"Bearer {self._access_token()}"})
            try:
                with urllib.request.urlopen(req) as r:
                    root = ET.fromstring(r.read())
                break
            except urllib.error.HTTPError as e:
                if e.code == 401 and attempt == 0:
                    self.tok["expires_at"] = 0
                    continue
                # Yahoo throttles with 999 (and sometimes 429); back off and retry.
                if e.code in (429, 999) and attempt < 4:
                    time.sleep(30 * (attempt + 1))
                    continue
                raise RuntimeError(f"{path} -> HTTP {e.code}: {e.read().decode(errors='replace')[:300]}")
        for el in root.iter():
            el.tag = el.tag.split("}", 1)[-1]
        time.sleep(0.3)
        return root


# ---------------- parsing helpers ----------------

def txt(el, path, default=None):
    found = el.find(path)
    return found.text if found is not None and found.text is not None else default


def num(el, path, default=0.0):
    v = txt(el, path)
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


def integer(el, path, default=None):
    v = txt(el, path)
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


# ---------------- export ----------------

def list_leagues(c):
    root = c.get("users;use_login=1/games;game_codes=nfl/leagues")
    out = []
    for game in root.iter("game"):
        for lg in game.iter("league"):
            out.append({
                "league_key": txt(lg, "league_key"),
                "name": txt(lg, "name"),
                "season": integer(lg, "season") or integer(game, "season"),
                "num_teams": integer(lg, "num_teams"),
                # "renew"/"renewed" link a league to its previous/next season, as "<game>_<league id>".
                "renew": txt(lg, "renew"),
                "renewed": txt(lg, "renewed"),
            })
    return sorted(out, key=lambda l: (l["season"] or 0, l["name"] or ""))


def export_league(c, key):
    settings_root = c.get(f"league/{key}/settings")
    lg = settings_root.find("league")
    s = lg.find("settings")
    meta = {
        "source": "yahoo",
        "league_key": key,
        "name": txt(lg, "name"),
        "season": integer(lg, "season"),
        "num_teams": integer(lg, "num_teams"),
        "start_week": integer(lg, "start_week", 1),
        "end_week": integer(lg, "end_week"),
        "is_finished": txt(lg, "is_finished") == "1",
        "scoring_type": txt(lg, "scoring_type"),
        "draft_type": txt(s, "draft_type"),
        "playoff_week_start": integer(s, "playoff_start_week"),
        "num_playoff_teams": integer(s, "num_playoff_teams"),
        "roster_positions": [
            {"position": txt(p, "position"), "count": integer(p, "count", 0)}
            for p in s.iter("roster_position")
        ],
    }

    teams = []
    for t in c.get(f"league/{key}/standings").iter("team"):
        mgr = t.find("managers/manager")
        ts = t.find("team_standings")
        teams.append({
            "team_id": integer(t, "team_id"),
            "team_key": txt(t, "team_key"),
            "name": txt(t, "name"),
            # Yahoo shows "--hidden--" for managers who left Yahoo or hid their profile.
            "manager": txt(mgr, "nickname") if mgr is not None else None,
            "manager_guid": txt(mgr, "guid") if mgr is not None else None,
            "rank": integer(ts, "rank"),
            "playoff_seed": integer(ts, "playoff_seed"),
            "wins": integer(ts, "outcome_totals/wins", 0),
            "losses": integer(ts, "outcome_totals/losses", 0),
            "ties": integer(ts, "outcome_totals/ties", 0),
            "points_for": num(ts, "points_for"),
            "points_against": num(ts, "points_against"),
        })

    weeks, week_info = {}, {}
    for w in range(meta["start_week"], (meta["end_week"] or 17) + 1):
        rows = []
        is_playoffs = False
        for mid, m in enumerate(c.get(f"league/{key}/scoreboard;week={w}").iter("matchup"), start=1):
            if txt(m, "status") != "postevent":
                continue
            is_playoffs = is_playoffs or txt(m, "is_playoffs") == "1"
            for t in m.iter("team"):
                rows.append({
                    "roster_id": integer(t, "team_id"),
                    "matchup_id": mid,
                    "points": num(t, "team_points/total"),
                    "projected": num(t, "team_projected_points/total", None),
                    "is_playoffs": txt(m, "is_playoffs") == "1",
                    "is_consolation": txt(m, "is_consolation") == "1",
                    "won": txt(m, "winner_team_key") == txt(t, "team_key"),
                })
        if not rows:
            break
        weeks[str(w)] = rows
        week_info[str(w)] = {"is_playoffs": is_playoffs}

    picks = []
    for d in c.get(f"league/{key}/draftresults").iter("draft_result"):
        if txt(d, "player_key") is None:
            continue
        team_key = txt(d, "team_key")
        picks.append({
            "round": integer(d, "round"),
            "pick": integer(d, "pick"),
            "cost": integer(d, "cost"),
            "team_id": int(team_key.rsplit(".t.", 1)[1]),
            "player_key": txt(d, "player_key"),
        })
    names = player_names(c, key, [p["player_key"] for p in picks])
    for p in picks:
        p.update(names.get(p["player_key"], {}))

    return {**meta, "teams": teams, "weeks": weeks, "week_info": week_info, "draft": picks}


def player_names(c, league_key, player_keys):
    out = {}
    keys = list(dict.fromkeys(player_keys))
    for i in range(0, len(keys), 25):  # Yahoo caps a players collection at 25 keys
        batch = ",".join(keys[i:i + 25])
        for p in c.get(f"league/{league_key}/players;player_keys={batch}").iter("player"):
            out[txt(p, "player_key")] = {
                "player": txt(p, "name/full"),
                "position": txt(p, "display_position"),
                "nfl_team": (txt(p, "editorial_team_abbr") or "").upper() or None,
            }
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--name")
    ap.add_argument("--season", type=int, action="append")
    ap.add_argument("--code")
    args = ap.parse_args()

    c = Client(args.code)
    leagues = list_leagues(c)
    if args.name:
        leagues = [l for l in leagues if args.name.lower() in (l["name"] or "").lower()]
    if args.season:
        leagues = [l for l in leagues if l["season"] in args.season]

    for l in leagues:
        print(f"{l['season']}  {l['league_key']:<20} {l['num_teams'] or '?':>2} teams  {l['name']}")
    if args.list or not leagues:
        if not leagues:
            print("No matching Yahoo NFL leagues found for this account.")
        return

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    index_path = OUT_DIR / "index.json"
    index = json.loads(index_path.read_text()) if index_path.exists() else []
    by_key = {e["league_key"]: e for e in index}

    for l in leagues:
        print(f"Exporting {l['season']} {l['name']}...", end=" ", flush=True)
        try:
            data = export_league(c, l["league_key"])
        except RuntimeError as e:
            print(f"failed: {e}")
            continue
        slug = re.sub(r"[^a-z0-9]+", "-", (data["name"] or "league").lower()).strip("-")
        fname = f"{data['season']}-{slug}.json"
        (OUT_DIR / fname).write_text(json.dumps(data, indent=1))
        by_key[l["league_key"]] = {"league_key": l["league_key"], "season": data["season"],
                                   "name": data["name"], "file": fname}
        print(f"{len(data['weeks'])} weeks, {len(data['draft'])} picks -> data/yahoo/{fname}")

    index_path.write_text(json.dumps(sorted(by_key.values(), key=lambda e: (e["season"], e["name"])), indent=1))


if __name__ == "__main__":
    main()
