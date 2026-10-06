"""Render one league's dispatch: facts JSON + copy module -> HTML -> PDF (headless Chrome).
usage: python3 -I build.py <facts.json> <copy.py> <out.pdf>"""
import json, sys, math, html, importlib.util, subprocess, os, tempfile, time, shutil

F = json.load(open(sys.argv[1]))
spec = importlib.util.spec_from_file_location("copy_mod", sys.argv[2]); C = importlib.util.module_from_spec(spec); spec.loader.exec_module(C)
C = C.COPY
OUT = sys.argv[3]
TEAMS = F["teams"]
BY = {t["name"]: t for t in TEAMS}
H = F["history"]
e = html.escape
pts = lambda x: f"{x:,.2f}"  # fantasy points are scored to the hundredth
pct = lambda x: f"{math.floor(x * 1000 + 0.5) / 10:g}%"  # index.html: Math.round(x*1000)/10

def luck_word(t):
    # index.html's luckTag: a full win either way
    if t["luck"] >= 1: return '<span class="lucky">lucky</span>'
    if t["luck"] <= -1: return '<span class="robbed">robbed</span>'
    return '<span class="faint">fair</span>'

def standings():
    rows = []
    for t in TEAMS:
        s = H["starts_like_these"][t["rec"]]
        hist = f'{s["made_playoffs"]} of {s["n"]}' if s["n"] else "first ever"
        rows.append(f'<tr><td><b>{e(t["name"])}</b></td><td class="n">{t["rec"]}</td><td class="n">{pts(t["pf"])}</td><td class="n">{pts(t["pa"])}</td>'
                    f'<td class="n">{t["allplay"]}</td><td class="n">{luck_word(t)}</td><td class="n">{hist}</td></tr>')
    return (f'<table><thead><tr><th>Team</th><th class="n">Rec</th><th class="n">PF</th><th class="n">PA</th><th class="n">All-play</th><th class="n">Luck</th>'
            f'<th class="n">Same start made playoffs</th></tr></thead><tbody>{"".join(rows)}</tbody></table>')

def luck_map():
    W, Hh, L, R, Tp, B = 640, 400, 54, 22, 18, 46
    pw, ph = W - L - R, Hh - Tp - B
    x = lambda v: L + v * pw; y = lambda v: Tp + (1 - v) * ph
    col = lambda t: "#0b7aa0" if t["luck"] >= 1 else "#b32a3e" if t["luck"] <= -1 else "#8a8a85"
    spots = {}
    for t in TEAMS:
        wp = (t["w"] + .5 * t["t"]) / max(1, t["w"] + t["l"] + t["t"])
        spots.setdefault((round(t["appct"], 4), round(wp, 4)), []).append(t)
    pts = []
    for (ap, wp), ts in spots.items():
        cx, cy = x(ap), y(wp); names = [t["name"] for t in ts]
        w = max(len(n) for n in names) * 6.4 + 4; h = len(names) * 13
        left = cx + 10 + w > W - R
        pts.append(dict(cx=cx, cy=cy, names=names, w=w, h=h, left=left, lx=cx - 10 if left else cx + 10, top=cy - h / 2 - 2, t=ts[0], n=len(ts)))
    box = lambda p: (p["lx"] - p["w"], p["lx"]) if p["left"] else (p["lx"], p["lx"] + p["w"])
    for _ in range(400):
        moved = False
        for a in pts:
            for b in pts:
                if a is b: continue
                a0, a1 = box(a); b0, b1 = box(b)
                ov = min(a["top"] + a["h"], b["top"] + b["h"]) - max(a["top"], b["top"])
                if a0 < b1 and b0 < a1 and ov > 0:
                    s = -1 if a["top"] <= b["top"] else 1; a["top"] += s * (ov / 2 + .5); b["top"] -= s * (ov / 2 + .5); moved = True
                if a0 - 8 < b["cx"] < a1 + 8 and a["top"] - 8 < b["cy"] < a["top"] + a["h"] + 8:
                    a["top"] += (-1 if a["top"] + a["h"] / 2 <= b["cy"] else 1) * 1.5; moved = True
        for p in pts: p["top"] = max(Tp, min(Hh - B - p["h"], p["top"]))
        if not moved: break
    g = []
    for v in (0, .25, .5, .75, 1):
        g.append(f'<line class="grid" x1="{x(0)}" x2="{x(1)}" y1="{y(v)}" y2="{y(v)}"/><line class="grid" x1="{x(v)}" x2="{x(v)}" y1="{y(0)}" y2="{y(1)}"/>'
                 f'<text class="tick" x="{L-8}" y="{y(v)+4}" text-anchor="end">{int(v*100)}%</text><text class="tick" x="{x(v)}" y="{Hh-B+18}" text-anchor="middle">{int(v*100)}%</text>')
    dots, labels = [], []
    for p in pts:
        dots.append(f'<circle cx="{p["cx"]:.1f}" cy="{p["cy"]:.1f}" r="{8 if p["n"]>1 else 6.5}" fill="{col(p["t"])}" stroke="#fff" stroke-width="2"/>')
        mid = p["top"] + p["h"] / 2
        if abs(mid - p["cy"]) > 9:
            labels.append(f'<line class="lead" x1="{p["cx"]+(-7 if p["left"] else 7):.1f}" y1="{p["cy"]:.1f}" x2="{p["lx"]:.1f}" y2="{mid:.1f}"/>')
        ts = "".join(f'<tspan x="{p["lx"]:.1f}" y="{p["top"]+10+k*13:.1f}">{e(n)}</tspan>' for k, n in enumerate(p["names"]))
        labels.append(f'<text class="lbl" text-anchor="{"end" if p["left"] else "start"}">{ts}</text>')
    return f'''<svg viewBox="0 0 {W} {Hh}" class="chart" role="img" aria-label="Luck map">
<polygon fill="#0b7aa0" fill-opacity=".05" points="{x(0)},{y(0)} {x(0)},{y(1)} {x(1)},{y(1)}"/>
<polygon fill="#b32a3e" fill-opacity=".05" points="{x(0)},{y(0)} {x(1)},{y(0)} {x(1)},{y(1)}"/>
{"".join(g)}<line class="diag" x1="{x(0)}" y1="{y(0)}" x2="{x(1)}" y2="{y(1)}"/>
<text class="zlbl" x="{x(.03)}" y="{y(.93)}" fill="#0b7aa0">LUCKY</text>
<text class="zlbl" x="{x(.97)}" y="{y(.04)}" fill="#b32a3e" text-anchor="end">ROBBED</text>
<text class="tick" x="{L+pw/2}" y="{Hh-8}" text-anchor="middle">All-play win %: how good your scores have been</text>
<text class="tick" transform="translate(14 {Tp+ph/2}) rotate(-90)" text-anchor="middle">Actual win %</text>
{"".join(dots)}{"".join(labels)}</svg>'''

def power():
    out = []
    for t in sorted(TEAMS, key=lambda t: t["power"]):
        m = t["power_move"]
        mv = f'<span class="up">▲{m}</span>' if m > 0 else f'<span class="dn">▼{-m}</span>' if m < 0 else '<span class="faint">–0</span>'
        out.append(f'<div class="pr"><div class="pr-n">{t["power"]}</div><div class="pr-m">{mv}</div><div class="pr-b"><b>{e(t["name"])}</b> · {C["power"][t["name"]]}</div></div>')
    return "".join(out)

def odds():
    rows = []
    for t in sorted(TEAMS, key=lambda t: (-t["odds"]["title"], -t["odds"]["playoffs"])):
        o = t["odds"]
        rows.append(f'<tr><td>{e(t["name"])}</td><td class="n">{t["rec"]}</td><td class="n">{pts(t["pfg"])}</td><td class="n">{pct(o["playoffs"])}</td>'
                    f'<td class="n">{pct(o["seed1"])}</td><td class="n"><b>{pct(o["title"])}</b></td></tr>')
    return ('<table class="dark"><thead><tr><th>Team</th><th class="n">Rec</th><th class="n">PF/g</th><th class="n">Playoffs</th><th class="n">1 seed</th><th class="n">Title</th></tr></thead>'
            f'<tbody>{"".join(rows)}</tbody></table>')

def coach():
    rows = []
    for i, t in enumerate(sorted(TEAMS, key=lambda t: -t["coach"]["eff"])):
        c = t["coach"]
        rows.append(f'<tr><td>{i+1}</td><td><b>{e(t["name"])}</b></td><td class="n">{c["eff"]*100:.1f}%</td><td class="n">{pts(c["benched"])}</td><td>{C["coach"].get(t["name"], "")}</td></tr>')
    return f'<table><thead><tr><th>#</th><th>Manager</th><th class="n">Efficiency</th><th class="n">Benched</th><th>Verdict</th></tr></thead><tbody>{"".join(rows)}</tbody></table>'

def cards(cs):
    return "".join(f'<div class="card c-{c["cls"]}"><div class="tag">{c["tag"]}</div><div class="big">{c["big"]}</div><div class="hl">{c["hl"]}</div><p>{c["body"]}</p></div>' for c in cs)

def items(xs): return "<ul>" + "".join(f"<li>{x}</li>" for x in xs) + "</ul>"
def hardware(xs): return "".join(f'<div class="hw"><div class="hw-k">{k}</div><p>{v}</p></div>' for k, v in xs)
def paras(xs): return "".join(f"<p>{x}</p>" for x in (xs if isinstance(xs, list) else [xs]))

c = C
body = f'''
<div class="kicker">{c["kicker"]}</div>
<h1>{c["title"]}</h1>
<div class="sub">{c["subtitle"]}</div>
<div class="rule"></div>
<p class="lede">{c["lede"]}</p>

<div class="keep"><h2>The standings, and what history says about them</h2>
{paras(c["standings_intro"])}</div>
<div class="cap">{c["standings_cap"]}</div>
{standings()}
{paras(c["standings_after"])}

<div class="keep"><h2>The luck map</h2>
{paras(c["luck_intro"])}</div>
<div class="chartbox"><div class="charttitle">{c["luck_title"]}</div>{luck_map()}</div>
{paras(c["luck_after"])}

<div class="keep"><h2>{c["feature_title"]}</h2>
{paras(c["feature_intro"])}</div>
{cards(c["cards"])}
{paras(c["feature_after"])}

<div class="keep"><h2>Power rankings</h2>
<p class="intro">True strength (all-play, then points), with movement since last issue.</p></div>
{power()}

<div class="keep"><h2>Matchup of the week</h2>
<div class="motw"><div class="motw-h">{c["motw_head"]}</div>{paras(c["motw_body"])}<div class="motw-s">{c["motw_series"]}</div></div></div>
{paras(c["elsewhere"])}

<div class="keep"><h2>The hardware</h2>
{hardware(c["hardware"])}</div>

<div class="keep"><h2>Coach ratings</h2>
{paras(c["coach_intro"])}</div>
{coach()}
{paras(c["coach_after"])}

<div class="keep"><h2>{c["cellar_title"]}</h2>
{paras(c["cellar_intro"])}</div>
{items(c["cellar_items"])}

<div class="keep"><h2>Rivalry spotlight &amp; milestone watch</h2>
{items(c["rivalry_items"])}</div>

<div class="keep"><h2>Playoff &amp; title odds</h2>
{paras(c["odds_intro"])}</div>
{odds()}
{paras(c["odds_after"])}

<div class="keep"><h2>Odds &amp; ends</h2>
{items(c["ends"])}</div>
<div class="closer">{c["closer"]}</div>
<div class="foot">{c["footer"]}</div>
'''

CSS = '''
@page{size:letter;margin:0.7in 0.85in 0.75in}
*{box-sizing:border-box}
body{margin:0;font:10.6pt/1.55 Charter,"Bitstream Charter",Georgia,serif;font-variant-numeric:lining-nums;font-feature-settings:"lnum" 1;color:#1d1d1b;background:#fff;-webkit-print-color-adjust:exact;print-color-adjust:exact}
h1,h2,.kicker,.sub,table,.pr-n,.pr-m,.tag,.big,.hw-k,.cap,.charttitle,.motw-h,.motw-s,.foot{font-family:"Helvetica Neue",Helvetica,Arial,sans-serif}
.kicker{font-size:7.6pt;letter-spacing:.09em;color:#b07d1a;font-weight:600}
h1{font-size:25pt;line-height:1.02;color:#6b1420;margin:6px 0 6px;font-weight:800;letter-spacing:-.01em}
.sub{font-size:8.6pt;color:#6b6b66}
.rule{height:2.5px;background:#6b1420;margin:12px 0 16px}
.lede{font-size:12.4pt;line-height:1.55}
.lede::first-letter{float:left;font-size:44pt;line-height:.9;padding:4px 8px 0 0;color:#6b1420}
h2{font-size:12.5pt;margin:26px 0 8px;padding-bottom:6px;border-bottom:1.5px solid #1d1d1b;break-after:avoid}
p{margin:0 0 9px}
.intro{color:#3b3b38}
b{font-weight:700}
.lucky{color:#0b7aa0;font-weight:700}.robbed{color:#b32a3e;font-weight:700}.faint{color:#8a8a85}
.up{color:#1f7a45}.dn{color:#b32a3e}
.inj{color:#b32a3e;font-weight:700}.good{color:#1f7a45;font-weight:700}
table{width:100%;border-collapse:collapse;font-size:8.3pt;margin:4px 0 12px}
tr{break-inside:avoid}
th{text-align:left;font-weight:700;color:#3b3b38;border-bottom:1.5px solid #1d1d1b;padding:5px 6px}
td{padding:4.5px 6px;border-bottom:1px solid #e3e1da;vertical-align:top}
.n{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
table.dark th{background:#1d1d1b;color:#fff;border:0}
.cap{font-size:8pt;color:#6b6b66;margin-top:8px}
.chartbox{background:#faf8f3;border:1px solid #e8e4da;border-radius:4px;padding:10px 10px 4px;margin:8px 0 10px;break-inside:avoid}
.charttitle{font-size:9.5pt;font-weight:700;margin:0 0 2px 6px}
.chart{width:100%;height:auto;display:block}
.chart .grid{stroke:#e4e1d8;stroke-width:1}.chart .diag{stroke:#8a8a85;stroke-dasharray:4 4;stroke-width:1.2}
.chart .tick{font:8.5px "Helvetica Neue",Arial,sans-serif;fill:#6b6b66}.chart .zlbl{font:italic 700 11px "Helvetica Neue",Arial,sans-serif;letter-spacing:.05em}
.chart .lbl{font:10px "Helvetica Neue",Arial,sans-serif;fill:#1d1d1b}.chart .lead{stroke:#b9b6ad;stroke-width:1}
.card{border-left:4px solid #8a8a85;background:#faf8f3;padding:10px 14px 6px;margin:10px 0;break-inside:avoid}
.card.c-robbed{border-color:#b32a3e}.card.c-lucky{border-color:#0b7aa0}.card.c-good{border-color:#1f7a45}
.tag{font-size:7.4pt;letter-spacing:.09em;font-weight:700;color:#6b6b66}
.big{font-size:20pt;font-weight:800;line-height:1.1;margin-top:2px}
.hl{font-weight:700;margin:2px 0 5px}
.card p{font-size:9.8pt}
.pr{display:grid;grid-template-columns:22px 30px 1fr;gap:6px;padding:7px 0;border-bottom:1px solid #e3e1da;break-inside:avoid}
.pr-n{font-size:12pt;color:#6b1420;font-weight:700}.pr-m{font-size:7.6pt;padding-top:4px}.pr-b{font-size:9.8pt}
.motw{background:#faf8f3;border:1px solid #e8e4da;padding:12px 14px 6px;margin:6px 0 12px;break-inside:avoid}
.motw-h{font-size:12pt;font-weight:800;margin-bottom:6px}.motw-s{font-size:8.6pt;color:#6b1420;font-weight:700;margin:2px 0 8px}
.hw{break-inside:avoid;margin:0 0 4px}.hw-k{font-size:7.4pt;letter-spacing:.09em;font-weight:700;color:#b07d1a;margin-top:10px}
ul{padding-left:18px;margin:4px 0 10px}li{margin:0 0 7px}
.closer{background:#f1ece0;padding:12px 16px;margin:16px 0;font-size:11pt;break-inside:avoid}
.keep{break-inside:avoid}
.foot{border-top:1px solid #1d1d1b;margin-top:18px;padding-top:8px;font-size:7.4pt;color:#6b6b66}
'''
doc = f'<!doctype html><html><head><meta charset="utf-8"><title>{e(c["doc_title"])}</title><style>{CSS}</style></head><body>{body}</body></html>'
htmlp = os.path.splitext(OUT)[0] + ".html"
open(htmlp, "w").write(doc)
chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
if os.path.exists(OUT): os.remove(OUT)
prof = tempfile.mkdtemp()
if True:
    # headless Chrome on macOS often writes the PDF and then never exits, so wait for the file to settle and close it ourselves
    proc = subprocess.Popen([chrome, "--headless=new", "--disable-gpu", f"--user-data-dir={prof}", "--no-pdf-header-footer", f"--print-to-pdf={OUT}", "file://" + os.path.abspath(htmlp)],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    last, t0 = -1, time.time()
    while time.time() - t0 < 90:
        time.sleep(1)
        size = os.path.getsize(OUT) if os.path.exists(OUT) else -1
        if proc.poll() is not None or (size > 0 and size == last): break
        last = size
    proc.kill(); proc.wait(); time.sleep(1)
shutil.rmtree(prof, ignore_errors=True)
if not os.path.exists(OUT): sys.exit("Chrome did not produce a PDF")
print(OUT)
