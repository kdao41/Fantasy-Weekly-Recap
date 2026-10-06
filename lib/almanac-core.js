// The League Almanac's calculations, shared by index.html (loaded with <script src>), the PDF dispatch
// skill and the unit tests in tests/ (both load it with require in Node). Functions that need league state take it as their first argument,
// `CUR`: the same object index.html builds in load(), with rName, weeks, sched, upcoming, upWeek, pwk, id,
// lg, rosters, and after compute() the derived _T, _games, _completed, _h2hRaw.
// No DOM, no fetch: anything here must run unchanged in both places.
// AlmanacCore is the live model. AlmanacCore.canary is the same code with the proposed settings (MODELS.canary),
// shown on the site behind a switch until it's promoted; docs/almanac-audit.md has the backtest behind it.
const AlmanacCore=(()=>{
// Weekly scores swing about 23.30 points around a team's level while true levels differ by only 4 to 9, so the
// canary counts g/(g+14) of the edge a team has shown after g games. 23.30 × √(2π) turns all-play % into points
// for normally spread scores.
const CANARY_SD=23.3,CANARY_K=14;
const MODELS={
  live:{name:"live",sd:27,rate:(mean,s)=>0.62*s.pfg+0.38*(mean+(s.appct-0.5)*55),
    simMu:(m,mean)=>0.82*m+0.18*mean,reseed:()=>true,repeatGap:null,boldCalls:true,upsetConf:.7},
  canary:{name:"canary",sd:CANARY_SD,rate:(mean,s)=>mean+CANARY_SD*Math.sqrt(2*Math.PI)*(s.appct-0.5)*s.g/(s.g+CANARY_K),
    // Sleeper's bracket is fixed (1 seed meets the 4/5 winner) unless the league picked re-seeding
    simMu:null,reseed:st=>st.playoff_seed_type===1,
    // matchup of the week skips last week's teams when a game within 0.5 of the best one has neither
    repeatGap:0.5,boldCalls:false,
    // the Dispatch leads with an upset when the beaten favourite was this sure. The canary's chances run closer to
    // 50% and never reach .70; .56 keeps about the same share of past picks eligible (22% against the live 19%).
    upsetConf:.56},
};
function build(M){
// Team names are escaped once when loaded (rName), so they can go straight into HTML everywhere.
const esc=s=>String(s??"").replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
// Undoes exactly what esc does.
const unesc=s=>String(s).replace(/&quot;/g,'"').replace(/&gt;/g,">").replace(/&lt;/g,"<").replace(/&amp;/g,"&");
const nameOf=(PLAYERS,p)=>{if(PLAYERS&&PLAYERS[p]){const x=PLAYERS[p];return x.full_name||((x.first_name||"")+" "+(x.last_name||"")).trim()||p;}return /^[A-Z]{2,4}$/.test(p)?p+" DST":p;};
const positionOf=(PLAYERS,p)=>{if(PLAYERS&&PLAYERS[p])return (PLAYERS[p].fantasy_positions&&PLAYERS[p].fantasy_positions[0])||PLAYERS[p].position;return /^[A-Z]{2,4}$/.test(p)?"DEF":null;};
const injuryOf=(PLAYERS,p)=>PLAYERS&&PLAYERS[p]?PLAYERS[p].injury_status:null;

// Seeded so the playoff odds don't wobble between refreshes of the same week.
function rng(seed){let a=0;for(const c of String(seed))a=(a*31+c.charCodeAt(0))|0;
  return ()=>{a=(a+0x6D2B79F5)|0;let t=Math.imul(a^a>>>15,1|a);t=t+Math.imul(t^t>>>7,61|t)^t;return ((t^t>>>14)>>>0)/4294967296;};}
function erf(x){const t=1/(1+0.3275911*Math.abs(x));const y=1-(((((1.061405429*t-1.453152027)*t)+1.421413741)*t-0.284496736)*t+0.254829592)*t*Math.exp(-x*x);return x>=0?y:-y;}
const normcdf=z=>0.5*(1+erf(z/Math.SQRT2));
const FLEX={FLEX:["RB","WR","TE"],WRRB_FLEX:["RB","WR"],REC_FLEX:["WR","TE"],SUPER_FLEX:["QB","RB","WR","TE"],IDP_FLEX:["DL","LB","DB"]};
function bestLineup(slots,pp,ppos){
  const pool=Object.keys(pp).filter(p=>pp[p]!=null&&ppos(p));
  const used=new Set();let tot=0;
  const order=slots.map((s,i)=>[s,i]).filter(([s])=>!["BN","IR","TAXI"].includes(s)).sort((a,b)=>(FLEX[a[0]]?1:0)-(FLEX[b[0]]?1:0));
  for(const [slot] of order){const ok=FLEX[slot]||[slot];let pick=null,best=-1e9;
    for(const p of pool){if(used.has(p))continue;if(!ok.includes(ppos(p)))continue;if((pp[p]||0)>best){best=pp[p]||0;pick=p;}}
    if(pick){used.add(pick);tot+=best;}}
  return tot;
}
// Sleeper moves state.week on to the next week once Monday night ends, so any earlier week is final
// and state.week itself is either upcoming or being played right now.
function isFinal(lg,state,w){
  if(!state||lg.season!==state.season||state.season_type!=="regular")return true;
  return w<state.week;
}
function compute(CUR){
  const {rName,weeks,pwk}=CUR;
  const ids=Object.keys(rName);
  const S={}; ids.forEach(r=>S[r]={rid:r,name:rName[r],w:0,l:0,t:0,pf:0,pa:0,aw:0,al:0,scores:[],log:[]});
  const games=[]; // {wk,hi,lo,hip,lop}
  const completed=Object.keys(weeks).map(Number).sort((a,b)=>a-b);
  for(const w of completed){
    const m=weeks[w];
    const sc=m.map(x=>({r:x.roster_id,p:x.points||0}));
    sc.forEach(a=>sc.forEach(b=>{if(a.r!==b.r){if(a.p>b.p)S[a.r].aw++;else if(a.p<b.p)S[a.r].al++;}}));
    m.forEach(x=>S[x.roster_id].scores.push({wk:w,p:x.points||0}));
    const bm={};m.forEach(x=>{(bm[x.matchup_id]=bm[x.matchup_id]||[]).push(x);});
    for(const k in bm){const [a,b]=bm[k];if(!a||!b)continue;const ap=a.points||0,bp=b.points||0;
      S[a.roster_id].pf+=ap;S[a.roster_id].pa+=bp;S[b.roster_id].pf+=bp;S[b.roster_id].pa+=ap;
      if(ap>bp){S[a.roster_id].w++;S[b.roster_id].l++;}else if(bp>ap){S[b.roster_id].w++;S[a.roster_id].l++;}else{S[a.roster_id].t++;S[b.roster_id].t++;}
      const res=(x,y)=>x>y?"W":x<y?"L":"T";
      S[a.roster_id].log.push({wk:w,p:ap,opp:rName[b.roster_id],op:bp,res:res(ap,bp)});
      S[b.roster_id].log.push({wk:w,p:bp,opp:rName[a.roster_id],op:ap,res:res(bp,ap)});
      const hi=ap>=bp?a:b,lo=ap>=bp?b:a;
      games.push({wk:w,hi:rName[hi.roster_id],lo:rName[lo.roster_id],hip:Math.max(ap,bp),lop:Math.min(ap,bp)});}
  }
  const T=ids.map(r=>{const s=S[r];const g=s.w+s.l+s.t;const ap=s.aw+s.al;
    return {...s,g,gp:completed.length,winpct:g?(s.w+0.5*s.t)/g:0,appct:ap?s.aw/ap:0,pfg:completed.length?s.pf/completed.length:0};});
  return {T,games,completed};
}
// Playoff sim: plays out the real remaining schedule (random pairings only where Sleeper hasn't posted one).
function simulate(CUR,T,regWeeks,completed,spots,N){
  const n=T.length,rand=rng(CUR.id+":"+completed);
  const mu=T.map(t=>M.rate(meanPF(T),t));
  if(M.simMu){const mean=mu.reduce((a,b)=>a+b,0)/n; for(let i=0;i<n;i++)mu[i]=M.simMu(mu[i],mean);}
  const reseed=M.reseed((CUR.lg&&CUR.lg.settings)||{});
  const W0=T.map(t=>t.w+0.5*t.t), PF0=T.map(t=>t.pf);
  const at={};T.forEach((t,i)=>at[t.rid]=i);
  const future=[];
  for(let w=completed+1;w<=regWeeks;w++){const m=CUR.sched[w];const bm={};
    (m||[]).forEach(x=>{if(x.matchup_id!=null)(bm[x.matchup_id]=bm[x.matchup_id]||[]).push(at[x.roster_id]);});
    const pairs=Object.values(bm).filter(p=>p.length===2);
    future.push(pairs.length?pairs:null);}
  let po=new Array(n).fill(0), ti=new Array(n).fill(0), s1=new Array(n).fill(0);
  const SD=M.sd;
  const rnd=()=>{let u=0,v=0;while(!u)u=rand();while(!v)v=rand();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);};
  const shuffledPairs=()=>{const idx=[...Array(n).keys()];for(let i=n-1;i>0;i--){const k=Math.floor(rand()*(i+1));[idx[i],idx[k]]=[idx[k],idx[i]];}
    const out=[];for(let i=0;i+1<n;i+=2)out.push([idx[i],idx[i+1]]);return out;};
  for(let s=0;s<N;s++){
    const w=W0.slice(),pf=PF0.slice();
    for(const wk of future){
      const sc=mu.map(m=>m+SD*rnd());
      for(const [a,b] of (wk||shuffledPairs())){if(sc[a]>sc[b])w[a]++;else w[b]++;pf[a]+=sc[a];pf[b]+=sc[b];}
    }
    const order=[...Array(n).keys()].sort((a,b)=>(w[b]-w[a])||(pf[b]-pf[a]));
    const seeds=order.slice(0,spots); seeds.forEach(i=>po[i]++); s1[order[0]]++;
    const game=(a,b)=>((mu[a]+SD*rnd())>(mu[b]+SD*rnd()))?a:b;
    ti[playBracket(seeds,spots,reseed,game)]++;
  }
  return T.map((t,i)=>({name:t.name,playoff:po[i]/N,title:ti[i]/N,top:s1[i]/N}));
}
// One playoff bracket; returns the champion. game(a,b) returns the winner. The top nextPow2(spots)-spots seeds
// get byes. Reseeded: each round pairs best vs worst remaining. Fixed: winners stay in their slots.
function playBracket(seeds,spots,reseed,game){
  if(!reseed){
    let field=bracketSlots(nextPow2(spots)).map(k=>k<=spots?seeds[k-1]??null:null);
    while(field.length>1){const nx=[];for(let i=0;i<field.length;i+=2){const a=field[i],b=field[i+1];nx.push(a==null?b:b==null?a:game(a,b));}field=nx;}
    return field[0];
  }
  const byes=nextPow2(spots)-spots;
  let active=seeds.slice(byes), bench=seeds.slice(0,byes);
  while(active.length+bench.length>1){
    let winners=[];
    for(let i=0;i<active.length/2;i++){winners.push(game(active[i],active[active.length-1-i]));}
    let pool=bench.concat(winners);
    pool.sort((a,b)=>seeds.indexOf(a)-seeds.indexOf(b));
    active=pool; bench=[];
    if(active.length===1)break;
  }
  return active[0];
}
// Standard bracket order, so seeds 1 and 2 can only meet in the final: bracketSlots(8) is 1,8,4,5,2,7,3,6.
function bracketSlots(P){let s=[1];while(s.length<P){const m=s.length*2+1;s=s.flatMap(x=>[x,m-x]);}return s;}
function meanPF(T){return T.reduce((a,b)=>a+b.pfg,0)/T.length;}
function nextPow2(n){let p=1;while(p<n)p*=2;return p;}
function statsThrough(CUR,cut){
  const {rName,weeks}=CUR; const ids=Object.keys(rName);
  const S={}; ids.forEach(r=>S[r]={w:0,l:0,t:0,pf:0,g:0,aw:0,al:0});
  const wks=Object.keys(weeks).map(Number).filter(w=>w<=cut).sort((a,b)=>a-b);
  for(const w of wks){
    const m=weeks[w];
    const sc=m.map(x=>({r:x.roster_id,p:x.points||0}));
    sc.forEach(a=>sc.forEach(b=>{if(a.r!==b.r){if(a.p>b.p)S[a.r].aw++;else if(a.p<b.p)S[a.r].al++;}}));
    const bm={};m.forEach(x=>{(bm[x.matchup_id]=bm[x.matchup_id]||[]).push(x);});
    for(const k in bm){const [a,b]=bm[k];if(!a||!b)continue;const ap=a.points||0,bp=b.points||0;
      S[a.roster_id].pf+=ap;S[b.roster_id].pf+=bp;S[a.roster_id].g++;S[b.roster_id].g++;
      if(ap>bp){S[a.roster_id].w++;S[b.roster_id].l++;}else if(bp>ap){S[b.roster_id].w++;S[a.roster_id].l++;}else{S[a.roster_id].t++;S[b.roster_id].t++;}}
  }
  const out={};
  ids.forEach(r=>{const s=S[r];const ap=s.aw+s.al;
    out[r]={...s,pfg:s.g?s.pf/s.g:0,winpct:s.g?(s.w+0.5*s.t)/s.g:0,appct:ap?s.aw/ap:0};});
  return out;
}
function strengthThrough(CUR,cut){
  const st=statsThrough(CUR,cut); const ids=Object.keys(st);
  const mean=ids.reduce((a,r)=>a+st[r].pfg,0)/ids.length;
  const rate={}; ids.forEach(r=>{rate[r]=M.rate(mean,st[r]);});
  return {rate,st};
}
function weekPairs(CUR,w){
  const m=CUR.weeks[w]; if(!m)return [];
  const bm={};m.forEach(x=>{(bm[x.matchup_id]=bm[x.matchup_id]||[]).push(x);});
  const out=[]; for(const k in bm){const [a,b]=bm[k];if(a&&b)out.push({a:a.roster_id,b:b.roster_id,ap:a.points||0,bp:b.points||0});}
  return out;
}
const CONF=gap=>normcdf(gap/(M.sd*Math.SQRT2)); // P(favorite wins), from the model's weekly scoring SD
function pickRecord(CUR){
  const {rName,weeks}=CUR;
  const comp=Object.keys(weeks).map(Number).sort((a,b)=>a-b);
  const perWeek=[]; let correct=0,total=0,brierSum=0;
  for(const w of comp){ if(w<=comp[0])continue; // week 1 has no prior data to pick from
    const {rate}=strengthThrough(CUR,w-1); const picks=[];
    weekPairs(CUR,w).forEach(p=>{
      const fav=rate[p.a]>=rate[p.b]?p.a:p.b, dog=fav===p.a?p.b:p.a;
      const conf=CONF(Math.abs(rate[p.a]-rate[p.b]));
      const aw=p.ap===p.bp?null:(p.ap>p.bp?p.a:p.b);
      const hit=aw===null?null:aw===fav;
      if(hit!==null){total++; if(hit)correct++; brierSum+=Math.pow(conf-(hit?1:0),2);}
      picks.push({fav:rName[fav],dog:rName[dog],conf,hit,
        favScore:fav===p.a?p.ap:p.bp, dogScore:dog===p.a?p.ap:p.bp});
    });
    perWeek.push({wk:w,picks});
  }
  return {correct,total,perWeek,brier:total?brierSum/total:null};
}
function upcomingPicks(CUR){
  if(!CUR.upcoming||!CUR.upcoming.length)return null;
  const comp=Object.keys(CUR.weeks).map(Number); if(!comp.length)return null;
  const {rate}=strengthThrough(CUR,Math.max(...comp));
  const {rName,upcoming,upWeek}=CUR;
  const bm={};upcoming.forEach(x=>{(bm[x.matchup_id]=bm[x.matchup_id]||[]).push(x);});
  const picks=[];
  for(const k in bm){const [a,b]=bm[k];if(!a||!b)continue;
    const ra=rate[a.roster_id],rb=rate[b.roster_id];
    const fav=ra>=rb?a.roster_id:b.roster_id, dog=fav===a.roster_id?b.roster_id:a.roster_id;
    picks.push({fav:rName[fav],dog:rName[dog],conf:CONF(Math.abs(ra-rb))});}
  picks.sort((x,y)=>y.conf-x.conf);
  return {week:upWeek,picks};
}
function recstr(t){return `${t.w}-${t.l}${t.t?('-'+t.t):''}`;}
const luckWins=t=>(t.w+t.t/2)-t.appct*t.g; // actual wins minus the wins your scores earned (all-play % x games)
// Record of team a against team b (live, escaped names). Consolation games don't count, as in the saved standings.
function h2h(CUR,a,b){
  const R=CUR._h2hRaw,out={w:0,l:0,t:0,pw:0,pl:0,pf:0,pa:0,games:[]};
  if(R){const la=R.alias[unesc(a)],lb=R.alias[unesc(b)];
    if(la&&lb)R.rows.forEach(r=>{if(r.manager!==la||r.opponent_manager!==lb)return;
      out.games.push({season:+r.season,wk:+r.week,p:+r.points,op:+r.opponent_points,res:r.result,po:r.is_playoffs==="True"});});}
  const T=CUR._T.find(t=>t.name===a);
  if(T)T.log.forEach(g=>{if(g.opp===b)out.games.push({season:+CUR.lg.season,wk:g.wk,p:g.p,op:g.op,res:g.res,po:false});});
  out.games.sort((x,y)=>(x.season-y.season)||(x.wk-y.wk));
  out.games.forEach(g=>{out[g.res==="W"?"w":g.res==="L"?"l":"t"]++;if(g.po){if(g.res==="W")out.pw++;else if(g.res==="L")out.pl++;}out.pf+=g.p;out.pa+=g.op;});
  out.n=out.games.length;out.last=out.games[out.n-1]||null;
  let k=0;for(let i=out.n-1;i>=0&&out.games[i].res===out.last.res;i--)k++;out.streak=out.last?`${out.last.res}${k}`:"";
  return out;
}
const recH=h=>`${h.w}-${h.l}${h.t?"-"+h.t:""}`;
function seriesLine(CUR,a,b){const h=h2h(CUR,a,b);
  if(!h.n)return "First meeting";
  const lead=h.w>h.l?`${a} leads`:h.l>h.w?`${b} leads`:"Series tied";
  const s=h.w>=h.l?recH(h):`${h.l}-${h.w}${h.t?"-"+h.t:""}`;
  if(!(h.pw+h.pl))return `${lead} ${s} all-time`;
  // playoff split from the side that leads it, named, so it can't be read as the other team's
  const [pn,pw,pl]=h.pw>=h.pl?[a,h.pw,h.pl]:[b,h.pl,h.pw];
  return `${lead} ${s} all-time; ${pn} ${pw}-${pl} in playoffs`;}
// Each person's nemesis (worst record, 4+ games), punching bag (best record, 4+ games) and current streaks, from the saved history.
function rivalsOf(CUR,lab){
  CUR._G=CUR._G||histGames(CUR);
  const games=CUR._G[lab]||[],opp={};
  games.forEach(g=>{const o=opp[g.opp]=opp[g.opp]||{w:0,l:0,n:0};o.n++;if(g.res==="W")o.w++;else if(g.res==="L")o.l++;});
  const opps=Object.entries(opp).filter(([,o])=>o.n>=4).map(([k,o])=>({k,...o,p:o.w/o.n}));
  const nem=[...opps].sort((a,b)=>a.p-b.p||b.n-a.n)[0],bag=[...opps].sort((a,b)=>b.p-a.p||b.n-a.n)[0];
  return {nem:nem&&nem.p<.5?nem:null,bag:bag&&bag.p>.5?bag:null,opp};
}
// Story chips for one pairing: nemesis / punching bag from either side, playoff history, dead even, streaks, first meeting.
function rivalryChips(CUR,a,b){
  if(!CUR._h2hRaw)return [];
  const al=CUR._h2hRaw.alias,la=al[unesc(a)]||unesc(a),lb=al[unesc(b)]||unesc(b),H=h2h(CUR,a,b),out=[];
  if(!H.n)return [{t:"🆕 First meeting"}];
  const ra=rivalsOf(CUR,la),rb=rivalsOf(CUR,lb);
  // "B is A's nemesis" and "A is B's punching bag" tell the same story, so show at most one per side of the series
  const tags=[ra.nem&&ra.nem.k===lb&&{t:`😈 ${b} is ${a}'s nemesis`,c:"hot",side:b},rb.nem&&rb.nem.k===la&&{t:`😈 ${a} is ${b}'s nemesis`,c:"hot",side:a},
    ra.bag&&ra.bag.k===lb&&{t:`🥊 ${b} is ${a}'s punching bag`,c:"own",side:a},rb.bag&&rb.bag.k===la&&{t:`🥊 ${a} is ${b}'s punching bag`,c:"own",side:b}].filter(Boolean);
  const owner=new Set();tags.forEach(x=>{if(!owner.has(x.side)){owner.add(x.side);out.push(x);}});
  if(H.pw+H.pl>=2)out.push({t:`🔥 ${H.pw+H.pl} playoff meetings`});
  if(H.n>=8&&H.w===H.l)out.push({t:"⚖️ Dead even"});
  const k=+H.streak.slice(1);
  if(k>=3)out.push({t:`📈 ${H.streak[0]==="W"?a:b} has won ${k} straight`});
  return out;
}
// Sleeper stores each roster's season points (fpts) and best-possible-lineup points (ppts), so use those.
// Older leagues without ppts fall back to rebuilding the best lineup each week, which needs player positions.
function coachRows(CUR,ppos){
  const dec=(a,b)=>(a||0)+(b||0)/100;
  const fromSleeper=CUR.rosters.map(r=>({name:CUR.rName[r.roster_id],act:dec(r.settings.fpts,r.settings.fpts_decimal),opt:dec(r.settings.ppts,r.settings.ppts_decimal)}));
  if(fromSleeper.every(r=>r.opt>0))return fromSleeper;
  if(!ppos||!CUR.lg.roster_positions)return null;
  const tot={};
  for(const w of CUR._completed)for(const x of CUR.weeks[w]){const t=tot[x.roster_id]=tot[x.roster_id]||{name:CUR.rName[x.roster_id],act:0,opt:0};
    t.act+=x.points||0;t.opt+=Math.max(x.points||0,x.players_points?bestLineup(CUR.lg.roster_positions,x.players_points,ppos):0);}
  return Object.values(tot);
}
function parseCSV(text){
  const rows=[];let row=[],f="",q=false;
  for(let i=0;i<text.length;i++){const c=text[i];
    if(q){if(c==='"'&&text[i+1]==='"'){f+='"';i++;}else if(c==='"')q=false;else f+=c;}
    else if(c==='"')q=true;else if(c===","){row.push(f);f="";}
    else if(c==="\n"||c==="\r"){if(c==="\r"&&text[i+1]==="\n")i++;row.push(f);rows.push(row);row=[];f="";}
    else f+=c;}
  if(f||row.length){row.push(f);rows.push(row);}
  const [h,...b]=rows.filter(r=>r.length>1);
  return b.map(r=>Object.fromEntries(h.map((k,i)=>{const v=r[i]??"";return [k,v!==""&&!isNaN(v)?Number(v):v];})));
}
// Saved seasons (labels from data/combined) plus this season's finished games, one chronological list per person.
function histGames(CUR){
  const R=CUR._h2hRaw,G={};
  const add=(lab,g)=>(G[lab]=G[lab]||[]).push(g);
  R.rows.forEach(r=>add(r.manager,{season:+r.season,wk:+r.week,p:+r.points,op:+r.opponent_points,opp:r.opponent_manager,res:r.result,po:r.is_playoffs==="True",live:false}));
  const lab=nm=>R.alias[unesc(nm)]||unesc(nm);
  CUR._T.forEach(t=>t.log.forEach(g=>add(lab(t.name),{season:+CUR.lg.season,wk:g.wk,p:g.p,op:g.op,opp:lab(g.opp),res:g.res,po:false,live:true})));
  Object.values(G).forEach(a=>a.sort((x,y)=>(x.season-y.season)||(x.wk-y.wk)));
  return G;
}
function rivalryPairs(CUR){
  const G=histGames(CUR),P={};
  Object.entries(G).forEach(([a,gs])=>gs.forEach(g=>{if(a>g.opp)return; // count each game once, from the alphabetically first side
    const k=a+"\u0000"+g.opp,r=P[k]=P[k]||{a,b:g.opp,w:0,l:0,t:0,n:0,po:0,m:0,last:null};
    r.n++;r[g.res==="W"?"w":g.res==="L"?"l":"t"]++;if(g.po)r.po++;r.m+=g.p-g.op;r.last=g;}));
  return Object.values(P);
}
// Display name for every roster (escaped), from Sleeper's users and rosters.
function teamNames(users,rosters){
  const uname={};users.forEach(u=>uname[u.user_id]=u.display_name||u.username);
  const rName={};rosters.forEach(r=>rName[r.roster_id]=esc((r.owner_id&&uname[r.owner_id])||("Team "+r.roster_id)));
  return rName;
}
// Regular-season matchups (all[i] is week i+1) split into finished weeks and the schedule still to play.
// The first week that isn't final (or has no points yet) is the upcoming one.
function splitWeeks(lg,state,all){
  const weeks={},sched={}; let upcoming=null,upWeek=null;
  all.forEach((m,i)=>{const w=i+1;if(!m||!m.length)return;
    if(!upWeek&&isFinal(lg,state,w)&&m.some(x=>x.points>0))weeks[w]=m;
    else{if(!upWeek){upcoming=m;upWeek=w;}sched[w]=m;}});
  return {weeks,sched,upcoming,upWeek};
}
// Playoff, 1-seed and title odds: 4,000 simulated rest-of-seasons over the real remaining schedule.
const SIMS=4000;
const playoffSpots=CUR=>CUR.lg.settings.playoff_teams||6;
function playoffOdds(CUR){return simulate(CUR,CUR._T,CUR.pwk-1,CUR._completed.length,playoffSpots(CUR),SIMS);}
// Coach ratings: efficiency is points scored / best possible, benched is the gap. Best efficiency first.
function rateCoaches(rows){
  rows.forEach(r=>{r.left=Math.max(0,r.opt-r.act);r.eff=r.opt?r.act/r.opt:1;});
  return rows.sort((a,b)=>b.eff-a.eff);
}
// Each player's points this season while on any roster, started or not.
function playerPoints(weeks){
  const sp={};for(const w in weeks)for(const x of weeks[w]){const pp=x.players_points||{};for(const p in pp)sp[p]=(sp[p]||0)+pp[p];}
  return sp;
}
// Each roster's top scorer this season (points while on that roster), as {p, pts}, or null for an empty roster.
function seasonMvps(CUR){
  const {weeks,rName}=CUR;
  const tp={};Object.keys(rName).forEach(r=>tp[r]={});
  for(const w in weeks)for(const x of weeks[w]){const pp=x.players_points||{};for(const p in pp)tp[x.roster_id][p]=(tp[x.roster_id][p]||0)+pp[p];}
  const out={};Object.keys(tp).forEach(r=>{const mv=Object.keys(tp[r]).sort((a,b)=>tp[r][b]-tp[r][a])[0];out[r]=mv?{p:mv,pts:tp[r][mv]}:null;});
  return out;
}
// Started performances of 30+ points, best first.
function topPerformances(weeks){
  const tops=[];
  for(const w in weeks){for(const x of weeks[w]){const st=new Set(x.starters||[]);const pp=x.players_points||{};
    for(const p in pp){if(st.has(p)&&pp[p]>=30)tops.push({p,rid:x.roster_id,wk:+w,pts:pp[p]});}}}
  return tops.sort((a,b)=>b.pts-a.pts);
}
// Sleeper injury tags that count as hurt; Questionable doesn't.
const INJURED=["Out","IR","Doubtful","PUP","Sus","NA"];
// Completed trades, waiver and free-agent adds (biggest bid first) and FAAB spent per roster (first spender first),
// from each week's transactions: txs[i] is week i+1. Pass the rosters to take each one's total from Sleeper's
// waiver_budget_used, which also counts FAAB traded between teams; rosters without it keep their summed bids.
function rosterMoves(txs,rosters){
  const trades=[],adds=[],spentBy={};
  txs.forEach((tx,i)=>{const w=i+1;
    for(const t of tx||[]){if(t.status!=="complete")continue;
      if(t.type==="trade")trades.push({w,rosters:t.roster_ids||[],adds:t.adds||{}});
      else if((t.type==="waiver"||t.type==="free_agent")&&t.adds){const bid=(t.settings&&t.settings.waiver_bid)||0;
        for(const p in t.adds){const r=t.adds[p];adds.push({w,rid:r,p,bid});
          (spentBy[r]=spentBy[r]||{rid:r,spent:0,order:Object.keys(spentBy).length}).spent+=bid;}}}});
  adds.sort((a,b)=>b.bid-a.bid);
  (rosters||[]).forEach(r=>{const used=r.settings&&r.settings.waiver_budget_used;if(used==null)return;
    if(spentBy[r.roster_id])spentBy[r.roster_id].spent=used;
    else if(used>0)spentBy[r.roster_id]={rid:r.roster_id,spent:used,order:Object.keys(spentBy).length};});
  const spent=Object.values(spentBy).sort((a,b)=>a.order-b.order).map(({rid,spent})=>({rid,spent}));
  return {trades,adds,spent};
}
// Power board order: all-play %, then points for. Standings order: win %, then points for.
const byPower=(a,b)=>(b.appct-a.appct)||(b.pf-a.pf);
const byRec=(a,b)=>(b.winpct-a.winpct)||(b.pf-a.pf);
// Movement vs the same ranking one week earlier, rebuilt from the box scores so everyone sees the same arrows.
function powerMoves(CUR,power,completed){
  const move={};
  if(completed.length>1){const st=statsThrough(CUR,completed[completed.length-2]);
    const prev=Object.keys(st).map(r=>({name:CUR.rName[r],...st[r]})).sort(byPower).map(t=>t.name);
    power.forEach((t,i)=>{const was=prev.indexOf(t.name);if(was>=0)move[t.name]=was-i;});}
  return move;
}
// Next week's games with the model's chance that a beats b.
function matchupPairs(CUR){
  const {rName,upcoming}=CUR;
  const bm={};upcoming.forEach(x=>{(bm[x.matchup_id]=bm[x.matchup_id]||[]).push(x);});
  const comp=CUR._completed;const rate=comp.length?strengthThrough(CUR,comp[comp.length-1]).rate:null;
  const prob=(a,b)=>rate?CONF(rate[a]-rate[b]):.5; // P(a beats b)
  const pairs=[];for(const k in bm){const [a,b]=bm[k];if(a&&b)pairs.push({a:rName[a.roster_id],b:rName[b.roster_id],pa:prob(a.roster_id,b.roster_id)});}
  return pairs;
}
// Matchup of the week: the pair maximizing combined all-play + closeness. `prev` is last week's two teams.
function spotlight(T,pairs,prev){
  const byName={};T.forEach(t=>byName[t.name]=t);
  const juice=p=>{const A=byName[p.a],B=byName[p.b];return A&&B?(A.appct+B.appct)*2 - Math.abs(A.appct-B.appct):null;};
  const top=ps=>{let best=null,bs=-1;ps.forEach(p=>{const j=juice(p);if(j!==null&&j>bs){bs=j;best=p;}});return {best,bs};};
  const {best,bs}=top(pairs);
  const again=p=>prev&&(prev.includes(p.a)||prev.includes(p.b));
  if(M.repeatGap==null||!best||!again(best))return best;
  const alt=top(pairs.filter(p=>!again(p)));
  return alt.best&&alt.bs>=bs-M.repeatGap?alt.best:best;
}
// The two teams last week's matchup of the week featured, replayed week by week (each from the weeks before it).
function spotlightLast(CUR){
  if(M.repeatGap==null)return null;
  let prev=null;
  for(const w of Object.keys(CUR.weeks).map(Number).sort((a,b)=>a-b)){const st=statsThrough(CUR,w-1);
    const T=Object.keys(st).map(r=>({name:CUR.rName[r],appct:st[r].appct}));
    const b=spotlight(T,weekPairs(CUR,w).map(p=>({a:CUR.rName[p.a],b:CUR.rName[p.b]})),prev);
    prev=b?[b.a,b.b]:null;}
  return prev;
}
// Saved regular seasons as the {rName, weeks} the pick functions read, oldest first. Labels stand in for names.
function pastSeasons(rows){
  const by={};rows.forEach(r=>{if(r.is_playoffs!=="True")(by[r.season]=by[r.season]||[]).push(r);});
  return Object.keys(by).sort((a,b)=>a-b).map(s=>{const R=by[s],ids={},rName={},weeks={};
    R.forEach(r=>[r.manager,r.opponent_manager].forEach(m=>{if(!ids[m]){ids[m]=String(Object.keys(ids).length+1);rName[ids[m]]=m;}}));
    R.forEach(r=>{if(r.manager>r.opponent_manager)return;const m=weeks[r.week]=weeks[r.week]||[],mid=m.length/2+1;
      m.push({roster_id:ids[r.manager],matchup_id:mid,points:+r.points},{roster_id:ids[r.opponent_manager],matchup_id:mid,points:+r.opponent_points});});
    return {season:+s,rName,weeks};});
}
// This model's picks replayed over every saved season, graded like pickRecord.
function pickBacktest(rows){
  let correct=0,total=0,brierSum=0;
  const seasons=pastSeasons(rows).map(S=>{const r=pickRecord(S);correct+=r.correct;total+=r.total;brierSum+=(r.brier||0)*r.total;
    return {season:S.season,correct:r.correct,total:r.total,brier:r.brier};});
  return {seasons,correct,total,brier:total?brierSum/total:null};
}
// Every saved team's record and all-play after `wk` regular-season weeks, how its season ended, and that
// season's format. rows: all_weekly_scores without consolation games; recs: manager_season_records.
function historyStarts(rows,recs,wk){
  const fin={},fmt={};
  recs.forEach(s=>{fin[s.season+"|"+s.manager]=s;const f=fmt[s.season]=fmt[s.season]||{n_teams:0,spots:0};f.n_teams++;if(s.made_playoffs==="True")f.spots++;});
  const S={},byWeek={};
  rows.forEach(r=>{if(r.is_playoffs==="True"||+r.week>wk)return;
    const o=S[r.season+"|"+r.manager]=S[r.season+"|"+r.manager]||{season:+r.season,mgr:r.manager,w:0,l:0,t:0,pf:0,aw:0,al:0};
    o[r.result==="W"?"w":r.result==="L"?"l":"t"]++;o.pf+=+r.points;
    (byWeek[r.season+"|"+r.week]=byWeek[r.season+"|"+r.week]||[]).push(r);});
  Object.values(byWeek).forEach(R=>R.forEach(a=>R.forEach(b=>{if(a.manager!==b.manager&&+a.points!==+b.points)S[a.season+"|"+a.manager][+a.points>+b.points?"aw":"al"]++;})));
  return Object.entries(S).filter(([k])=>fin[k]).map(([k,o])=>{const f=fin[k];
    return {...o,rec:recstr(o),appct:o.aw/Math.max(1,o.aw+o.al),final_reg:f.regular_season_record,final_rank:+f.final_rank,
      playoffs:f.made_playoffs==="True",seed:f.playoff_seed===""?null:+f.playoff_seed,...fmt[o.season]};});
}
// How past teams with each record finished, counting only seasons with the same teams and playoff spots as `fmt`:
// a 2-2 start meant far more when 8 of 12 made the playoffs than it does with 6.
function startsLikeThese(starts,fmt){
  const out={};
  starts.filter(s=>s.n_teams===fmt.n_teams&&s.spots===fmt.spots).forEach(s=>{
    const o=out[s.rec]=out[s.rec]||{n:0,made_playoffs:0,titles:0,last:0,list:[]};
    o.n++;if(s.playoffs)o.made_playoffs++;if(s.final_rank===1)o.titles++;if(s.final_rank===s.n_teams)o.last++;o.list.push(s);});
  return out;
}
// The newest PDF dispatch week for a league's season, from almanac/issues.json ({league: {season: [weeks]}}), or null.
function latestIssue(issues,league,season){const w=((issues||{})[league]||{})[String(season)];return w&&w.length?Math.max(...w):null;}
// Saved history for head-to-head: every name a person has used (Yahoo nicknames, old and current Sleeper names)
// points at the label the saved files use. Seasons before `season` only; consolation games don't count.
function h2hRawFrom(rows,mg,season){
  const alias={};Object.values(mg).forEach(m=>{const nk=m.nicknames||[];if(!nk.length)return;
    const label=nk[nk.length-1]+(m.real_name?` (${m.real_name})`:"");nk.forEach(n=>alias[n]=label);alias[label]=label;});
  return {rows:rows.filter(r=>r.is_consolation!=="True"&&+r.season<+season),alias};
}
// Each finished week's median score, over every team that played.
function weekMedians(CUR){const med={};
  CUR._completed.forEach(w=>{const v=CUR.weeks[w].map(x=>x.points||0).sort((a,b)=>a-b),n=v.length;med[w]=n%2?v[(n-1)/2]:(v[n/2-1]+v[n/2])/2;});
  return med;}
// Where score p placed in week w: 1 is the top score, and equal scores share a place.
const rankIn=(CUR,w,p)=>1+CUR.weeks[w].filter(x=>(x.points||0)>p).length;
// Every team's place after each finished week under `order`: byRec for the standings race, byPower for the board.
function rankHistory(CUR,order){
  const out={};CUR._T.forEach(t=>out[t.name]=[]);
  for(const w of CUR._completed){const st=statsThrough(CUR,w);
    Object.keys(st).map(r=>({name:CUR.rName[r],...st[r]})).sort(order)
      .forEach((t,i)=>{if(out[t.name])out[t.name].push({wk:w,rank:i+1,rec:recstr(t)});});}
  return out;
}
// The regular-season games a roster still has to play, each with its opponent.
function remainingSchedule(CUR,rid){
  const out=[];
  Object.keys(CUR.sched).map(Number).filter(w=>w<CUR.pwk).sort((a,b)=>a-b).forEach(w=>{const m=CUR.sched[w];
    const mine=m.find(x=>String(x.roster_id)===String(rid)),opp=mine&&m.find(x=>x.matchup_id===mine.matchup_id&&x.roster_id!==mine.roster_id);
    if(opp)out.push({wk:w,rid:opp.roster_id,name:CUR.rName[opp.roster_id]});});
  return out;
}
// Each finished week's low score over every team that played, byes included, with everyone who tied it.
function weeklyLows(CUR){
  return Object.keys(CUR.weeks).map(Number).sort((a,b)=>a-b).map(w=>{const m=CUR.weeks[w],p=Math.min(...m.map(x=>x.points||0));
    const rids=m.filter(x=>(x.points||0)===p).map(x=>x.roster_id);return {wk:w,p,rids,names:rids.map(r=>CUR.rName[r])};});
}
// A full win either way separates schedule luck from noise.
const luckLabel=v=>v>=1?"lucky":v<=-1?"robbed":"fair";
// The standout games in a list from compute(): top score, widest and narrowest margins, most points in a loss.
// A tied game has no loser, so it can't be the heartbreak.
function gameHighs(games){
  const gap=g=>g.hip-g.lop;
  return {top:[...games].sort((a,b)=>b.hip-a.hip)[0]||null,blow:[...games].sort((a,b)=>gap(b)-gap(a))[0]||null,
    close:[...games].sort((a,b)=>gap(a)-gap(b))[0]||null,heart:games.filter(g=>g.hip>g.lop).sort((a,b)=>b.lop-a.lop)[0]||null};
}
// Unbeaten and winless teams by wins, then all-play %, then points: first is the unbeaten team whose scores back
// the record most, and the winless team the schedule has robbed most.
function unbeatenWinless(T){
  const by=(a,b)=>(b.w-a.w)||(b.appct-a.appct)||(b.pf-a.pf);
  return {unbeaten:T.filter(t=>t.l===0&&t.w>0).sort(by),winless:T.filter(t=>t.w===0&&t.l>0).sort(by)};
}
// The Dispatch's lead for the latest finished week, first that applies: an upset of a favourite this model gave at
// least M.upsetConf, a score 40 over the median, an unbeaten team at 3+ wins, a 50-point blowout, the power leader.
// `upset` is the model's surest pick that lost that week, which the Upset tile shows at any confidence.
function dispatchHeadline(CUR){
  const comp=CUR._completed,wk=comp[comp.length-1];if(!wk)return null;
  const {top,blow}=gameHighs(CUR._games.filter(g=>g.wk===wk)),med=weekMedians(CUR)[wk];
  const pw=comp.length>1?pickRecord(CUR).perWeek.find(x=>x.wk===wk):null;
  const upset=pw&&pw.picks.filter(p=>p.hit===false).sort((a,b)=>b.conf-a.conf)[0]||null;
  const U=unbeatenWinless(CUR._T).unbeaten[0];
  let head;
  if(upset&&upset.conf>=M.upsetConf)head={type:"upset",a:upset.dog,b:upset.fav,conf:upset.conf};
  else if(top&&top.hip-med>=40)head={type:"top",a:top.hi,p:top.hip};
  else if(U&&U.w>=3)head={type:"perfect",a:U.name,rec:recstr(U)};
  else if(blow&&blow.hip-blow.lop>=50)head={type:"blowout",a:blow.hi,b:blow.lo,margin:blow.hip-blow.lop};
  else head={type:"power",a:[...CUR._T].sort(byPower)[0].name};
  return {wk,head,upset};
}
// Bold calls from the weeks through `cut`: the luckiest team playing should lose, the most robbed should win.
function boldPicks(CUR,cut,playing){
  const st=statsThrough(CUR,cut);
  const arr=Object.keys(st).filter(r=>st[r].g>0&&playing.has(String(r))).map(r=>({r,luck:luckWins(st[r])}));
  if(arr.length<2)return [];
  const lucky=[...arr].sort((a,b)=>b.luck-a.luck)[0],robbed=[...arr].sort((a,b)=>a.luck-b.luck)[0],out=[];
  if(luckLabel(lucky.luck)==="lucky")out.push({type:"lucky",rid:lucky.r,name:CUR.rName[lucky.r]});
  if(luckLabel(robbed.luck)==="robbed"&&robbed.r!==lucky.r)out.push({type:"robbed",rid:robbed.r,name:CUR.rName[robbed.r]});
  return out;
}
// Every finished week's bold calls replayed from the weeks before it and graded; a tied game isn't graded.
function boldReplay(CUR){
  const comp=Object.keys(CUR.weeks).map(Number).sort((a,b)=>a-b),rows=[];let hit=0,tot=0;
  for(const w of comp){if(w<=comp[0])continue;
    const pairs=weekPairs(CUR,w),playing=new Set();pairs.forEach(p=>{playing.add(String(p.a));playing.add(String(p.b));});
    const resOf=rid=>{const p=pairs.find(p=>String(p.a)===String(rid)||String(p.b)===String(rid));if(!p)return null;
      const mine=String(p.a)===String(rid)?p.ap:p.bp,opp=String(p.a)===String(rid)?p.bp:p.ap;return mine===opp?null:mine>opp?"W":"L";};
    boldPicks(CUR,w-1,playing).forEach(c=>{const r=resOf(c.rid);if(r===null)return;
      const ok=r===(c.type==="lucky"?"L":"W");tot++;if(ok)hit++;rows.push({wk:w,...c,ok});});
  }
  return {rows,hit,tot};
}
// Next week's bold calls, or null when there are none.
function boldUpcoming(CUR){
  if(!CUR.upcoming||!CUR.upcoming.length)return null;
  const comp=Object.keys(CUR.weeks).map(Number);if(!comp.length)return null;
  const playing=new Set();CUR.upcoming.forEach(x=>playing.add(String(x.roster_id)));
  const calls=boldPicks(CUR,Math.max(...comp),playing);
  return calls.length?{week:CUR.upWeek,calls}:null;
}
// Ratings after the last finished week (null before week 1): the source of every pick and bracket chance.
function ratingsNow(CUR){const c=CUR._completed;return c&&c.length?strengthThrough(CUR,c[c.length-1]).rate:null;}
// Unplayed bracket games with both teams set, and this model's chance that t1 wins each one.
function bracketChances(CUR,B){
  const rate=ratingsNow(CUR);if(!rate||!Array.isArray(B))return [];
  return B.filter(g=>g.w==null&&g.t1!=null&&g.t2!=null).map(g=>({m:g.m,r:g.r,t1:g.t1,t2:g.t2,p:CONF(rate[g.t1]-rate[g.t2])}));
}
// Where the coach-rating bars start: the nearest 5% below the worst efficiency so gaps show, and never above 95%
// so a perfect (or empty) board still draws.
const coachFloor=rows=>rows.length?Math.min(.95,Math.floor(Math.min(...rows.map(r=>r.eff))*20)/20):.95;
// Win or loss runs in one person's chronological games. A run reaching the end of the list is still going only
// when `current` (the person plays this season); a manager who left has finished every run.
function streaks(games,want,current){const out=[];let run=null;
  games.forEach(g=>{if(g.res===want){if(!run)run={len:0,a:g};run.len++;run.b=g;}else if(run){out.push(run);run=null;}});
  if(run){if(current)run.ongoing=true;out.push(run);}return out;}
// Top-n leaderboards across every saved season, with this season's finished games competing live. seasons is
// manager_season_records, whose points_for is regular season only, so points per game divides by regular-season games.
function recordBook(CUR,seasons,n=5){
  const G=histGames(CUR),all=Object.entries(G).flatMap(([lab,gs])=>gs.map(g=>({lab,...g})));
  const top=(arr,key)=>[...arr].sort((a,b)=>key(b)-key(a)).slice(0,n);
  const label=nm=>CUR._h2hRaw.alias[unesc(nm)]||unesc(nm),current=new Set(CUR._T.map(t=>label(t.name)));
  const runs=res=>top(Object.entries(G).flatMap(([lab,gs])=>streaks(gs,res,current.has(lab)).map(r=>({lab,...r}))),r=>r.len+(r.ongoing?.1:0));
  const gp=r=>(+r.regular_wins)+(+r.regular_losses)+(+r.regular_ties);
  const pct=r=>{const w=+r.regular_wins,l=+r.regular_losses,t=+r.regular_ties;return (w+t/2)/Math.max(1,w+l+t);};
  return {high:top(all,g=>g.p),low:top(all.filter(g=>g.p>0),g=>-g.p),blowouts:top(all.filter(g=>g.res==="W"),g=>g.p-g.op),
    winStreaks:runs("W"),loseStreaks:runs("L"),
    ppg:top(seasons.filter(r=>gp(r)>0),r=>r.points_for/gp(r)).map(r=>({...r,ppg:r.points_for/gp(r)})),
    best:top(seasons,r=>pct(r)+r.points_for/1e6),worst:top(seasons,r=>-pct(r)-r.points_for/1e6)};
}

return {esc,unesc,teamNames,splitWeeks,SIMS,playoffSpots,playoffOdds,rateCoaches,playerPoints,seasonMvps,topPerformances,INJURED,rosterMoves,nameOf,positionOf,injuryOf,rng,erf,normcdf,FLEX,bestLineup,isFinal,compute,simulate,meanPF,nextPow2,
  statsThrough,strengthThrough,weekPairs,CONF,pickRecord,upcomingPicks,recstr,luckWins,h2h,recH,seriesLine,rivalsOf,
  rivalryChips,coachRows,parseCSV,histGames,rivalryPairs,byPower,byRec,powerMoves,matchupPairs,spotlight,h2hRawFrom,
  latestIssue,playBracket,bracketSlots,spotlightLast,pastSeasons,pickBacktest,historyStarts,startsLikeThese,model:M,
  weekMedians,rankIn,rankHistory,remainingSchedule,weeklyLows,luckLabel,gameHighs,unbeatenWinless,dispatchHeadline,boldPicks,
  boldReplay,boldUpcoming,ratingsNow,bracketChances,coachFloor,streaks,recordBook};
}
const live=build(MODELS.live);
live.canary=build(MODELS.canary);
return live;
})();
if(typeof module!=="undefined")module.exports=AlmanacCore;
