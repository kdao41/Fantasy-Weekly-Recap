"""Facts for one league's Week-N dispatch: the live season joined to the combined history.
usage: python3 -I facts.py <live_dir> <repo_dir> <league> <site.json>  -> JSON on stdout
<live_dir> comes from fetch_live.py, <site.json> from calc.js.

Everything the site shows (records, all-play, luck, power and movement, ratings, favorites, the matchup of
the week, playoff odds, coach ratings, head-to-head, MVPs, top performances, draft points, moves, which
injuries count, player names and positions) is read from <site.json>, computed by lib/almanac-core.js, and
never recomputed here. This script adds only what the site doesn't have: started points per roster, lineup
calls that cost games, draft steals and busts by round, and the historical precedent."""
import json, csv, sys, math, collections

LIVE, REPO, LG = sys.argv[1], sys.argv[2], sys.argv[3]
SITE = json.load(open(sys.argv[4]))
NW = len(SITE["completed"])
D = f"{LIVE}/{LG}"
J = lambda p: json.load(open(p))
lg, users, rosters = J(f"{D}/league.json"), J(f"{D}/users.json"), J(f"{D}/rosters.json")
SEASON = int(lg["season"])
tname = {u["user_id"]: (u.get("metadata") or {}).get("team_name") for u in users}
NAME = {t["rid"]: t["name"] for t in SITE["teams"]}
TEAM = {r["roster_id"]: tname.get(r["owner_id"]) for r in rosters}
RIDS = sorted(NAME)
WEEKS = {w: J(f"{D}/m{w}.json") for w in range(1, NW + 2)}
SLOTS = [s for s in lg["roster_positions"] if s not in ("BN", "IR", "TAXI")]
FLEX = SITE["flex"]
PL = SITE["players"]
def pname(pid): return PL[pid]["name"] if pid in PL else pid
def ppos(pid): return PL[pid]["pos"] if pid in PL else None
# fantasy points are scored to the hundredth
pts2 = lambda x: round(x, 2)

# ---------- history (combined) ----------
H = f"{REPO}/data/combined/{LG}"
mg = J(f"{H}/managers.json")
alias = {}
for m in mg.values():
    nk = m.get("nicknames") or []
    if not nk: continue
    lab = nk[-1] + (f" ({m['real_name']})" if m.get("real_name") else "")
    for n in nk: alias[n] = lab
    alias[lab] = lab
LAB = {r: alias.get(NAME[r], NAME[r]) for r in RIDS}
SHOW = {v: k for k, v in LAB.items()}  # history label -> this season's roster id
disp = lambda lab: NAME[SHOW[lab]] if lab in SHOW else lab
rows = [r for r in csv.DictReader(open(f"{H}/all_weekly_scores.csv")) if r["is_consolation"] != "True"]
seasons = list(csv.DictReader(open(f"{H}/manager_season_records.csv")))
lhist = list(csv.DictReader(open(f"{H}/league_history.csv")))

# ---------- this season, as index.html computed it ----------
BYNAME = {t["name"]: t for t in SITE["teams"]}
def pairs(w):
    bm = collections.defaultdict(list)
    for x in WEEKS[w]:
        if x.get("matchup_id") is not None: bm[x["matchup_id"]].append(x)
    return [v for v in bm.values() if len(v) == 2]
st = {r: BYNAME[NAME[r]] for r in RIDS}
log = {r: [dict(g, p=pts2(g["p"]), op=pts2(g["op"])) for g in st[r]["log"]] for r in RIDS}
games = [dict(g, wp=pts2(g["wp"]), lp=pts2(g["lp"]), margin=pts2(g["wp"] - g["lp"])) for g in SITE["games"]]
coach_site = {c["name"]: c for c in SITE["coach"]}
T = {}
for r in RIDS:
    s = st[r]
    T[r] = dict(name=NAME[r], team=TEAM[r], rec=f"{s['w']}-{s['l']}" + (f"-{s['t']}" if s["t"] else ""), w=s["w"], l=s["l"], t=s["t"],
                pf=pts2(s["pf"]), pa=pts2(s["pa"]), pfg=pts2(s["pfg"]), allplay=f"{s['aw']}-{s['al']}", appct=s["appct"],
                luck=s["luck"], rating=pts2(s["rating"]), scores=[pts2(x) for x in s["scores"]], log=log[r],
                power=SITE["power"].index(NAME[r]) + 1, power_move=SITE["power_move"].get(NAME[r], 0),
                odds=SITE["odds"][NAME[r]])
    c = coach_site[NAME[r]]
    T[r]["coach"] = dict(scored=pts2(c["scored"]), best=pts2(c["best"]), benched=pts2(c["benched"]), eff=c["eff"])
# renderStandings order: win %, then points for
for i, r in enumerate(sorted(RIDS, key=lambda r: (-st[r]["winpct"], -st[r]["pf"]))): T[r]["standing"] = i + 1

# ---------- lineups: MVPs, top performances, coach ratings, bench crimes ----------
startpts = collections.defaultdict(collections.Counter)  # roster -> player -> started points
crimes = []
for w in range(1, NW + 1):
    res = {}
    for a, b in pairs(w):
        res[a["roster_id"]] = (a["points"] or 0) - (b["points"] or 0); res[b["roster_id"]] = -res[a["roster_id"]]
    for x in WEEKS[w]:
        r, pp = x["roster_id"], {k: v or 0 for k, v in (x.get("players_points") or {}).items()}
        starters = x.get("starters") or []
        for p, v in zip(starters, x.get("starters_points") or []):
            if p == "0": continue
            startpts[r][p] += v
        bench = [p for p in pp if p not in starters]
        for slot, s in zip(SLOTS, starters):
            ok = FLEX.get(slot, [slot])
            for b in bench:
                if ppos(b) in ok and s != "0" and pp[b] - pp.get(s, 0) > 0:
                    gap = pp[b] - pp.get(s, 0)
                    crimes.append(dict(wk=w, mgr=NAME[r], benched=pname(b), bpts=pts2(pp[b]), started=pname(s), spts=pts2(pp.get(s, 0)),
                                       gap=pts2(gap), margin=pts2(res.get(r, 0)), cost_game=res.get(r, 0) < 0 and gap > -res.get(r, 0)))
for r in RIDS:
    T[r]["mvp"] = [dict(player=pname(p), pos=ppos(p), pts=pts2(v)) for p, v in startpts[r].most_common(3)]
    mv = SITE["season_mvps"][NAME[r]]
    T[r]["season_mvp"] = dict(player=pname(mv["p"]), pos=ppos(mv["p"]), pts=pts2(mv["pts"])) if mv else None
perf = [dict(wk=t["wk"], player=pname(t["p"]), pos=ppos(t["p"]), pts=pts2(t["pts"]), mgr=t["team"]) for t in SITE["top_performances"]]
SEASONPTS = SITE["player_points"]
crimes.sort(key=lambda d: -d["gap"])

# ---------- injuries (the site's list, plus Questionable for context) ----------
INJURED = set(SITE["injured_statuses"])
draftpick = {}
for pk in J(f"{D}/picks.json"):
    draftpick[pk["player_id"]] = dict(rd=pk["round"], no=pk["pick_no"], by=NAME.get(pk["roster_id"]), player=pname(pk["player_id"]), pos=ppos(pk["player_id"]))
for r in rosters:
    rid, inj = r["roster_id"], []
    for p in r.get("players") or []:
        q = PL.get(p) or {}
        if q.get("injury") in INJURED | {"Questionable"}:
            inj.append(dict(player=pname(p), pos=ppos(p), status=q["injury"], on_site_list=q["injury"] in INJURED, body=q.get("injury_body_part"), note=q.get("injury_notes"),
                            started_pts=pts2(startpts[rid][p]), drafted=draftpick.get(p, {}).get("rd")))
    inj.sort(key=lambda d: -d["started_pts"])
    T[rid]["injuries"] = inj
    T[rid]["roster"] = sorted([dict(player=pname(p), pos=ppos(p), pts=pts2(SEASONPTS.get(p, 0)), started=pts2(startpts[rid][p])) for p in r.get("players") or []], key=lambda d: -d["pts"])[:8]

# ---------- draft value (the site's season points per player) ----------
picks = []
for pid, d in draftpick.items():
    picks.append(dict(d, pts=pts2(SEASONPTS.get(pid, 0)), inj=(PL.get(pid) or {}).get("injury")))
picks.sort(key=lambda d: d["no"])
ranked = sorted(picks, key=lambda d: -d["pts"])
for i, d in enumerate(ranked): d["pts_rank"] = i + 1
steals = sorted([d for d in picks if d["rd"] >= 6], key=lambda d: -d["pts"])[:5]
busts = sorted([d for d in picks if d["rd"] <= 3], key=lambda d: d["pts"])[:6]

# ---------- moves (the site's trades, adds and FAAB) ----------
RID = {v: k for k, v in NAME.items()}
trades = [dict(wk=t["w"], teams=t["teams"], adds={pname(p): tm for p, tm in t["adds"].items()}) for t in SITE["moves"]["trades"]]
adds = [dict(wk=a["w"], mgr=a["team"], player=pname(a["p"]), pos=ppos(a["p"]), bid=a["bid"], started_since=pts2(startpts[RID[a["team"]]][a["p"]]))
        for a in SITE["moves"]["adds"]]
adds.sort(key=lambda d: -d["started_since"])
spent = {x["team"]: x["spent"] for x in SITE["moves"]["spent"]}
for r in RIDS:
    T[r]["faab"] = spent.get(NAME[r], 0); T[r]["adds"] = sum(a["mgr"] == NAME[r] for a in adds)

# ---------- next week + head-to-head, as index.html computed them ----------
def h2h_site(a, b):
    """series from a's side, from the site's h2h() (all meetings, playoffs included, consolation excluded)."""
    k = f"{a} | {b}"
    if k in SITE["h2h_all"]: h = dict(SITE["h2h_all"][k]); flip = False
    else: h = dict(SITE["h2h_all"][f"{b} | {a}"]); flip = True
    if flip:
        h["w"], h["l"], h["pw"], h["pl"], h["pf"], h["pa"] = h["l"], h["w"], h["pl"], h["pw"], h["pa"], h["pf"]
        if h["last"]: h["last"] = dict(h["last"], p=h["last"]["op"], op=h["last"]["p"], res={"W": "L", "L": "W"}.get(h["last"]["res"], "T"))
        if h["streak"]: h["streak"] = {"W": "L", "L": "W"}.get(h["streak"][0], "T") + h["streak"][1:]
    h.update(a=a, b=b, playoff=f"{h['pw']}-{h['pl']}", avg_margin=pts2((h["pf"] - h["pa"]) / h["n"]) if h["n"] else 0)
    return h
spot = set(SITE["spotlight"])
nxt = [dict(fav=m["fav"], dog=m["dog"], conf=m["conf"], fav_rec=BYNAME[m["fav"]]["w"] and T[RIDS[0]]["rec"] or "", dog_rec="",
            h2h=h2h_site(m["fav"], m["dog"]), spotlight={m["fav"], m["dog"]} == spot) for m in SITE["next_week"]]
REC = {T[r]["name"]: T[r]["rec"] for r in RIDS}
for m in nxt: m["fav_rec"], m["dog_rec"] = REC[m["fav"]], REC[m["dog"]]
nxt.sort(key=lambda m: not m["spotlight"])
REG = SITE["playoff_week_start"] - 1
SPOTS = SITE["playoff_spots"]

# ---------- history context ----------
cur_labs = set(LAB.values())
def through(season, wk):
    """record and all-play for every manager in a season through week wk (regular season)."""
    out = collections.defaultdict(lambda: dict(w=0, l=0, t=0, pf=0.0, aw=0, al=0))
    byweek = collections.defaultdict(list)
    for x in rows:
        if int(x["season"]) == season and int(x["week"]) <= wk and x["is_playoffs"] != "True":
            o = out[x["manager"]]; o[{"W": "w", "L": "l", "T": "t"}[x["result"]]] += 1; o["pf"] += float(x["points"])
            byweek[x["week"]].append((x["manager"], float(x["points"])))
    for wkrows in byweek.values():
        for m, p in wkrows:
            for m2, p2 in wkrows:
                if m != m2 and p != p2: out[m]["aw" if p > p2 else "al"] += 1
    return out
fin = {(int(s["season"]), s["manager"]): s for s in seasons}
# every saved start through this week, and the same-record comparisons (same teams and playoff spots only), from the lib
def start_row(x):
    return dict(season=x["season"], mgr=disp(x["mgr"]), rec=x["rec"], pf=pts2(x["pf"]), allplay=f"{x['aw']}-{x['al']}", appct=round(x["appct"], 3),
                final_reg=x["final_reg"], final_rank=x["final_rank"], playoffs=x["playoffs"], seed=x["seed"], n_teams=x["n_teams"])
starts = [start_row(x) for x in SITE["starts"]]
def start_summary(rec):
    s = SITE["starts_like_these"].get(rec) or dict(n=0, made_playoffs=0, titles=0, last=0, list=[])
    return dict(s, list=[start_row(x) for x in s["list"]])
start_recs = {rec: start_summary(rec) for rec in sorted({T[r]["rec"] for r in RIDS})}
for r in RIDS:
    same = start_recs[T[r]["rec"]]["list"]
    T[r]["history_comps"] = dict(same_record=len(same), made_playoffs=sum(x["playoffs"] for x in same),
                                 allplay_rank_among_same_record=1 + sum(1 for x in same if x["appct"] > T[r]["appct"]),
                                 closest=sorted(same, key=lambda x: abs(x["appct"] - T[r]["appct"]))[:3])
best_starts = sorted(starts, key=lambda x: -x["appct"])[:6]
worst_starts = sorted(starts, key=lambda x: x["appct"])[:6]
most_pf_starts = sorted(starts, key=lambda x: -x["pf"])[:6]

allscores = sorted([dict(season=int(x["season"]), wk=int(x["week"]), mgr=disp(x["manager"]), pts=float(x["points"]), opp=disp(x["opponent_manager"]),
                         op=float(x["opponent_points"]), res=x["result"], po=x["is_playoffs"] == "True") for x in rows], key=lambda d: -d["pts"])
n_scores = len(allscores)
def rank_of(p): return 1 + sum(1 for d in allscores if d["pts"] > p)
def rank_low(p): return 1 + sum(1 for d in allscores if d["pts"] < p)
hi26 = max((s, NAME[r], i + 1) for r in RIDS for i, s in enumerate(st[r]["scores"]))
lo26 = min((s, NAME[r], i + 1) for r in RIDS for i, s in enumerate(st[r]["scores"]))
blow = max(games, key=lambda g: g["margin"]); close = min(games, key=lambda g: g["margin"])
loss_hi = max((dict(mgr=NAME[r], wk=e["wk"], p=e["p"], opp=e["opp"], op=e["op"]) for r in RIDS for e in log[r] if e["res"] == "L"), key=lambda d: d["p"])
win_lo = min((dict(mgr=NAME[r], wk=e["wk"], p=e["p"], opp=e["opp"], op=e["op"]) for r in RIDS for e in log[r] if e["res"] == "W"), key=lambda d: d["p"])
margins_hist = sorted([abs(float(x["points"]) - float(x["opponent_points"])) for x in rows if x["result"] == "W"], reverse=True)

# careers including this season
car = collections.defaultdict(lambda: dict(w=0, l=0, t=0, pf=0.0, titles=[], seasons=0, playoffs=0, runner=0, last=[]))
for x in rows:
    c = car[x["manager"]]; c[{"W": "w", "L": "l", "T": "t"}[x["result"]]] += 1; c["pf"] += float(x["points"])
for s in seasons:
    c = car[s["manager"]]; c["seasons"] += 1; c["playoffs"] += s["made_playoffs"] == "True"
    if s["final_rank"] == "1": c["titles"].append(int(s["season"]))
    if s["final_rank"] == "2": c["runner"] += 1
for h in lhist: car[h["last_place"]]["last"].append(int(h["season"]))
pre26 = {k: dict(v, titles=list(v["titles"])) for k, v in car.items()}
for r in RIDS:
    c = car[LAB[r]]; c["w"] += st[r]["w"]; c["l"] += st[r]["l"]; c["t"] += st[r]["t"]; c["pf"] += st[r]["pf"]
career = sorted([dict(mgr=disp(k), active=k in cur_labs, w=v["w"], l=v["l"], pct=round(v["w"] / max(1, v["w"] + v["l"] + v["t"]), 3), pf=pts2(v["pf"]),
                      pf_pre=pts2(pre26[k]["pf"]) if k in pre26 else 0, w_pre=pre26[k]["w"] if k in pre26 else 0,
                      titles=v["titles"], runner=v["runner"], seasons=v["seasons"], playoffs=v["playoffs"], last=v["last"]) for k, v in car.items()], key=lambda d: -d["w"])

per_mgr = {}
for r in RIDS:
    lab = LAB[r]; ss = sorted([s for s in seasons if s["manager"] == lab], key=lambda s: int(s["season"]))
    per_mgr[NAME[r]] = dict(history_label=lab, seasons=[dict(y=int(s["season"]), rank=int(s["final_rank"]), reg=s["regular_season_record"], seed=s["playoff_seed"], pf=float(s["points_for"])) for s in ss])
champs = [dict(season=int(h["season"]), champ=disp(h["champion"]), runner=disp(h["runner_up"]), last=disp(h["last_place"]), score=h["championship_score"], reg_winner=disp(h["regular_season_winner"])) for h in lhist]
repeat = [(a["season"], a["champ"]) for a, b in zip(champs, champs[1:]) if a["champ"] == b["champ"]]
champ_next = []
for a in champs[:-1]:
    f = fin.get((a["season"] + 1, alias.get(a["champ"], a["champ"]))) or fin.get((a["season"] + 1, next((k for k, v in SHOW.items() if NAME[v] == a["champ"]), a["champ"])))
    champ_next.append(dict(season=a["season"], champ=a["champ"], next_rank=int(f["final_rank"]) if f else None, next_reg=f["regular_season_record"] if f else None))

# rivalries among current managers
riv = []
for i, a in enumerate(RIDS):
    for b in RIDS[i + 1:]:
        h = h2h_site(NAME[a], NAME[b])
        if h["n"] >= 6: riv.append(h)
riv_lopsided = sorted(riv, key=lambda h: -abs(h["w"] - h["l"]) / h["n"])[:6]
riv_most = sorted(riv, key=lambda h: -h["n"])[:4]

# season-level all-play record lows/highs (full regular seasons) for context
def full_allplay():
    out = []
    for y in sorted({int(s["season"]) for s in seasons}):
        wk_max = max(int(x["week"]) for x in rows if int(x["season"]) == y and x["is_playoffs"] != "True")
        for m, o in through(y, wk_max).items():
            out.append(dict(season=y, mgr=disp(m), allplay=f"{o['aw']}-{o['al']}", appct=round(o["aw"] / max(1, o["aw"] + o["al"]), 3), rec=f"{o['w']}-{o['l']}"))
    return out
fa = full_allplay()

out = dict(
    league=lg["name"], season=lg["season"], n_teams=len(RIDS), weeks_done=NW, reg_weeks=REG, playoff_spots=SPOTS, trade_deadline=lg["settings"].get("trade_deadline"),
    model_pick_record=SITE["pick_record"],
    teams=sorted(T.values(), key=lambda t: t["standing"]),
    hardware=dict(high=dict(pts=hi26[0], mgr=hi26[1], wk=hi26[2], alltime_rank=rank_of(hi26[0]), of=n_scores),
                  low=dict(pts=lo26[0], mgr=lo26[1], wk=lo26[2], alltime_low_rank=rank_low(lo26[0])),
                  blowout=dict(blow, alltime_rank=1 + sum(1 for m in margins_hist if m > blow["margin"]), of=len(margins_hist)),
                  closest=close, most_in_loss=loss_hi, fewest_in_win=win_lo,
                  top_perf=perf[:8], all_games=games),
    alltime_top_scores=allscores[:8], alltime_low_scores=allscores[-5:],
    bench_crimes=crimes[:10], costly_crimes=[c for c in crimes if c["cost_game"]][:8],
    draft=dict(steals=steals, busts=busts, first_two_rounds=[d for d in picks if d["rd"] <= 2]),
    moves=dict(trades=trades, top_adds=adds[:8], total_adds=len(adds)),
    next_week=nxt,
    history=dict(champions=champs, repeat_champs=repeat, champ_next_year=champ_next,
                 starts_like_these=start_recs, starts_format=SITE["starts_format"], best_starts_through_n=best_starts, worst_starts_through_n=worst_starts, most_pf_through_n=most_pf_starts,
                 career=career, per_manager=per_mgr, rivalries_lopsided=riv_lopsided, rivalries_most_played=riv_most,
                 best_full_season_allplay=sorted(fa, key=lambda d: -d["appct"])[:5], worst_full_season_allplay=sorted(fa, key=lambda d: d["appct"])[:5]),
)
json.dump(out, sys.stdout, indent=1, default=str)
