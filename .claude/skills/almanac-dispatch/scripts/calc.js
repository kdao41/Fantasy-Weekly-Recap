// Every current-season number the dispatch uses, computed by lib/almanac-core.js, the same code index.html runs.
// Change a calculation there and the site and the next PDF both follow.
// usage: node calc.js <repo_dir> <live_dir> <league> > site.json      (<live_dir> from fetch_live.py)
const fs = require("fs"), path = require("path");
const [REPO, LIVE, LEAGUE] = process.argv.slice(2);
const Core = require(path.resolve(REPO, "lib/almanac-core.js"));
const J = p => JSON.parse(fs.readFileSync(p, "utf8"));
const D = path.join(LIVE, LEAGUE), u = Core.unesc;

// the same league object index.html's load() builds
const lg = J(`${D}/league.json`), users = J(`${D}/users.json`), rosters = J(`${D}/rosters.json`), state = J(`${D}/state.json`);
const pwk = lg.settings.playoff_week_start || 15;
const all = Array.from({length: pwk - 1}, (_, i) => { const p = `${D}/m${i + 1}.json`; return fs.existsSync(p) ? J(p) : null; });
const CUR = {lg, rName: Core.teamNames(users, rosters), rosters, ...Core.splitWeeks(lg, state, all), pwk, id: lg.league_id};
const {T, games, completed} = Core.compute(CUR);
Object.assign(CUR, {_T: T, _games: games, _completed: completed});
const power = [...T].sort(Core.byPower);
CUR._power = power; CUR._move = Core.powerMoves(CUR, power, completed);

// saved history, as loadH2H() reads it
const L = J(`${REPO}/data/leagues.json`).leagues.find(l => l.id === LEAGUE);
const base = `${REPO}/data/combined/${L.id}/`;
CUR._h2hRaw = Core.h2hRawFrom(Core.parseCSV(fs.readFileSync(base + "all_weekly_scores.csv", "utf8")), J(base + "managers.json"), lg.season);

// "teams that started like this", counted only in seasons with this league's teams and playoff spots
const starts = Core.historyStarts(CUR._h2hRaw.rows, Core.parseCSV(fs.readFileSync(base + "manager_season_records.csv", "utf8")), completed.length);
const startsFormat = {n_teams: T.length, spots: Core.playoffSpots(CUR)};

const PLAYERS = J(`${LIVE}/players.json`);
const ppos = p => Core.positionOf(PLAYERS, p);
const last = completed[completed.length - 1];
const rate = last ? Core.strengthThrough(CUR, last).rate : {};
const odds = {};
Core.playoffOdds(CUR).forEach(o => odds[u(o.name)] = {playoffs: o.playoff, seed1: o.top, title: o.title});
const series = (a, b) => { const H = Core.h2h(CUR, a, b);
  return {w: H.w, l: H.l, t: H.t, n: H.n, pw: H.pw, pl: H.pl, pf: H.pf, pa: H.pa, streak: H.streak, last: H.last,
          line: u(Core.seriesLine(CUR, a, b)), chips: Core.rivalryChips(CUR, a, b).map(c => u(c.t))}; };
const pairs = {}, names = T.map(t => t.name);
names.forEach((a, i) => names.slice(i + 1).forEach(b => { pairs[`${u(a)} | ${u(b)}`] = series(a, b); }));
const spot = Core.spotlight(T, Core.matchupPairs(CUR), Core.spotlightLast(CUR));
const up = (Core.upcomingPicks(CUR) || {picks: []}).picks;
const pr = Core.pickRecord(CUR);
const txs = Array.from({length: pwk - 1}, (_, i) => { const p = `${D}/t${i + 1}.json`; return fs.existsSync(p) ? J(p) : []; });
const moves = Core.rosterMoves(txs);
const mvps = Core.seasonMvps(CUR);
const team = rid => u(CUR.rName[rid]);
// names, positions and injury tags for every player the issue can mention, as the site shows them
const pids = new Set([...rosters.flatMap(r => r.players || []), ...J(`${D}/picks.json`).map(p => p.player_id),
  ...Object.values(CUR.weeks).flat().flatMap(x => Object.keys(x.players_points || {})), ...moves.adds.map(a => a.p)]);
const players = Object.fromEntries([...pids].map(p => [p, {name: Core.nameOf(PLAYERS, p), pos: ppos(p), injury: Core.injuryOf(PLAYERS, p),
  injury_body_part: (PLAYERS[p] || {}).injury_body_part || null, injury_notes: (PLAYERS[p] || {}).injury_notes || null}]));

process.stdout.write(JSON.stringify({
  league: lg.name, season: +lg.season, league_id: CUR.id, completed, up_week: CUR.upWeek,
  playoff_week_start: pwk, playoff_spots: Core.playoffSpots(CUR), trade_deadline: lg.settings.trade_deadline,
  teams: T.map(t => ({rid: +t.rid, name: u(t.name), w: t.w, l: t.l, t: t.t, pf: t.pf, pa: t.pa, aw: t.aw, al: t.al,
    appct: t.appct, winpct: t.winpct, pfg: t.pfg, luck: Core.luckWins(t), rating: rate[t.rid],
    scores: t.scores.map(s => s.p), log: t.log.map(g => ({wk: g.wk, p: g.p, opp: u(g.opp), op: g.op, res: g.res}))})),
  power: power.map(t => u(t.name)),
  power_move: Object.fromEntries(Object.entries(CUR._move).map(([k, v]) => [u(k), v])),
  odds,
  coach: Core.rateCoaches(Core.coachRows(CUR, ppos) || []).map(r => ({name: u(r.name), scored: r.act, best: r.opt, benched: r.left, eff: r.eff})),
  games: games.map(g => ({wk: g.wk, win: u(g.hi), lose: u(g.lo), wp: g.hip, lp: g.lop})),
  spotlight: spot ? [u(spot.a), u(spot.b)] : [],
  next_week: up.map(p => ({fav: u(p.fav), dog: u(p.dog), conf: p.conf, h2h: series(p.fav, p.dog)})),
  h2h_all: pairs,
  pick_record: {correct: pr.correct, total: pr.total, brier: pr.brier},
  starts,
  starts_format: {...startsFormat, seasons: [...new Set(starts.filter(s => s.n_teams === startsFormat.n_teams && s.spots === startsFormat.spots).map(s => s.season))]},
  starts_like_these: Core.startsLikeThese(starts, startsFormat),
  player_points: Core.playerPoints(CUR.weeks),
  season_mvps: Object.fromEntries(Object.entries(mvps).map(([rid, m]) => [team(rid), m])),
  top_performances: Core.topPerformances(CUR.weeks).map(t => ({p: t.p, team: team(t.rid), wk: t.wk, pts: t.pts})),
  injured_statuses: Core.INJURED,
  moves: {trades: moves.trades.map(t => ({w: t.w, teams: t.rosters.map(team), adds: Object.fromEntries(Object.entries(t.adds).map(([p, r]) => [p, team(r)]))})),
          adds: moves.adds.map(a => ({w: a.w, team: team(a.rid), p: a.p, bid: a.bid})),
          spent: moves.spent.map(x => ({team: team(x.rid), spent: x.spent}))},
  flex: Core.FLEX,
  players,
}) + "\n");
