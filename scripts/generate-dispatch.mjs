#!/usr/bin/env node
/* ============================================================
   Weekly dispatch generator  (runs on GitHub Actions)
   - Pulls each league live from Sleeper (GitHub runners CAN reach it)
   - REUSES lib/almanac-core.js so every number matches the site and the PDF
   - Asks the Claude API to write the story column in the Almanac voice
   - Writes dispatches/<leagueId>/wk<week>.html  (index.html swaps it into the
     Dispatch tab's story column; the headline, tiles and sidebar stay live)
   Requires env:  ANTHROPIC_API_KEY
   Config:        dispatch.config.json  { "model": "...", "leagues": [{id,name}] }
   Optional env:  ONLY_LEAGUE=<id>   FORCE=1 (overwrite an existing week)
   ============================================================ */
import { createRequire } from "node:module";
import { readFile, writeFile, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
const require = createRequire(import.meta.url);
const Core = require("../lib/almanac-core.js");

const API = "https://api.sleeper.app/v1";
const KEY = process.env.ANTHROPIC_API_KEY;
if (!KEY) { console.error("Missing ANTHROPIC_API_KEY"); process.exit(1); }
const cfg = JSON.parse(await readFile(new URL("../dispatch.config.json", import.meta.url), "utf8"));
const MODEL = cfg.model || "claude-sonnet-5-5";
const LEAGUES = cfg.leagues || [];
const ONLY = process.env.ONLY_LEAGUE || "";
const j = async (u) => { const r = await fetch(u); if (!r.ok) throw new Error(u + " -> " + r.status); return r.json(); };
const n1 = (x) => Math.round(x * 10) / 10;

// Build the same CUR object index.html builds in load(), using the shared core.
async function buildCUR(id) {
  const [lg, users, rosters, state] = await Promise.all([
    j(`${API}/league/${id}`), j(`${API}/league/${id}/users`),
    j(`${API}/league/${id}/rosters`), j(`${API}/state/nfl`).catch(() => null)]);
  const rName = Core.teamNames(users, rosters);
  const pwk = (lg.settings && lg.settings.playoff_week_start) || 15;
  const all = await Promise.all(Array.from({ length: pwk - 1 }, (_, i) => j(`${API}/league/${id}/matchups/${i + 1}`).catch(() => null)));
  const { weeks, sched, upcoming, upWeek } = Core.splitWeeks(lg, state, all);
  const CUR = { lg, rName, rosters, weeks, sched, upcoming, upWeek, pwk, id };
  const { T, games, completed } = Core.compute(CUR);
  CUR._T = T; CUR._games = games; CUR._completed = completed;
  CUR._power = [...T].sort(Core.byPower);
  CUR._move = Core.powerMoves(CUR, CUR._power, completed);
  return CUR;
}

function brief(CUR, tops) {
  const { lg } = CUR, T = CUR._T, P = CUR._power, comp = CUR._completed, wk = comp[comp.length - 1];
  const rec = (t) => Core.recstr(t);
  const byRec = [...T].sort(Core.byRec);
  const byLuck = [...T].sort((a, b) => Core.luckWins(b) - Core.luckWins(a));
  const { unbeaten, winless } = Core.unbeatenWinless(T);
  const { top, heart, blow, close } = Core.gameHighs(CUR._games);
  const lo = Core.weeklyLows(CUR).find(x => x.wk === wk), hi = Core.weeklyHighs(CUR).find(x => x.wk === wk);
  const L = [];
  L.push(`LEAGUE: ${lg.name} | ${lg.season} | ${lg.total_rosters} teams | through Week ${wk}`);
  L.push(`\nSTANDINGS (record, PF, PA, all-play W-L, luck = wins above/below what the scores earned):`);
  byRec.forEach((t, i) => L.push(`${i + 1}. ${t.name}: ${rec(t)}, PF ${n1(t.pf)}, PA ${n1(t.pa)}, all-play ${t.aw}-${t.al}, luck ${n1(Core.luckWins(t))}`));
  L.push(`\nPOWER (by all-play, true strength): ${P.map((t, i) => `${i + 1}.${t.name}`).join("  ")}`);
  const movers = Object.entries(CUR._move).filter(([, d]) => d !== 0).sort((a, b) => b[1] - a[1]);
  if (movers.length) L.push(`MOVERS vs last week: ${movers.map(([n, d]) => `${n} ${d > 0 ? "+" + d : d}`).join(", ")}`);
  const lk = byLuck[0], rb = byLuck[byLuck.length - 1];
  L.push(`\nLUCKIEST: ${lk.name} (${rec(lk)}, all-play ${lk.aw}-${lk.al}, ${n1(Core.luckWins(lk))} wins above earned)`);
  L.push(`MOST ROBBED: ${rb.name} (${rec(rb)}, all-play ${rb.aw}-${rb.al}, ${n1(Core.luckWins(rb))})`);
  if (unbeaten.length) L.push(`UNBEATEN: ${unbeaten.map(t => t.name + " " + rec(t)).join(", ")}`);
  if (winless.length) L.push(`WINLESS: ${winless.map(t => t.name + " " + rec(t)).join(", ")}`);
  if (top) L.push(`\nSEASON HIGH: ${top.hi} ${n1(top.hip)} (wk ${top.wk})`);
  if (blow) L.push(`BIGGEST BLOWOUT: ${blow.hi} ${n1(blow.hip)} over ${blow.lo} ${n1(blow.lop)} (wk ${blow.wk})`);
  if (heart) L.push(`WORST BAD BEAT: ${heart.lo} scored ${n1(heart.lop)} and still lost to ${heart.hi} (wk ${heart.wk})`);
  if (close) L.push(`CLOSEST GAME: ${close.hi} ${n1(close.hip)}-${n1(close.lop)} ${close.lo} (wk ${close.wk})`);
  if (hi) L.push(`WEEK ${wk} HIGH: ${hi.names.join(" & ")} ${n1(hi.p)}`);
  if (lo) L.push(`WEEK ${wk} LOW: ${lo.names.join(" & ")} ${n1(lo.p)}`);
  if (tops && tops.length) L.push(`\nTOP PERFORMERS (season, 30+ pt starts): ${tops.slice(0, 6).map(t => `${t.pl} (${t.tm}) ${n1(t.pts)} in wk${t.wk}`).join(" · ")}`);
  if (CUR.upcoming && CUR.upcoming.length) {
    const bm = {}; CUR.upcoming.forEach(x => { (bm[x.matchup_id] = bm[x.matchup_id] || []).push(x); });
    const pairs = []; for (const k in bm) { const [a, b] = bm[k]; if (a && b) pairs.push(`${CUR.rName[a.roster_id]} vs ${CUR.rName[b.roster_id]}`); }
    if (pairs.length) L.push(`\nUPCOMING Week ${CUR.upWeek}: ${pairs.join(" | ")}`);
  }
  return L.join("\n");
}

const SYSTEM = `You write the main story column of "The League Almanac" front page — a weekly fantasy football dispatch read by the managers of a private league who have known each other for years. The page already shows the week's headline and the stat tiles ABOVE your column, so don't just re-announce the top score — dive into the storylines with a take. Your job is to ENTERTAIN and STIR THE POT: a column people screenshot into the group chat and argue about. Think Bill Simmons running a roast.

VOICE:
- Be genuinely funny. Bits, running gags, nicknames, callbacks, overblown metaphors, hot takes.
- Weave the numbers INTO jokes and storylines. Never recite a stat line like a box score. Every number should serve a jab, a bit, or an argument.
- Take sides. Declare frauds, anoint victims, pick fights. Call people out BY NAME and dare them to prove you wrong.
- Go for the jugular. This is a group of adults who love roasting each other — be savage, be merciless, let it fly. If one manager's week is a train wreck, spend the column on them. No need to be even-handed.
- Vary sentence length. Land jokes on short punchy lines. One devastating burn beats three mild ones.

HARD RULES:
- Return ONLY an HTML fragment for the story column: <h3> subheads (funny titles, not "Standings") and <p> paragraphs, <b> for emphasis. No <html>/<head>/<style>, no markdown, no code fences, no outer <article> wrapper.
- 6 to 9 paragraphs under 3-4 <h3> segments. Go in depth. ALWAYS finish cleanly; never stop mid-sentence. End with a forward look at next week and a dare or prediction.
- Use ONLY the REAL names and REAL numbers from the data. Never invent players, scores, injuries, trades, or history you weren't given.
- The luck gap (record vs all-play) is your best comedy material — lucky frauds with shiny records, unlucky victims getting robbed. Name the riser, the faller, and the cellar team.
- Trash talk: no holds barred on fantasy football — lineup decisions, draft reaches, bad beats, cowardly matchups. The ONE line you never cross: no slurs and no jokes built on someone's race, religion, sexuality, gender, or disability. Everything else is fair game.
- If a "LEAGUE LORE" section is provided, treat it as true real-world context about these managers and LEAN INTO IT — it's the inside-baseball the box scores can't show. Work it into the roast naturally; it's often the funniest material you've got.

Output the HTML fragment and nothing else.`;

async function callModel(messages) {
  const res = await fetch("https://api.anthropic.com/v1/messages", {
    method: "POST",
    headers: { "x-api-key": KEY, "anthropic-version": "2023-06-01", "content-type": "application/json" },
    body: JSON.stringify({ model: MODEL, max_tokens: 4096, system: SYSTEM, messages })
  });
  if (!res.ok) throw new Error("Anthropic API " + res.status + ": " + (await res.text()).slice(0, 300));
  const d = await res.json();
  return { text: (d.content || []).map(c => c.text || "").join(""), stop: d.stop_reason };
}
async function writeDispatch(dataBrief) {
  const messages = [{ role: "user", content: "Write this week's dispatch story column from this data:\n\n" + dataBrief }];
  let full = "";
  for (let i = 0; i < 3; i++) {  // auto-continue if the model ever hits the token ceiling
    const { text, stop } = await callModel(messages);
    full += text;
    if (stop !== "max_tokens") break;
    messages.push({ role: "assistant", content: text });
    messages.push({ role: "user", content: "Continue from exactly where you stopped. Do not repeat any text. Finish the piece cleanly with a forward look at next week." });
  }
  return full.replace(/^```html\s*/i, "").replace(/```$/, "").trim();
}

let wrote = 0;
for (const L of LEAGUES) {
  if (ONLY && L.id !== ONLY) continue;
  try {
    const CUR = await buildCUR(L.id);
    if (!CUR._completed.length) { console.log(`${L.name}: no completed weeks yet, skipping.`); continue; }
    const week = CUR._completed[CUR._completed.length - 1];
    const outPath = new URL(`../dispatches/${L.id}/wk${week}.html`, import.meta.url);
    if (existsSync(outPath) && !process.env.FORCE) { console.log(`${L.name}: wk${week} already exists, skipping (FORCE=1 to overwrite).`); continue; }
    let tops = [];
    try { const PLAYERS = await j(`${API}/players/nfl`); tops = Core.topPerformances(CUR.weeks).map(t => ({ pl: Core.nameOf(PLAYERS, t.p), tm: CUR.rName[t.rid], wk: t.wk, pts: t.pts })); } catch (e) { /* flavor only */ }
    let dataBrief = brief(CUR, tops);
    if (L.context) dataBrief += `\n\nLEAGUE LORE (real context — weave it in and lean into it):\n${L.context}`;
    const html = await writeDispatch(dataBrief);
    if (!html) { console.log(`${L.name}: model returned empty, skipping.`); continue; }
    await mkdir(new URL(`../dispatches/${L.id}/`, import.meta.url), { recursive: true });
    await writeFile(outPath, html + "\n", "utf8");
    console.log(`${L.name}: wrote dispatches/${L.id}/wk${week}.html (${html.length} chars)`);
    wrote++;
  } catch (e) {
    console.error(`${L.name}: FAILED — ${e.message}`);
  }
}
console.log(`\nDone. Wrote ${wrote} dispatch file(s).`);
if (process.env.GITHUB_OUTPUT) await writeFile(process.env.GITHUB_OUTPUT, `wrote=${wrote}\n`, { flag: "a" });
