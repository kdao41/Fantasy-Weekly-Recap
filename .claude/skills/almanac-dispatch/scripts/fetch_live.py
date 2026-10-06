"""Download the live Sleeper season for the leagues in data/leagues.json.
usage: python3 -I fetch_live.py <repo_dir> <out_dir> [league ...]   (default: every league in leagues.json)
Writes <out_dir>/<league>/{league,users,rosters,drafts,picks,traded_picks,state}.json, m<week>.json and
t<week>.json for weeks 1 to 18, plus <out_dir>/players.json (Sleeper's player directory, about 15 MB, for names,
positions and today's injury designations). state.json is Sleeper's NFL state, which decides which weeks are final."""
import json, os, sys, urllib.request

REPO, OUT = sys.argv[1], sys.argv[2]
API = "https://api.sleeper.app/v1"
get = lambda path: json.load(urllib.request.urlopen(f"{API}/{path}", timeout=60))
def save(path, obj):
    with open(path, "w") as f: json.dump(obj, f)

leagues = json.load(open(f"{REPO}/data/leagues.json"))["leagues"]
want = set(sys.argv[3:]) or {l["id"] for l in leagues}
state = get("state/nfl")
os.makedirs(OUT, exist_ok=True)
for l in leagues:
    if l["id"] not in want: continue
    d = f"{OUT}/{l['id']}"; os.makedirs(d, exist_ok=True); lid = l["sleeper_league_id"]
    save(f"{d}/state.json", state)
    for name in ("league", "users", "rosters", "drafts", "traded_picks"):
        save(f"{d}/{name}.json", get(f"league/{lid}" + ("" if name == "league" else f"/{name}")))
    drafts = json.load(open(f"{d}/drafts.json"))
    save(f"{d}/picks.json", get(f"draft/{drafts[0]['draft_id']}/picks") if drafts else [])
    for w in range(1, 19):
        save(f"{d}/m{w}.json", get(f"league/{lid}/matchups/{w}"))
        save(f"{d}/t{w}.json", get(f"league/{lid}/transactions/{w}"))
    print(f"{l['id']}: saved to {d}")
save(f"{OUT}/players.json", get("players/nfl"))
# `week` is the upcoming week during the season; every week before it is final once Monday night is done
print(json.dumps({k: state.get(k) for k in ("season", "season_type", "week", "display_week")}))
