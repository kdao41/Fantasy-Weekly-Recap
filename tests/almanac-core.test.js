import { createRequire } from "node:module";
import { readFileSync } from "node:fs";
import { describe, it, expect } from "vitest";

// the module is a plain script (so index.html can load it with <script src>), so load it the CommonJS way
const Core = createRequire(import.meta.url)("../lib/almanac-core.js");

// Four teams, three finished weeks, two scheduled. Every expected number below is worked out by hand:
//   wk1  A 120 - B 100   C  90 - D 110
//   wk2  A 130 - C  95   B 105 - D 105 (tie)
//   wk3  A 140 - D  80   B  99 - C 101
// Records A 3-0, B 0-2-1, C 1-2, D 1-1-1. All-play A 9-0, B 3-5, C 2-7, D 3-5.
const m = (roster_id, matchup_id, points) => ({ roster_id, matchup_id, points });
const WEEKS = [
  [m(1, 1, 120), m(2, 1, 100), m(3, 2, 90), m(4, 2, 110)],
  [m(1, 1, 130), m(3, 1, 95), m(2, 2, 105), m(4, 2, 105)],
  [m(1, 1, 140), m(4, 1, 80), m(2, 2, 99), m(3, 2, 101)],
  [m(1, 1, 0), m(2, 1, 0), m(3, 2, 0), m(4, 2, 0)],
  [m(1, 1, 0), m(3, 1, 0), m(2, 2, 0), m(4, 2, 0)],
];
const users = ["A", "B", "C", "D"].map((n, i) => ({ user_id: `u${i + 1}`, display_name: n }));
const rosters = [1, 2, 3, 4].map(r => ({ roster_id: r, owner_id: `u${r}`, settings: {} }));

function league() {
  const lg = { league_id: "123", season: "2026", settings: { playoff_week_start: 6, playoff_teams: 2 }, roster_positions: ["QB", "RB", "WR", "FLEX", "BN"] };
  const state = { season: "2026", season_type: "regular", week: 4 };
  const CUR = { lg, rName: Core.teamNames(users, rosters), rosters, ...Core.splitWeeks(lg, state, WEEKS), pwk: 6, id: lg.league_id };
  const { T, games, completed } = Core.compute(CUR);
  Object.assign(CUR, { _T: T, _games: games, _completed: completed });
  return CUR;
}
const team = (CUR, name) => CUR._T.find(t => t.name === name);

describe("names", () => {
  it("escapes once and unescapes back", () => {
    expect(Core.esc('A&B <"x">')).toBe("A&amp;B &lt;&quot;x&quot;&gt;");
    expect(Core.unesc(Core.esc('A&B <"x">'))).toBe('A&B <"x">');
  });
  it("names rosters by display name, then username, then roster number", () => {
    const names = Core.teamNames(
      [{ user_id: "a", display_name: "Tom & Jerry" }, { user_id: "b", username: "bob" }],
      [{ roster_id: 1, owner_id: "a" }, { roster_id: 2, owner_id: "b" }, { roster_id: 3, owner_id: null }]);
    expect(names).toEqual({ 1: "Tom &amp; Jerry", 2: "bob", 3: "Team 3" });
  });
});

describe("weeks", () => {
  it("treats weeks before Sleeper's current week as final", () => {
    const lg = { season: "2026" }, state = { season: "2026", season_type: "regular", week: 5 };
    expect(Core.isFinal(lg, state, 4)).toBe(true);
    expect(Core.isFinal(lg, state, 5)).toBe(false);
    expect(Core.isFinal({ season: "2025" }, state, 12)).toBe(true);
  });
  it("splits finished weeks from the schedule at the first unfinished week", () => {
    const CUR = league();
    expect(Object.keys(CUR.weeks).map(Number)).toEqual([1, 2, 3]);
    expect(CUR.upWeek).toBe(4);
    expect(Object.keys(CUR.sched).map(Number)).toEqual([4, 5]);
  });
  it("keeps a final week with no points yet in the schedule", () => {
    const { weeks, upWeek } = Core.splitWeeks({ season: "2026" }, { season: "2026", season_type: "regular", week: 9 }, [WEEKS[0], WEEKS[3]]);
    expect(Object.keys(weeks)).toEqual(["1"]);
    expect(upWeek).toBe(2);
  });
});

describe("compute", () => {
  const CUR = league();
  it("builds records, points and all-play", () => {
    expect(["A", "B", "C", "D"].map(n => Core.recstr(team(CUR, n)))).toEqual(["3-0", "0-2-1", "1-2", "1-1-1"]);
    expect(team(CUR, "A")).toMatchObject({ pf: 390, pa: 275, aw: 9, al: 0, appct: 1 });
    expect(team(CUR, "B")).toMatchObject({ pf: 304, pa: 326, aw: 3, al: 5, appct: 0.375 });
    expect(team(CUR, "C")).toMatchObject({ aw: 2, al: 7 });
  });
  it("measures luck as wins minus the wins the scores earned", () => {
    expect(Core.luckWins(team(CUR, "A"))).toBe(0);
    expect(Core.luckWins(team(CUR, "B"))).toBeCloseTo(0.5 - 0.375 * 3);
    expect(Core.luckWins(team(CUR, "C"))).toBeCloseTo(1 - (2 / 9) * 3);
  });
  it("lists every game winner first", () => {
    expect(CUR._games).toHaveLength(6);
    expect(CUR._games[0]).toEqual({ wk: 1, hi: "A", lo: "B", hip: 120, lop: 100 });
  });
});

describe("power board and standings", () => {
  const CUR = league();
  const power = [...CUR._T].sort(Core.byPower);
  it("orders power by all-play, then points", () => {
    expect(power.map(t => t.name)).toEqual(["A", "B", "D", "C"]);
  });
  it("orders standings by win %, then points", () => {
    expect([...CUR._T].sort(Core.byRec).map(t => t.name)).toEqual(["A", "D", "C", "B"]);
  });
  it("moves teams against the board one week earlier", () => {
    // after week 2 the board was A, D (3-1 all-play), B, C
    expect(Core.powerMoves(CUR, power, CUR._completed)).toEqual({ A: 0, B: 1, D: -1, C: 0 });
  });
});

describe("the model", () => {
  const CUR = league();
  it("gives an even game 50% and the stronger team more", () => {
    expect(Core.CONF(0)).toBeCloseTo(0.5);
    const { rate } = Core.strengthThrough(CUR, 3);
    expect(rate[1]).toBeGreaterThan(rate[3]);
  });
  it("picks the matchup of the week by combined all-play and closeness", () => {
    const pairs = Core.matchupPairs(CUR);
    expect(pairs.map(p => [p.a, p.b])).toEqual([["A", "B"], ["C", "D"]]);
    expect(pairs[0].pa).toBeGreaterThan(0.5);
    expect(Core.spotlight(CUR._T, pairs)).toMatchObject({ a: "A", b: "B" });
  });
  it("grades its own past picks, skipping week 1", () => {
    // week 2: A over C (hit), B-D tie (not graded); week 3: A over D (hit), B over C (miss, C won 101-99)
    expect(Core.pickRecord(CUR)).toMatchObject({ correct: 2, total: 3 });
  });
  it("posts next week's picks favorite first", () => {
    const up = Core.upcomingPicks(CUR);
    expect(up.week).toBe(4);
    expect(up.picks[0]).toMatchObject({ fav: "A", dog: "B" });
  });
});

describe("playoff odds", () => {
  it("is seeded, so the same week always gives the same odds", () => {
    expect(Core.rng("1389331035040260096:4")()).toBe(0.39919281634502113);
    expect(Core.playoffOdds(league())).toEqual(Core.playoffOdds(league()));
  });
  it("adds up: two playoff spots, one 1 seed, one champion per simulated season", () => {
    const odds = Core.playoffOdds(league());
    const sum = k => odds.reduce((a, o) => a + o[k], 0);
    expect(sum("playoff")).toBeCloseTo(2);
    expect(sum("top")).toBeCloseTo(1);
    expect(sum("title")).toBeCloseTo(1);
    expect(odds.find(o => o.name === "A").title).toBe(Math.max(...odds.map(o => o.title)));
  });
});

describe("coach ratings", () => {
  const ppos = p => ({ q: "QB", r: "RB", w: "WR" })[p[0]];
  it("fills strict slots before the flex", () => {
    const pp = { q1: 20, q2: 25, r1: 10, r2: 8, w1: 15, w2: 12 };
    expect(Core.bestLineup(["QB", "RB", "WR", "FLEX", "BN"], pp, ppos)).toBe(25 + 10 + 15 + 12);
  });
  it("uses Sleeper's own best-lineup points when every roster has them", () => {
    const CUR = league();
    CUR.rosters = rosters.map(r => ({ ...r, settings: { fpts: 300, fpts_decimal: 50, ppts: 350, ppts_decimal: 0 } }));
    expect(Core.coachRows(CUR, null)[0]).toEqual({ name: "A", act: 300.5, opt: 350 });
  });
  it("needs player positions to rebuild lineups otherwise", () => {
    expect(Core.coachRows(league(), null)).toBeNull();
  });
  it("rates efficiency, benched points, best first", () => {
    const rows = Core.rateCoaches([{ name: "x", act: 90, opt: 100 }, { name: "y", act: 95, opt: 100 }]);
    expect(rows.map(r => [r.name, r.eff, r.left])).toEqual([["y", 0.95, 5], ["x", 0.9, 10]]);
  });
});

describe("players and moves", () => {
  const box = (roster_id, starters, players_points) => ({ roster_id, matchup_id: 1, points: 0, starters, players_points });
  const weeks = {
    1: [box(1, ["q", "r"], { q: 31, r: 12, w: 40 }), box(2, ["x"], { x: 30 })],
    2: [box(1, ["q", "w"], { q: 18, r: 2, w: 9 }), box(2, ["x"], { x: 29.5 })],
  };
  it("totals each player's points whether started or not", () => {
    expect(Core.playerPoints(weeks)).toEqual({ q: 49, r: 14, w: 49, x: 59.5 });
  });
  it("names each roster's top scorer", () => {
    const mvps = Core.seasonMvps({ weeks, rName: { 1: "A", 2: "B", 3: "C" } });
    expect(mvps[1]).toEqual({ p: "q", pts: 49 });
    expect(mvps[3]).toBeNull();
  });
  it("lists started games of 30+ only, best first", () => {
    // w's 40 came off the bench, x's 29.5 is under the bar
    expect(Core.topPerformances(weeks).map(t => [t.p, t.wk, t.pts])).toEqual([["q", 1, 31], ["x", 1, 30]]);
  });
  it("counts completed moves only, biggest bid first, FAAB by first spender", () => {
    const txs = [
      [{ status: "complete", type: "waiver", adds: { a: 2 }, settings: { waiver_bid: 5 } },
       { status: "failed", type: "waiver", adds: { b: 1 }, settings: { waiver_bid: 99 } }],
      [{ status: "complete", type: "free_agent", adds: { c: 1 } },
       { status: "complete", type: "waiver", adds: { d: 1 }, settings: { waiver_bid: 12 } },
       { status: "complete", type: "trade", roster_ids: [1, 2], adds: { e: 1, f: 2 } }],
    ];
    const m = Core.rosterMoves(txs);
    expect(m.adds.map(a => [a.p, a.bid, a.w])).toEqual([["d", 12, 2], ["a", 5, 1], ["c", 0, 2]]);
    expect(m.spent).toEqual([{ rid: 2, spent: 5 }, { rid: 1, spent: 12 }]);
    expect(m.trades).toEqual([{ w: 2, rosters: [1, 2], adds: { e: 1, f: 2 } }]);
  });
  it("counts Out and IR as injured but not Questionable", () => {
    expect(Core.INJURED).toContain("IR");
    expect(Core.INJURED).not.toContain("Questionable");
  });
});

describe("head-to-head", () => {
  const csv = [
    "season,week,is_playoffs,is_consolation,manager,team,points,opponent_manager,opponent_team,opponent_points,result",
    "2024,3,False,False,A,\"Team, A\",110,B,Bees,100,W",
    "2025,15,True,False,A,\"Team, A\",90,B,Bees,95,L",
    "2025,16,False,True,A,\"Team, A\",80,B,Bees,70,W",
    "2026,1,False,False,A,\"Team, A\",120,B,Bees,100,W",
  ].join("\n");
  const managers = { g1: { nicknames: ["Ann", "A"], real_name: "" }, g2: { nicknames: ["B"], real_name: "" } };
  it("parses quoted fields and numbers", () => {
    const rows = Core.parseCSV(csv);
    expect(rows[0]).toMatchObject({ season: 2024, team: "Team, A", points: 110, result: "W" });
  });
  it("maps every old name to one label and drops consolation games and the current season", () => {
    const raw = Core.h2hRawFrom(Core.parseCSV(csv), managers, "2026");
    expect(raw.alias).toMatchObject({ Ann: "A", A: "A", B: "B" });
    expect(raw.rows).toHaveLength(2);
  });
  it("joins saved history to this season's games", () => {
    const CUR = league();
    CUR._h2hRaw = Core.h2hRawFrom(Core.parseCSV(csv), managers, "2026");
    const h = Core.h2h(CUR, "A", "B");
    expect(h).toMatchObject({ w: 2, l: 1, pw: 0, pl: 1, n: 3, streak: "W1" });
    expect(Core.seriesLine(CUR, "A", "B")).toBe("A leads 2-1 all-time; B 1-0 in playoffs");
    expect(Core.rivalryChips(CUR, "A", "B")).toEqual([]);
  });
});

describe("canary model", () => {
  const Live = Core, Can = Core.canary;
  it("counts g/(g+14) of the all-play edge, in points", () => {
    // through week 3: league average 106.25 PPG, three games each, A all-play 1.000, B 0.375; 23.30 × √(2π) = 58.40
    const { rate } = Can.strengthThrough(league(), 3);
    expect(rate[1]).toBeCloseTo(106.25 + 58.4044 * 0.5 * 3 / 17, 3);
    expect(rate[1]).toBeCloseTo(111.4033, 3);
    expect(rate[2]).toBeCloseTo(104.9617, 3);
    expect(rate[4]).toBe(rate[2]);
  });
  it("ranks teams in power-board order", () => {
    const CUR = league(), { rate } = Can.strengthThrough(CUR, 3);
    const byRate = [...CUR._T].sort((a, b) => (rate[b.rid] - rate[a.rid]) || (b.pf - a.pf)).map(t => t.name);
    expect(byRate).toEqual([...CUR._T].sort(Core.byPower).map(t => t.name));
  });
  it("uses a 23.30-point weekly spread", () => {
    expect(Can.CONF(0)).toBeCloseTo(0.5);
    expect(Can.CONF(10)).toBeCloseTo(0.6192, 4);
  });
  it("picks the same favorites as the live model, less sure of them", () => {
    const live = Live.upcomingPicks(league()).picks, can = Can.upcomingPicks(league()).picks;
    expect(can.map(p => [p.fav, p.dog])).toEqual(live.map(p => [p.fav, p.dog]));
    expect(can[0].conf).toBeCloseTo(0.5775, 3);
    expect(live[0].conf).toBeGreaterThan(0.75);
  });
  it("adds up and is seeded, like the live odds", () => {
    const odds = Can.playoffOdds(league());
    expect(odds).toEqual(Can.playoffOdds(league()));
    expect(odds.reduce((a, o) => a + o.title, 0)).toBeCloseTo(1);
    expect(odds.reduce((a, o) => a + o.playoff, 0)).toBeCloseTo(2);
  });
});

describe("playoff bracket", () => {
  // seeds are 1-6; 6 upsets 3 and then 1, everything else goes to the better seed
  const upsets = { "3-6": 6, "1-6": 6, "2-6": 2 };
  const play = reseed => { const games = [];
    const champ = Core.playBracket([1, 2, 3, 4, 5, 6], 6, reseed, (a, b) => { games.push([a, b]); return upsets[`${Math.min(a, b)}-${Math.max(a, b)}`] ?? Math.min(a, b); });
    return { champ, games }; };
  it("lays out the standard slots", () => {
    expect(Core.bracketSlots(8)).toEqual([1, 8, 4, 5, 2, 7, 3, 6]);
  });
  it("keeps a fixed bracket: the 1 seed meets the 4/5 winner, the 2 seed the 3/6 winner", () => {
    const { champ, games } = play(false);
    expect(games).toEqual([[4, 5], [3, 6], [1, 4], [2, 6], [1, 2]]);
    expect(champ).toBe(1);
  });
  it("reseeds when asked: the 1 seed meets the lowest seed left", () => {
    const { champ, games } = play(true);
    expect(games).toEqual([[3, 6], [4, 5], [1, 6], [2, 4], [2, 6]]);
    expect(champ).toBe(2);
  });
  it("follows the league's seeding setting in the canary, always reseeds in the live model", () => {
    expect(Core.canary.model.reseed({ playoff_seed_type: 1 })).toBe(true);
    expect(Core.canary.model.reseed({ playoff_seed_type: 0 })).toBe(false);
    expect(Core.model.reseed({ playoff_seed_type: 0 })).toBe(true);
  });
});

describe("matchup of the week repeats", () => {
  const T = [["A", 0.9], ["B", 0.8], ["C", 0.85], ["D", 0.8], ["E", 0.2], ["F", 0.1]].map(([name, appct]) => ({ name, appct }));
  const AB = { a: "A", b: "B" }, CD = { a: "C", b: "D" }, EF = { a: "E", b: "F" };
  it("skips last week's team when a game within 0.5 has neither", () => {
    // A-B scores 3.30, C-D 3.25
    expect(Core.canary.spotlight(T, [AB, CD, EF], ["A", "X"])).toBe(CD);
    expect(Core.canary.spotlight(T, [AB, EF], ["A", "X"])).toBe(AB);
    expect(Core.spotlight(T, [AB, CD, EF], ["A", "X"])).toBe(AB);
  });
  it("replays last week's pick from the box scores", () => {
    // wk1 A-B (no data yet, so the first game), wk2 B-D, wk3 A-D: each week the only other game repeats a team too
    expect(Core.canary.spotlightLast(league())).toEqual(["A", "D"]);
    expect(Core.spotlightLast(league())).toBeNull();
  });
});

describe("history", () => {
  const NAMES = { 1: "A", 2: "B", 3: "C", 4: "D" };
  const rowsFrom = (season, weeks, is_playoffs = "False") => weeks.flatMap((m, i) => m.map(x => {
    const o = m.find(y => y.matchup_id === x.matchup_id && y !== x);
    return { season, week: i + 1, is_playoffs, manager: NAMES[x.roster_id], opponent_manager: NAMES[o.roster_id], points: x.points,
      opponent_points: o.points, result: x.points > o.points ? "W" : x.points < o.points ? "L" : "T" };
  }));
  it("replays saved seasons' picks the way pickRecord grades this one", () => {
    const rows = [...rowsFrom(2025, WEEKS.slice(0, 3)), ...rowsFrom(2025, [WEEKS[0]], "True")];
    const bt = Core.pickBacktest(rows), pr = Core.pickRecord(league());
    expect(bt).toMatchObject({ correct: 2, total: 3, seasons: [{ season: 2025, correct: 2, total: 3 }] });
    expect(bt.brier).toBeCloseTo(pr.brier, 10);
  });
  it("beats a coin flip and the live model over every saved season", () => {
    for (const lg of ["aggtown", "sobergang"]) {
      const rows = Core.parseCSV(readFileSync(new URL(`../data/combined/${lg}/all_weekly_scores.csv`, import.meta.url), "utf8"))
        .filter(r => r.is_consolation !== "True");
      const can = Core.canary.pickBacktest(rows).brier;
      expect(can).toBeLessThan(0.25);
      expect(can).toBeLessThan(Core.pickBacktest(rows).brier);
    }
  });
  it("compares starts only with seasons in the same format", () => {
    const rows = [...rowsFrom(2021, WEEKS.slice(0, 3)), ...rowsFrom(2025, WEEKS.slice(0, 3))];
    const rec = (season, manager, made, rank) => ({ season, manager, made_playoffs: made ? "True" : "False", final_rank: rank, regular_season_record: "x", playoff_seed: "" });
    const recs = [rec(2021, "A", 1, 2), rec(2021, "B", 1, 1), rec(2021, "C", 0, 4), rec(2021, "D", 1, 3),
                  rec(2025, "A", 1, 1), rec(2025, "B", 0, 3), rec(2025, "C", 0, 4), rec(2025, "D", 1, 2)];
    const starts = Core.historyStarts(rows, recs, 2);
    // through week 2: A 2-0 with a 6-0 all-play, C 0-2 and 0-6
    expect(starts).toHaveLength(8);
    expect(starts.find(s => s.season === 2025 && s.mgr === "A")).toMatchObject({ rec: "2-0", aw: 6, al: 0, playoffs: true, final_rank: 1, n_teams: 4, spots: 2 });
    expect(Core.startsLikeThese(starts, { n_teams: 4, spots: 2 })["2-0"]).toMatchObject({ n: 1, made_playoffs: 1, titles: 1, last: 0 });
    expect(Core.startsLikeThese(starts, { n_teams: 4, spots: 3 })["2-0"]).toMatchObject({ n: 1, made_playoffs: 1, titles: 0 });
    expect(Core.startsLikeThese(starts, { n_teams: 4, spots: 2 })["0-2"]).toMatchObject({ n: 1, made_playoffs: 0, last: 1 });
  });
});
