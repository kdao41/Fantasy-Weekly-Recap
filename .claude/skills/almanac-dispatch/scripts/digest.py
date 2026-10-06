"""Bounded readout of a facts JSON: everything worth writing about, one line per item, so the full file never
has to be read into context.
usage: python3 -I digest.py <facts.json>"""
import json, sys

d = json.load(open(sys.argv[1])); h = d["history"]; hw = d["hardware"]
print(f"== {d['league']} {d['season']} · {d['n_teams']} teams · through Week {d['weeks_done']} · {d['playoff_spots']} make playoffs · reg season {d['reg_weeks']} wks · trade deadline wk {d['trade_deadline']}")
print("\nTEAMS (standing order): rec PF PA all-play luck | power(move) | odds | coach | faab/adds | scores | top starters | injuries | history comps")
for t in d["teams"]:
    o, c, hc = t["odds"], t["coach"], t["history_comps"]
    print(f"{t['standing']:>2} {t['name']} [{t['team']}] {t['rec']} PF {t['pf']} PA {t['pa']} AP {t['allplay']} luck {t['luck']:+} | P{t['power']}({t['power_move']:+})"
          f" | PO {o['playoffs']:.1%} 1st {o['seed1']:.1%} title {o['title']:.1%} | eff {c['eff']:.1%} benched {c['benched']} | ${t['faab']}/{t['adds']} | {t['scores']}")
    print(f"     top: {[(m['player'], m['pts']) for m in t['mvp']]} | inj: {[(i['player'], i['status'], i['started_pts'], i['drafted']) for i in t['injuries'][:5]]}")
    print(f"     same start: {hc['made_playoffs']}/{hc['same_record']} made playoffs; AP rank {hc['allplay_rank_among_same_record']} of {hc['same_record'] + 1}; closest: "
          f"{[(x['season'], x['mgr'], x['allplay'], x['final_reg'], x['final_rank']) for x in hc['closest']]}")

print("\nCHAMPIONS:"); [print(f"  {c['season']} {c['champ']} over {c['runner']} {c['score']} | last: {c['last']} | reg-season winner: {c['reg_winner']}") for c in h["champions"]]
print("repeat champions:", h["repeat_champs"] or "none")
print("champion's next season:", [(c["season"], c["champ"], c["next_rank"], c["next_reg"]) for c in h["champ_next_year"]])
f = h["starts_format"]
print(f"START comps count only seasons with {f['n_teams']} teams and {f['spots']} playoff spots: {f['seasons']}")
for rec, s in h["starts_like_these"].items():
    print(f"START {rec}: n={s['n']} playoffs={s['made_playoffs']} titles={s['titles']} last={s['last']}")
print("best starts by all-play:", [(x["season"], x["mgr"], x["rec"], x["allplay"], x["final_rank"]) for x in h["best_starts_through_n"]])
print("worst starts by all-play:", [(x["season"], x["mgr"], x["rec"], x["allplay"], x["final_rank"]) for x in h["worst_starts_through_n"]])
print("most points through this week:", [(x["season"], x["mgr"], x["rec"], x["pf"], x["final_rank"]) for x in h["most_pf_through_n"]])
print("best full-season all-play:", [(x["season"], x["mgr"], x["allplay"], x["rec"]) for x in h["best_full_season_allplay"]])
print("worst full-season all-play:", [(x["season"], x["mgr"], x["allplay"], x["rec"]) for x in h["worst_full_season_allplay"]])

print("\nCAREERS (this season included; pf_pre/w_pre = before it):")
for c in h["career"]:
    print(f"  {c['mgr']} {c['w']}-{c['l']} ({c['pct']}) PF {c['pf']} (pre {c['pf_pre']}, W pre {c['w_pre']}) titles {c['titles']} runner-ups {c['runner']} seasons {c['seasons']} playoffs {c['playoffs']} last {c['last']}{'' if c['active'] else ' (no longer in league)'}")
for n, m in h["per_manager"].items(): print(f"  finishes {n}: " + " ".join(f"{s['y'] % 100:02d}:{s['rank']}" for s in m["seasons"]))
print("lopsided rivalries:", [(r["a"], r["b"], f"{r['w']}-{r['l']}", "po " + r["playoff"], r["streak"]) for r in h["rivalries_lopsided"]])
print("most-played:", [(r["a"], r["b"], f"{r['w']}-{r['l']}", r["n"], "po " + r["playoff"]) for r in h["rivalries_most_played"]])

print("\nHARDWARE:")
for k in ("high", "low", "blowout", "closest", "most_in_loss", "fewest_in_win"): print(f"  {k}: {hw[k]}")
print("  top performances:", [(p["player"], p["pts"], p["mgr"], p["wk"]) for p in hw["top_perf"]])
print("  all-time top scores:", [(x["season"], x["wk"], x["mgr"], x["pts"]) for x in d["alltime_top_scores"]])
print("  all-time low scores:", [(x["season"], x["wk"], x["mgr"], x["pts"]) for x in d["alltime_low_scores"]])
print("  games:", [(g["wk"], g["win"], g["wp"], g["lose"], g["lp"]) for g in hw["all_games"]])

print("\nNEXT WEEK (favorite first; h2h from the favorite's side, playoffs included, consolation excluded):")
for n in d["next_week"]:
    x = n["h2h"]; print(f"  {'MATCHUP OF THE WEEK (same pick as index.html) ' if n.get('spotlight') else ''}{n['fav']} {n['fav_rec']} vs {n['dog']} {n['dog_rec']} fav {n['conf']:.0%} | h2h {x['w']}-{x['l']} po {x['playoff']} streak {x['streak']} last {x['last']}")
print("\nLINEUP CALLS THAT COST A GAME:", [(c["mgr"], c["wk"], c["benched"], c["bpts"], c["started"], c["spts"], c["margin"]) for c in d["costly_crimes"]])
print("biggest bench gaps:", [(c["mgr"], c["wk"], c["benched"], c["bpts"], c["started"], c["spts"]) for c in d["bench_crimes"][:5]])
print("DRAFT steals (rd 6+):", [(x["player"], x["rd"], x["no"], x["by"], x["pts"]) for x in d["draft"]["steals"]])
print("DRAFT busts (rd 1-3):", [(x["player"], x["rd"], x["no"], x["by"], x["pts"], x["inj"]) for x in d["draft"]["busts"]])
print("MOVES trades:", d["moves"]["trades"] or "none", "| adds:", d["moves"]["total_adds"], "| best adds:", [(a["mgr"], a["player"], a["bid"], a["started_since"]) for a in d["moves"]["top_adds"][:5]])
