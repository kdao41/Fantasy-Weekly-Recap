"""Turn normalized league seasons into the organized history files.

Each season is a dict in the raw/<season>.json shape written by yahoo_scrape.py
(and sleeper_export.py): league settings, teams with final rank/seed/record,
weekly matchup rows keyed by week, and draft picks. The builder doesn't care
which platform a season came from. See data/yahoo/aggtown/README.md for the
output files.
"""
import csv
import json
import sys
from pathlib import Path


def manager_id(team, season):
    # guid is stable across seasons and nickname changes; hidden managers have none.
    guid = team.get("manager_guid")
    # Yahoo reports a hidden manager's guid as "--", which would merge all hidden managers into one.
    return guid if guid and guid.strip("-") else f"unknown-{season}-team{team['team_id']}"


def load_managers(path, seasons):
    managers = json.loads(path.read_text()) if path.exists() else {}
    for s in seasons:
        for t in s["teams"]:
            m = managers.setdefault(manager_id(t, s["season"]), {"real_name": "", "nicknames": [], "teams": {}})
            if t["manager"] and t["manager"] not in m["nicknames"]:
                m["nicknames"].append(t["manager"])
            m["teams"][str(s["season"])] = t["name"]
    path.write_text(json.dumps(managers, indent=1, sort_keys=True))
    return managers


def label(managers, mid):
    m = managers.get(mid, {})
    nick = m["nicknames"][-1] if m.get("nicknames") else mid
    return f"{nick} ({m['real_name']})" if m.get("real_name") else nick


def week_history(season, weeks_out):
    """Adds standings-after-the-week and highlights to each week. Standings cover the regular
    season only, ranked by win % then points for (Yahoo's default tiebreak); playoff weeks get
    highlights only."""
    rec, standing_rows, highlight_rows = {}, [], []
    for w, data in sorted(weeks_out.items()):
        games = [m for m in data["matchups"] if len(m["teams"]) == 2]
        scored = [t for m in data["matchups"] for t in m["teams"]]
        hi = max(scored, key=lambda t: t["points"])
        lo = min(scored, key=lambda t: t["points"])
        margin = lambda m: abs(m["teams"][0]["points"] - m["teams"][1]["points"])
        game = lambda m: (lambda win, lose: {"winner": win["manager"], "winner_points": win["points"],
                                             "loser": lose["manager"], "loser_points": lose["points"],
                                             "margin": round(margin(m), 2)})(
            *sorted(m["teams"], key=lambda t: -t["points"]))
        data["highlights"] = {
            "high_score": {"manager": hi["manager"], "team": hi["team"], "points": hi["points"]},
            "low_score": {"manager": lo["manager"], "team": lo["team"], "points": lo["points"]},
            "closest_game": game(min(games, key=margin)) if games else None,
            "biggest_blowout": game(max(games, key=margin)) if games else None,
        }
        h = data["highlights"]
        highlight_rows.append({
            "season": season, "week": w, "is_playoffs": data["is_playoffs"],
            "high_score_manager": h["high_score"]["manager"], "high_score": h["high_score"]["points"],
            "low_score_manager": h["low_score"]["manager"], "low_score": h["low_score"]["points"],
            "closest_game": (f"{h['closest_game']['winner']} over {h['closest_game']['loser']} by {h['closest_game']['margin']}"
                             if h["closest_game"] else None),
            "biggest_blowout": (f"{h['biggest_blowout']['winner']} over {h['biggest_blowout']['loser']} by {h['biggest_blowout']['margin']}"
                                if h["biggest_blowout"] else None),
        })
        if data["is_playoffs"]:
            continue

        week_result = {}
        for m in data["matchups"]:
            for t in m["teams"]:
                opp = next((o for o in m["teams"] if o is not t), None)
                res = "W" if t["won"] else ("L" if opp and opp["won"] else "T")
                week_result[t["team_id"]] = (t, opp, res)
                r = rec.setdefault(t["team_id"], {"W": 0, "L": 0, "T": 0, "pf": 0.0, "pa": 0.0, "streak": ""})
                r[res] += 1
                r["pf"] += t["points"]
                r["pa"] += opp["points"] if opp else 0
                r["streak"] = (res + str(int(r["streak"][1:]) + 1)) if r["streak"][:1] == res else res + "1"
        order = sorted(rec, key=lambda tid: (-(rec[tid]["W"] + rec[tid]["T"] / 2) / max(1, sum(rec[tid][k] for k in "WLT")),
                                             -rec[tid]["pf"]))
        table = []
        for rank, tid in enumerate(order, start=1):
            r = rec[tid]
            t, opp, res = week_result.get(tid, (None, None, None))
            row = {"rank": rank, "manager": t["manager"] if t else None, "team": t["team"] if t else None,
                   "record": fmt(r), "points_for": round(r["pf"], 2), "points_against": round(r["pa"], 2),
                   "streak": r["streak"], "week_points": t["points"] if t else None, "week_result": res,
                   "opponent": opp["manager"] if opp else None}
            table.append(row)
            standing_rows.append({"season": season, "week": w, **row})
        data["standings_after_week"] = table
    return standing_rows, highlight_rows


def build_season(s, managers, sdir):
    season = s["season"]
    teams = {t["team_id"]: t for t in s["teams"]}
    who = {tid: label(managers, manager_id(t, season)) for tid, t in teams.items()}

    def team_ref(tid):
        return {"team_id": tid, "team": teams[tid]["name"], "manager": who[tid]} if tid in teams else {"team_id": tid}

    standings = []
    for t in sorted(s["teams"], key=lambda t: (t["rank"] or 99)):
        standings.append({**team_ref(t["team_id"]), "final_rank": t["rank"], "playoff_seed": t["playoff_seed"],
                          "wins": t["wins"], "losses": t["losses"], "ties": t["ties"],
                          "points_for": t["points_for"], "points_against": t["points_against"]})

    weeks_out, playoff_games = {}, []
    for w, rows in sorted(s["weeks"].items(), key=lambda kv: int(kv[0])):
        games = {}
        for r in rows:
            games.setdefault(r["matchup_id"], []).append(r)
        matchups = []
        for g in games.values():
            entry = {
                "is_playoffs": g[0]["is_playoffs"],
                "is_consolation": g[0]["is_consolation"],
                "teams": [{**team_ref(r["roster_id"]), "points": r["points"], "projected": r["projected"],
                           "won": r["won"]} for r in g],
            }
            winner = next((t for t in entry["teams"] if t["won"]), None)
            entry["winner"] = winner["manager"] if winner else None
            matchups.append(entry)
            if entry["is_playoffs"] and not entry["is_consolation"]:
                playoff_games.append({"week": int(w), **entry})
        weeks_out[int(w)] = {"season": season, "week": int(w),
                             "is_playoffs": any(m["is_playoffs"] for m in matchups), "matchups": matchups}

    weekly_standings, weekly_highlights = week_history(season, weeks_out)

    by_rank = {t["final_rank"]: t for t in standings}
    title_game = None
    if s["is_finished"] and playoff_games and by_rank.get(1):
        # The final week also holds 3rd-place and other placement games; the title game is the champion's.
        last = max(g["week"] for g in playoff_games)
        champ_id = by_rank[1]["team_id"]
        g = next((g for g in playoff_games if g["week"] == last and any(t["team_id"] == champ_id for t in g["teams"])), None)
        if g:
            w = next(t for t in g["teams"] if t["team_id"] == champ_id)
            l = next((t for t in g["teams"] if t is not w), None)
            title_game = {"week": last, "winner": w["manager"], "winner_team": w["team"], "winner_points": w["points"],
                          "loser": l["manager"] if l else None, "loser_team": l["team"] if l else None,
                          "loser_points": l["points"] if l else None}
    reg_winner = next((t for t in standings if t["playoff_seed"] == 1), None)
    summary = {
        "season": season,
        "league": s["name"],
        "finished": s["is_finished"],
        "champion": by_rank.get(1) if s["is_finished"] else None,
        "championship_game": title_game,
        "runner_up": by_rank.get(2) if s["is_finished"] else None,
        "third_place": by_rank.get(3) if s["is_finished"] else None,
        "last_place": by_rank.get(max(by_rank)) if s["is_finished"] and by_rank else None,
        "regular_season_winner": reg_winner,
        "most_points": max(standings, key=lambda t: t["points_for"]) if standings else None,
    }

    (sdir / "weeks").mkdir(parents=True, exist_ok=True)
    for w, data in weeks_out.items():
        (sdir / "weeks" / f"week-{w:02d}.json").write_text(json.dumps(data, indent=1))
    draft = [{**team_ref(d["team_id"]), **{k: d.get(k) for k in ("round", "pick", "cost", "player", "position", "nfl_team")}}
             for d in s["draft"]]
    (sdir / "draft.json").write_text(json.dumps(draft, indent=1))
    settings = {k: s[k] for k in ("league_key", "num_teams", "start_week", "end_week", "playoff_week_start",
                                  "num_playoff_teams", "scoring_type", "draft_type", "roster_positions")}
    (sdir / "season.json").write_text(json.dumps(
        {**summary, "settings": settings, "standings": standings, "playoff_results": playoff_games}, indent=1))
    write_csv(sdir / "standings.csv", standings)

    score_rows = []
    for w, data in weeks_out.items():
        for m in data["matchups"]:
            for t in m["teams"]:
                opp = next((o for o in m["teams"] if o is not t), None)
                score_rows.append({
                    "season": season, "week": w, "is_playoffs": m["is_playoffs"], "is_consolation": m["is_consolation"],
                    "manager": t.get("manager"), "team": t.get("team"), "points": t["points"],
                    "opponent_manager": opp.get("manager") if opp else None,
                    "opponent_team": opp.get("team") if opp else None,
                    "opponent_points": opp["points"] if opp else None,
                    "result": "W" if t["won"] else ("L" if opp and opp["won"] else "T"),
                })
    write_csv(sdir / "weekly_standings.csv", weekly_standings)
    write_csv(sdir / "weekly_highlights.csv", weekly_highlights)
    return summary, score_rows, standings, s["num_playoff_teams"], weekly_standings, weekly_highlights


def wlt(rows):
    return {r: sum(1 for x in rows if x["result"] == r) for r in "WLT"}


def fmt(rec):
    return f"{rec['W']}-{rec['L']}" + (f"-{rec['T']}" if rec["T"] else "")


def season_records(season, standings, scores, num_playoff_teams):
    """One row per manager: regular season, championship-bracket playoffs, consolation, and total
    (regular season + playoffs; consolation games don't count toward it)."""
    rows = []
    for t in standings:
        mine = [r for r in scores if r["manager"] == t["manager"] and r["team"] == t["team"]]
        reg = wlt([r for r in mine if not r["is_playoffs"]])
        po = wlt([r for r in mine if r["is_playoffs"] and not r["is_consolation"]])
        con = wlt([r for r in mine if r["is_consolation"]])
        tot = {k: reg[k] + po[k] for k in "WLT"}
        rows.append({
            "season": season, "manager": t["manager"], "team": t["team"],
            "final_rank": t["final_rank"], "playoff_seed": t["playoff_seed"],
            "made_playoffs": bool(t["playoff_seed"] and num_playoff_teams and t["playoff_seed"] <= num_playoff_teams),
            "regular_season_record": fmt(reg), "playoff_record": fmt(po), "consolation_record": fmt(con),
            "total_record": fmt(tot),
            "total_wins": tot["W"], "total_losses": tot["L"], "total_ties": tot["T"],
            "regular_wins": reg["W"], "regular_losses": reg["L"], "regular_ties": reg["T"],
            "playoff_wins": po["W"], "playoff_losses": po["L"],
            "points_for": t["points_for"], "points_against": t["points_against"],
            # Yahoo's own standings count, kept to catch any mismatch with the weekly games.
            "_yahoo_wins": t["wins"], "_yahoo_losses": t["losses"],
        })
    return rows


def career_records(season_rows, managers):
    by_mgr = {}
    for r in season_rows:
        by_mgr.setdefault(r["manager"], []).append(r)
    out = []
    for mgr, rows in by_mgr.items():
        add = lambda k: sum(r[k] for r in rows)
        tot = {"W": add("total_wins"), "L": add("total_losses"), "T": add("total_ties")}
        reg = {"W": add("regular_wins"), "L": add("regular_losses"), "T": add("regular_ties")}
        po = {"W": add("playoff_wins"), "L": add("playoff_losses"), "T": 0}
        games = tot["W"] + tot["L"] + tot["T"]
        out.append({
            "manager": mgr, "seasons": len(rows),
            "championships": sum(1 for r in rows if r["final_rank"] == 1),
            "championship_seasons": " ".join(str(r["season"]) for r in rows if r["final_rank"] == 1),
            "runner_ups": sum(1 for r in rows if r["final_rank"] == 2),
            "playoff_appearances": sum(1 for r in rows if r["made_playoffs"]),
            "total_record": fmt(tot), "win_pct": round((tot["W"] + tot["T"] / 2) / games, 3) if games else None,
            "regular_season_record": fmt(reg), "playoff_record": fmt(po),
            "points_for": round(add("points_for"), 2), "points_against": round(add("points_against"), 2),
        })
    return sorted(out, key=lambda r: (-r["championships"], -(r["win_pct"] or 0)))


def write_csv(path, rows):
    if not rows:
        return
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def build_dir(out, seasons):
    """Write every summary file into `out` from normalized seasons (the raw/<season>.json shape).
    Seasons can come from any platform; managers are matched across them by manager_guid."""
    out = Path(out)
    if not seasons:
        sys.exit(f"No seasons to build into {out}.")
    managers = load_managers(out / "managers.json", seasons)

    history, all_scores, record_rows, all_standings, all_highlights = [], [], [], [], []
    for s in seasons:
        if not s["weeks"]:
            print(f"  {s['season']}: no games played on Yahoo, skipped")
            continue
        summary, scores, standings, n_playoff, wk_standings, wk_highlights = build_season(
            s, managers, out / "seasons" / str(s["season"]))
        all_standings += wk_standings
        all_highlights += wk_highlights
        history.append(summary)
        all_scores += scores
        records = season_records(s["season"], standings, scores, n_playoff)
        bad = [r["manager"] for r in records if (r["regular_wins"], r["regular_losses"]) != (r["_yahoo_wins"], r["_yahoo_losses"])]
        if bad:
            print(f"  warning {s['season']}: regular-season record differs from Yahoo's standings for {', '.join(bad)}")
        for r in records:
            del r["_yahoo_wins"], r["_yahoo_losses"]
        write_csv(out / "seasons" / str(s["season"]) / "records.csv", records)
        record_rows += records

    (out / "league_history.json").write_text(json.dumps(history, indent=1))
    pick = lambda t: t["manager"] if t else None
    write_csv(out / "league_history.csv", [{
        "season": h["season"], "league": h["league"], "champion": pick(h["champion"]),
        "champion_team": h["champion"]["team"] if h["champion"] else None,
        "championship_score": (f"{h['championship_game']['winner_points']} - {h['championship_game']['loser_points']}"
                               if h["championship_game"] else None),
        "runner_up": pick(h["runner_up"]), "third_place": pick(h["third_place"]),
        "regular_season_winner": pick(h["regular_season_winner"]), "most_points": pick(h["most_points"]),
        "last_place": pick(h["last_place"]),
    } for h in history])
    write_csv(out / "all_weekly_scores.csv", all_scores)
    write_csv(out / "manager_season_records.csv", record_rows)
    write_csv(out / "weekly_standings.csv", all_standings)
    write_csv(out / "weekly_highlights.csv", all_highlights)
    write_csv(out / "manager_career_records.csv", career_records(record_rows, managers))

    print(f"\nBuilt {len(history)} seasons in {out}")
    for h in history:
        g = h["championship_game"]
        champ = f"{g['winner']} beat {g['loser']} {g['winner_points']}-{g['loser_points']}" if g else "(season not finished)"
        print(f"  {h['season']}  champion: {champ}")
    unnamed = sum(1 for m in managers.values() if not m["real_name"])
    if unnamed:
        print(f"\n{unnamed} managers have no real_name yet: fill them in {out / 'managers.json'}, then run `build`.")
