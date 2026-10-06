COPY = dict(
doc_title="The Sober Gang Almanac, Week 5 2026",
kicker="WEEK 5 DISPATCH · FOUR WEEKS IN · THE ARCHIVE EDITION",
title="The Sober Gang<br>Almanac",
subtitle="State of the league after Weeks 1 to 4 · 2026 season · checked against every game since 2019",
lede="""Last year's last-place team is in first. The defending champion is 1-3. The best team in the league by every measure except the one that counts is 2-2,
and in seven seasons no 2-2 team has ever won this thing. Four teams sit at 3-1, which matters more than it sounds: five of the seven Sober Gang champions
started exactly 3-1. This is the first issue with the whole archive behind it, the Nooblets years on Yahoo included, and the archive has opinions.""",

standings_intro=["""Record is what happened. All-play (your record if you played all nine opponents every week) is what should have happened.
The last column is new: of every team since 2019 that started with the same record, how many made the playoffs."""],
standings_cap="Sober Gang through Week 4 · sorted by record, then points",
standings_after=["""A 3-1 start has made the playoffs 12 times in 16 tries and produced five champions. A 2-2 start has made it 15 of 25 times and produced none.
And 0-4 is 0 for 5."""],

luck_intro=["""Every team by how good it has actually been (all-play) versus what the scoreboard gave it. Above the line you're a thief. Below it, you've been robbed."""],
luck_title="The Sober Gang luck map · through Week 4",
luck_after=["""<b>jasonle is stranded in the robbed corner</b>: a 29-7 all-play, the most points in the league, and a .500 record. <b>keveezy is right behind</b>,
1-3 on a winning 22-14 all-play. Up top, <b>lmphm is 3-1 on a losing all-play</b>, and if that sounds familiar it's because lmphm is also the luckiest team in Aggtown. Two leagues, one horseshoe."""],

feature_title="Four weeks, seven years of precedent",
feature_intro=["""Sober Gang's Sleeper history only starts in 2024. With the Nooblets years added, we can ask the real question: when a team has looked like this after four weeks, what happened next?"""],
cards=[
 dict(cls="good", tag="WORST TO FIRST · donblood", big="182.10",
      hl="Last place in 2025. First place now, and it isn't a fluke.",
      body="""donblood finished 10th of 10 last year at 5-9. This year's team opened with <b>182.10 in Week 1, the sixth-highest score in league history</b> (of 1,058),
      and hasn't let up: 3-1, a 24-12 all-play, CeeDee Lamb (112.20) and Derrick Henry (90.80) both rolling. The two previous teams to start 3-1 on a 24-12 all-play
      were keveezy in 2019 and anth0nyng in 2025. Both won the title. The worry is the receiver room: <span class="inj">McConkey and Coker Out</span>."""),
 dict(cls="robbed", tag="THE ROBBED · jasonle", big="29-7",
      hl="The best all-play of any 2-2 start in league history.",
      body="""591.78 points, most in the league. Losses to the sixth-highest score ever (donblood's 182.10, while jasonle put up 155.46, the most in a loss this season)
      and to Abadahh by <b>half a point</b> in Week 3, with Michael Wilson's 25.90 on the bench and Tetairoa McMillan's 3.70 in the lineup. The sim makes jasonle the title
      favorite. History adds two footnotes: no 2-2 team has ever won Sober Gang, and jasonle's own 2025 team started 2-2 on a 24-12 all-play and finished 4-10."""),
 dict(cls="robbed", tag="THE OTHER ROBBED · keveezy", big="22-14",
      hl="The best all-play of any 1-3 start in league history.",
      body="""Eighteen teams have started 1-3 here. Nine made the playoffs, and jigri won the whole thing from 1-3 in 2024. keveezy has scored 532.98, as many as 3-1 jigri (534.28) and PutItOnYa (533.62),
      and lost the opener by 13.36 with Chuba Hubbard (23.70) on the bench behind Saquon Barkley (9.00),
      who is now <span class="inj">Out</span>. The sim gives keveezy a 62% playoff shot. History says that's about right."""),
],
feature_after=["""And the 0-4 floor: yckyb is the sixth team to start 0-4. None of the first five made the playoffs. The defending champion, anth0nyng, is 1-3 on a 16-20 all-play,
and no Sober Gang champion has ever repeated. The best title defense so far is 2nd (PutItOnYa in 2024, jigri in 2025). anth0nyng's previous defense, in 2022, ended 9th."""],

power={
 "jasonle":"""The best team in the league, at .500. Gibbs (116.00), Kenneth Walker (110.10) and McMillan (74.50) make the deepest core here, and 591.78 points is 25 clear of anyone.
 <span class="inj">A.J. Brown on IR</span> after five points as a second-round pick is the only real scar. The 2022 champion.""",
 "donblood":"""3-1, second in points, 24-12 all-play, and a week-one score for the history books. <span class="inj">McConkey and Coker Out, Kamara Questionable, Jordan Mason on IR</span>,
 so the depth will get tested. donblood has never won Sober Gang (runner-up in 2020).""",
 "keveezy":"""The riser. 1-3 with a winning all-play, Amon-Ra (91.30) and Chris Olave (90.10) producing, and Patrick Mahomes (a 12th-round pick) giving real value.
 <span class="inj">Saquon is Out</span>. The 2019 champion, but last place as recently as 2024.""",
 "jigri":"""3-1 on a 20-16 all-play. JSN (116.66) is the top-scoring player in the league. The 3-1 start could be 4-0 if Jared Goff (29.78, a 15th-round steal) had started over
 Trevor Lawrence (7.16) in a 4.16-point loss to lmphm. <span class="inj">Justin Jefferson Out</span>. Two titles and last year's runner-up.""",
 "PutItOnYa":"""3-1, the sharpest lineup-setter in the league (94.7% efficiency), Bijan (105.40) and Kyren (89.70) doing the work. The one loss was by 0.28 points to jigri.
 <span class="inj">Etienne on IR</span>. The career wins leader in this league.""",
 "lmphm":"""3-1 on a 17-19 all-play: 15th of the 16 teams who've started 3-1 by all-play. The closest comp is jigri in 2020 (3-1 on 17-19), who won the title, so don't laugh too hard.
 Josh Allen (115.46) is the engine; <span class="inj">DeVonta Smith and Terry McLaurin are Out</span>, and first-round pick Puka Nacua has 40.10 points.""",
 "anth0nyng":"""The defending champion, 1-3 on a 16-20 all-play. Opened the season with the year's worst beating (46.16 points, to lmphm) and hasn't found a rhythm since.
 McCaffrey (74.00) and Davante Adams (73.00) are fine; <span class="inj">Rashee Rice is Questionable</span>. The most active manager on the wire (9 adds).""",
 "dexclusive":"""2-2, and by lineup alone should be 3-1 or better: lost Week 2 by 1.28 with Stefon Diggs (21.70) benched for DJ Moore (-0.10), and Week 3 with Brock Bowers (27.60) benched
 for Dalton Schultz (6.00). Biggest FAAB spender ($45), best free pickup (Bryce Young, 60.18 started points). <span class="inj">Goedert, Keenan Allen and Rachaad White Out; Tee Higgins Questionable</span>.""",
 "Abadahh":"""2-2 on a 10-26 all-play, tied for the worst all-play of any 2-2 start in league history. Wins by 7.00 over yckyb and 0.52 over jasonle are the whole story.
 <span class="inj">Ja'Marr Chase and Breece Hall Out, Jeremiyah Love Questionable</span>.""",
 "yckyb":"""0-4, fewest points (412.88), an 8-28 all-play, and the most points left on the bench (102.96). Brock Purdy, a 15th-round pick, has the most points of any drafted
 player in the league (101.48). <span class="inj">Lamar Questionable, Achane on IR</span>.""",
},

motw_head="jasonle (2-2) vs PutItOnYa (3-1)",
motw_body=["""The league's most robbed team against its most efficient one, and a title-game rematch. PutItOnYa leads the series 8-5, all of it built in the regular season. But the two playoff meetings both went to jasonle: the 2019 third-place game (134.82 to 110.66) and <b>the 2022 championship</b> (144.10 to 112.28).""",
"""The model makes jasonle a 64.5% favorite on scoring alone. PutItOnYa's answer has been to start the right players every single week and let the other team blink.
Something has to give."""],
motw_series="Series: PutItOnYa leads 8-5 · jasonle 2-0 in the playoffs, including the 2022 title game",
elsewhere=["""<b>Elsewhere:</b> donblood (3-1) gets the defending champ anth0nyng (1-3), who leads the series 6-3, though donblood won their only playoff meeting.
lmphm (3-1) draws winless yckyb, who leads that series 6-4 and has won the last two. And jigri vs dexclusive is dead even at 6-6, except in the playoffs, where dexclusive is 2-0."""],

hardware=[
 ("HIGH SCORE OF THE SEASON", """donblood, 182.10 (Week 1). The sixth-highest score in Sober Gang history, out of 1,058. The record is still Abadahh's 212.58 from 2021."""),
 ("LOW SCORE OF THE SEASON", """Abadahh, 78.48 in Week 4, a loss to jigri. yckyb's 84.34 in Week 3 is next."""),
 ("BIGGEST BLOWOUT", """lmphm 154.36, anth0nyng 108.20 (Week 1). A 46.16-point welcome back for the defending champ."""),
 ("MOST POINTS IN A LOSS", """jasonle, Week 1: 155.46 and still lost, because donblood dropped 182.10."""),
 ("CLOSEST GAME", """jigri 139.10, PutItOnYa 138.82 (Week 1). Decided by 0.28. Abadahh over jasonle by 0.52 in Week 3 is a close second."""),
 ("DRAFT STEAL / BUST", """Steal: Brock Purdy, pick 149 (yckyb), 101.48 points, the most of any drafted player in the league. Bust: A.J. Brown, pick 20 (jasonle), 5.60 points, now on IR."""),
 ("TOP PERFORMANCE", """Tetairoa McMillan, 45.20 (jasonle, Week 4), one week after scoring 3.70 in the half-point loss. JSN's 42.50 (jigri, Week 2) is second."""),
],

coach_intro=["""Efficiency is points scored divided by the best lineup possible from the same roster each week. Benched is the gap. Higher efficiency is better."""],
coach={
 "PutItOnYa":"Sharpest in the league",
 "Abadahh":"Sharp, with less to choose from",
 "donblood":"Good",
 "lmphm":"Good",
 "anth0nyng":"Fine",
 "jasonle":"The half-point loss lives here",
 "keveezy":"One call cost Week 1",
 "jigri":"One call cost Week 2",
 "dexclusive":"Two calls cost two games",
 "yckyb":"One call cost Week 1; most points benched",
},
coach_after=["""<b>The lineup calls that flipped results.</b> Six games this season were lost by less than the gap between a benched player and the starter he could have replaced:
yckyb in Week 1 (Isaiah Likely 27.80 over Colston Loveland 0.00, lost by 7.00), keveezy in Week 1 (Hubbard 23.70 over Saquon 9.00, lost by 13.36), jigri in Week 2
(Goff 29.78 over Lawrence 7.16, lost by 4.16), dexclusive in Weeks 2 and 3 (Diggs, then Bowers), and jasonle in Week 3 (Michael Wilson 25.90 over McMillan 3.70, lost by 0.52).
In a world of perfect lineups, jigri is 4-0, lmphm is 1-3, and Abadahh is 0-4."""],

cellar_title="The cellar",
cellar_intro=["""Four weeks in, the bottom of the table reads:"""],
cellar_items=[
 """<b>yckyb</b> (10th, 0-4). Fewest points, the worst all-play, and the history of 0-4 starts says 0 for 5. yckyb has finished last twice already (2021, 2022), tied for the most in league history.""",
 """<b>anth0nyng</b> (9th, 1-3), the defending champion, with a 27% playoff shot and a 16-20 all-play. The worst title defense in league history is 9th, and it was anth0nyng's last one.""",
 """<b>Abadahh</b> (improbably 2-2), the second-worst team by all-play, insulated by two wins by a combined 7.52 points. Last place in 2020 and 2023.""",
 """<b>Last year's last-place finisher:</b> donblood, now in first. The cellar is not destiny.""",
],

rivalry_items=[
 """<b>The scoring crown is a photo finish.</b> anth0nyng leads all-time with 14,214.60 points. jigri has 14,198.98. That is <b>15.62 points across seven seasons</b>, one decent quarter. It could flip this week.""",
 """<b>Most career wins:</b> PutItOnYa (68-45, .602), then jigri (65) and anth0nyng (64). jigri and anth0nyng also share the title lead with two each.""",
 """<b>The most-played rivalry</b> is anth0nyng vs jigri: 17 games, jigri leads 9-8, and they've split four playoff meetings 2-2.""",
 """<b>Most lopsided:</b> jigri is 10-1 against Abadahh and has won six straight. PutItOnYa is 11-3 against Abadahh (eight straight) and 10-2 against yckyb.
 dexclusive is 8-2 against keveezy, and anth0nyng is 10-3 against lmphm.""",
 """<b>The record nobody wants:</b> Abadahh has 66 career losses and a .371 win rate, both the worst in league history.""",
],

odds_intro=["""Four thousand simulated rest-of-seasons from current records: the live Almanac's own simulation, same seed, so these are the numbers on the site. Six of ten make it. Ten weeks to go."""],
odds_after=["""The sim and the standings disagree about who's best: <b>jasonle at 2-2 is the title favorite at 30%</b>, ahead of all four 3-1 teams. And keveezy at 1-3 is a 62% bet to make the
playoffs, better than anth0nyng, dexclusive or Abadahh. Five of ten teams are above 85%, so the real race is for the sixth spot."""],

ends=[
 """<b>Still zero trades.</b> Four weeks in, not one deal. The Week 11 deadline is the only clock.""",
 """<b>dexclusive leads the FAAB spending</b> ($45), with keveezy ($35) next. donblood, PutItOnYa, lmphm and Abadahh still haven't spent a dime. The best pickup was free: dexclusive's Bryce Young, 60.18 started points.""",
 """<b>Bench crime of the month:</b> jasonle's half-point loss in Week 3 with Michael Wilson's 25.90 on the bench. Honorable mention to yckyb, whose Week 1 starting tight end scored zero while Isaiah Likely put up 27.80 on the bench. That one was the difference between 0-4 and 1-3.""",
],
closer="""donblood went from last to first, jasonle is the best team at .500, and the defending champion is 1-3 in a league that has never had a repeat champion.
Five of seven titles have gone to a team that started 3-1, and four teams are sitting there now. History says one of them is the champion. The scores say it might be jasonle anyway.""",
footer="""Records, lineups, injuries, draft picks, FAAB and every weekly result pulled live from Sleeper through Week 4 (injury designations as of Oct 6).
History from the combined Yahoo (Nooblets, 2019 to 2023) and Sleeper (2024 to 2025) archive: 7 seasons, 529 games, consolation games excluded. Power-ranking movement is measured against last issue.
Odds from the live Almanac's 4,000 simulated rest-of-seasons, a forecast, not a promise.""",
)
