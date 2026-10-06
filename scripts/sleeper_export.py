#!/usr/bin/env python3
"""Archive Sleeper league history and combine it with the league's Yahoo years.

Leagues come from data/leagues.json. Sleeper's API is public, so no login.

Usage:
  python3 scripts/sleeper_export.py fetch [LEAGUE]     # archive + normalize every finished Sleeper season
  python3 scripts/sleeper_export.py rebuild [LEAGUE]   # re-normalize the archived seasons, no download
  python3 scripts/sleeper_export.py combine [LEAGUE]   # Yahoo seasons + Sleeper seasons -> one history
  python3 scripts/sleeper_export.py all                # fetch and combine every league in leagues.json

LEAGUE is an id from leagues.json (aggtown, sobergang); omit it to run every league.

Output:
  data/sleeper/players_nfl.json            Sleeper's player directory (weekly data only has player ids)
  data/sleeper/<league>/
    raw/sleeper_api/<season>/              every response exactly as Sleeper sent it (JSON)
      league, users, rosters, winners_bracket, losers_bracket, drafts, traded_picks .json
      draft-<draft id>-picks.json
      matchups/week-NN.json                each team's score, starters and every player's points
      transactions/week-NN.json
    raw/<season>.json                      normalized season, same shape as the Yahoo raw files
    ...                                    Sleeper-only history (same files as data/yahoo/<league>/)
  data/combined/<league>/                  Yahoo + Sleeper history, same files again

Only finished seasons are archived; the season in progress is what the Almanac shows live.
"""
import json
import sys
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from league_build import build_dir  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
API = "https://api.sleeper.app/v1"


def config():
    return json.loads((DATA / "leagues.json").read_text())["leagues"]


def get(path, dest=None):
    """GET an API path. With `dest`, the body is saved verbatim and reused on later runs."""
    if dest and dest.exists() and dest.stat().st_size:
        return json.loads(dest.read_bytes())
    for attempt in range(4):
        try:
            with urllib.request.urlopen(f"{API}/{path}", timeout=60) as r:
                body = r.read()
            break
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < 3:
                time.sleep(10 * (attempt + 1))
                continue
            raise RuntimeError(f"{path} -> HTTP {e.code}")
    if dest:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(body)
    time.sleep(0.1)
    return json.loads(body)


# ---------------- fetch ----------------

def season_chain(league_id):
    out = []
    while league_id and league_id != "0":
        lg = get(f"league/{league_id}")
        if not lg:
            break
        out.append(lg)
        league_id = lg.get("previous_league_id")
    return sorted(out, key=lambda lg: int(lg["season"]))


def archive_season(lg, d):
    lid = lg["league_id"]
    get(f"league/{lid}", d / "league.json")
    for name in ("users", "rosters", "winners_bracket", "losers_bracket", "drafts", "traded_picks"):
        get(f"league/{lid}/{name}", d / f"{name}.json")
    for dr in json.loads((d / "drafts.json").read_text()):
        get(f"draft/{dr['draft_id']}/picks", d / f"draft-{dr['draft_id']}-picks.json")
    for w in range(1, last_week(lg, d) + 1):
        get(f"league/{lid}/matchups/{w}", d / "matchups" / f"week-{w:02d}.json")
        get(f"league/{lid}/transactions/{w}", d / "transactions" / f"week-{w:02d}.json")


def last_week(lg, d):
    rounds = max((m["r"] for m in json.loads((d / "winners_bracket.json").read_text()) or []), default=0)
    if lg["settings"].get("playoff_round_type", 0) != 0:
        sys.exit(f"{lg['season']}: multi-week playoff rounds aren't supported yet.")
    return lg["settings"]["playoff_week_start"] + rounds - 1


def fetch(league):
    out = DATA / "sleeper" / league["id"]
    players = DATA / "sleeper" / "players_nfl.json"
    if not players.exists():
        print("Downloading Sleeper's player directory (once)...")
        get("players/nfl", players)
    for lg in season_chain(league["sleeper_league_id"]):
        if lg["status"] != "complete":
            print(f"{lg['season']}  {lg['name']}: {lg['status']}, skipped (the Almanac shows it live)")
            continue
        d = out / "raw" / "sleeper_api" / lg["season"]
        print(f"{lg['season']}  {lg['name']} ({lg['league_id']})...", end=" ", flush=True)
        archive_season(lg, d)
        data = normalize(d, json.loads(players.read_text()))
        (out / "raw" / f"{lg['season']}.json").write_text(json.dumps(data, indent=1))
        print(f"{len(data['weeks'])} weeks, {len(data['draft'])} picks")
    seasons = [json.loads(p.read_text()) for p in sorted((out / "raw").glob("*.json"))]
    build_dir(out, seasons)


def rebuild(league):
    out = DATA / "sleeper" / league["id"]
    players = json.loads((DATA / "sleeper" / "players_nfl.json").read_text())
    for d in sorted((out / "raw" / "sleeper_api").iterdir()):
        data = normalize(d, players)
        (out / "raw" / f"{d.name}.json").write_text(json.dumps(data, indent=1))
        print(f"{d.name}  re-normalized")
    seasons = [json.loads(p.read_text()) for p in sorted((out / "raw").glob("*.json"))]
    build_dir(out, seasons)


# ---------------- normalize ----------------

def advances_loser(bracket, d, pws):
    """True when the bracket's "w" teams scored less than their opponents, i.e. losers move on."""
    lower = higher = 0
    for m in bracket:
        f = d / "matchups" / f"week-{pws + m['r'] - 1:02d}.json"
        if not m.get("w") or not f.exists():
            continue
        pts = {x["roster_id"]: x["points"] for x in json.loads(f.read_text())}
        w, l = pts.get(m["w"]), pts.get(m["l"])
        if w is not None and l is not None:
            lower += w < l
            higher += w > l
    return lower > higher


def normalize(d, players):
    """One archived Sleeper season -> the raw/<season>.json shape league_build expects."""
    read = lambda name: json.loads((d / name).read_text())
    lg, users, rosters = read("league.json"), read("users.json"), read("rosters.json")
    wb, lb = read("winners_bracket.json") or [], read("losers_bracket.json") or []
    st = lg["settings"]
    pws, n_playoff, n = st["playoff_week_start"], st["playoff_teams"], len(rosters)
    user = {u["user_id"]: u for u in users}

    teams = {}
    for r in rosters:
        s, u = r["settings"], user.get(r["owner_id"]) or {}
        teams[r["roster_id"]] = {
            "team_id": r["roster_id"],
            "team_key": f"{lg['league_id']}.{r['roster_id']}",
            "name": (u.get("metadata") or {}).get("team_name") or u.get("display_name") or f"Team {r['roster_id']}",
            "manager": u.get("display_name"),
            "manager_guid": f"sleeper:{r['owner_id']}" if r["owner_id"] else None,
            "wins": s.get("wins", 0), "losses": s.get("losses", 0), "ties": s.get("ties", 0),
            "points_for": round(s.get("fpts", 0) + s.get("fpts_decimal", 0) / 100, 2),
            "points_against": round(s.get("fpts_against", 0) + s.get("fpts_against_decimal", 0) / 100, 2),
        }

    # Seeds: regular-season order by win %, then points for (Sleeper's default tiebreak).
    order = sorted(teams.values(), key=lambda t: (-(t["wins"] + t["ties"] / 2) / max(1, t["wins"] + t["losses"] + t["ties"]),
                                                  -t["points_for"]))
    for i, t in enumerate(order, start=1):
        t["playoff_seed"] = i if i <= n_playoff else None
    bracket_teams = {x for m in wb for x in (m.get("t1"), m.get("t2")) if isinstance(x, int)}
    if bracket_teams and bracket_teams != {t["team_id"] for t in order[:n_playoff]}:
        print(f"\n  warning {lg['season']}: computed playoff seeds don't match Sleeper's bracket")

    # Final rank: placement games in the winners bracket decide 1st to Nth, the losers bracket the rest.
    rank = {}
    for m in wb:
        if m.get("p") and m.get("w"):
            rank[m["w"]], rank[m["l"]] = m["p"], m["p"] + 1
    # Sleeper records the team that advanced as "w". A consolation bracket advances game winners (its p=1
    # "w" finishes just below the playoff teams); a toilet bowl advances game losers (its p=1 "w" finishes last).
    # Both look the same in the bracket, so compare the scores.
    toilet = advances_loser(lb, d, pws)
    for m in lb:
        if m.get("p") and m.get("w"):
            if toilet:
                rank[m["w"]], rank[m["l"]] = n - m["p"] + 1, n - m["p"]
            else:
                rank[m["w"]], rank[m["l"]] = n_playoff + m["p"], n_playoff + m["p"] + 1
    free = [r for r in range(1, n + 1) if r not in rank.values()]
    for t in order:  # anyone the brackets didn't place, in regular-season order
        if t["team_id"] not in rank:
            rank[t["team_id"]] = free.pop(0)
    for tid, t in teams.items():
        t["rank"] = rank[tid]

    end = last_week(lg, d)
    pair_round = {}
    for bracket, consolation in ((wb, False), (lb, True)):
        for m in bracket:
            if isinstance(m.get("t1"), int) and isinstance(m.get("t2"), int):
                pair_round[(pws + m["r"] - 1, frozenset((m["t1"], m["t2"])))] = consolation
    weeks, week_info = {}, {}
    for w in range(1, end + 1):
        games = {}
        for x in json.loads((d / "matchups" / f"week-{w:02d}.json").read_text()):
            if x.get("matchup_id") is not None:
                games.setdefault(x["matchup_id"], []).append(x)
        rows = []
        for mid, g in games.items():
            if len(g) != 2 or not any(x["points"] for x in g):
                continue
            playoffs = w >= pws
            # Playoff-week games outside both brackets are exhibition games; count them as consolation.
            consolation = playoffs and pair_round.get((w, frozenset(x["roster_id"] for x in g)), True)
            a, b = g
            for x, o in ((a, b), (b, a)):
                rows.append({"roster_id": x["roster_id"], "matchup_id": mid, "points": x["points"], "projected": None,
                             "is_playoffs": playoffs, "is_consolation": consolation, "won": x["points"] > o["points"]})
        if rows:
            weeks[str(w)] = rows
            week_info[str(w)] = {"is_playoffs": w >= pws}

    draft, draft_type = [], None
    for dr in json.loads((d / "drafts.json").read_text()):
        draft_type = draft_type or dr.get("type")
        for p in json.loads((d / f"draft-{dr['draft_id']}-picks.json").read_text()):
            md = p.get("metadata") or {}
            pl = players.get(p["player_id"], {})
            draft.append({
                "round": p["round"], "pick": p["pick_no"], "team_id": p["roster_id"],
                "cost": int(md["amount"]) if md.get("amount") else None,
                "player_key": f"sleeper.p.{p['player_id']}",
                "player": f"{md.get('first_name', '')} {md.get('last_name', '')}".strip() or pl.get("full_name"),
                "position": md.get("position") or pl.get("position"),
                "nfl_team": md.get("team") or pl.get("team"),
            })

    slots = Counter(lg["roster_positions"])
    return {
        "source": "sleeper", "league_key": lg["league_id"], "name": lg["name"], "season": int(lg["season"]),
        "num_teams": n, "start_week": st.get("start_week", 1), "end_week": end, "is_finished": lg["status"] == "complete",
        "scoring_type": "head", "draft_type": draft_type, "playoff_week_start": pws, "num_playoff_teams": n_playoff,
        "roster_positions": [{"position": p, "count": c} for p, c in slots.items()],
        "teams": sorted(teams.values(), key=lambda t: t["rank"]), "weeks": weeks, "week_info": week_info, "draft": draft,
    }


# ---------------- combine ----------------

def combine(league):
    ydir, sdir = DATA / "yahoo" / league["yahoo_folder"], DATA / "sleeper" / league["id"]
    out = DATA / "combined" / league["id"]
    ymgr = json.loads((ydir / "managers.json").read_text())
    by_nick = {}
    for guid, m in ymgr.items():
        for nick in m["nicknames"]:
            by_nick.setdefault(nick, guid)
    yahoo = [json.loads(p.read_text()) for p in sorted((ydir / "raw").glob("*.json"))]
    sleeper = [json.loads(p.read_text()) for p in sorted((sdir / "raw").glob("*.json"))]
    if not sleeper:
        sys.exit(f"No Sleeper seasons in {sdir / 'raw'}; run `fetch` first.")
    # A season on both platforms (an unplayed auto-renewed Yahoo league) belongs to Sleeper.
    sleeper_years = {s["season"] for s in sleeper}
    yahoo = [s for s in yahoo if s["weeks"] and s["is_finished"] and s["season"] not in sleeper_years]

    unlinked = set()
    for s in sleeper:
        for t in s["teams"]:
            nick = league["people"].get(t["manager"])
            if nick and nick in by_nick:
                t["manager_guid"] = by_nick[nick]
            else:
                unlinked.add(t["manager"])
    if unlinked:
        print(f"  not linked to a Yahoo manager (new to the league, or missing from leagues.json): {', '.join(sorted(unlinked))}")

    # Real names typed into the Yahoo managers.json carry over; the combined file can add more.
    out.mkdir(parents=True, exist_ok=True)
    mpath = out / "managers.json"
    merged = json.loads(mpath.read_text()) if mpath.exists() else {}
    for guid, m in ymgr.items():
        if m.get("real_name") and not merged.get(guid, {}).get("real_name"):
            merged.setdefault(guid, {"real_name": "", "nicknames": [], "teams": {}})["real_name"] = m["real_name"]
    mpath.write_text(json.dumps(merged, indent=1, sort_keys=True))

    print(f"{league['name']}: {len(yahoo)} Yahoo + {len(sleeper)} Sleeper seasons")
    build_dir(out, sorted(yahoo + sleeper, key=lambda s: s["season"]))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else ""
    want = sys.argv[2] if len(sys.argv) > 2 else None
    leagues = [l for l in config() if want in (None, l["id"])]
    if want and not leagues:
        sys.exit(f"No league '{want}' in data/leagues.json.")
    if cmd not in ("fetch", "rebuild", "combine", "all"):
        sys.exit(__doc__)
    for l in leagues:
        print(f"== {l['name']}")
        if cmd in ("fetch", "all"):
            fetch(l)
        if cmd == "rebuild":
            rebuild(l)
        if cmd in ("combine", "all"):
            combine(l)
