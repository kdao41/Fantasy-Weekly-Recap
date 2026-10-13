COPY = dict(
doc_title="The Sober Gang Almanac, Week 6 2026",
kicker="WEEK 6 DISPATCH · FIVE WEEKS IN · THE TWO HUNDRED EDITION",
title="The Sober Gang<br>Almanac",
subtitle="State of the league after Weeks 1 to 5 · 2026 season · checked against every game since 2019",
lede="""Two hundred points. lmphm scored 200.20 in Week 5, the second-highest total in Sober Gang history, beat winless yckyb by 103.64 and moved into first at 4-1,
a record that has reached the playoffs nine times out of nine. The best team on paper is still jasonle: a 36-9 all-play, the best of any 3-2 start in the archive,
and the most points in the league. keveezy has the best all-play any 2-3 team has ever posted, and yckyb is only the second team in league history to start 0-5,
with its top scorer, Brock Purdy, mostly on the bench. Next week the scoreboard's leader meets the all-play's: jasonle vs lmphm.""",

standings_intro=["""Record is what happened. All-play (your record if you played all nine opponents every week) is what should have happened.
The last column asks the archive: of every team since 2019 that started with the same record, how many made the playoffs. It counts only seasons with ten teams and
six playoff spots, which in Sober Gang is all seven of them."""],
standings_cap="Sober Gang through Week 5 · sorted by record, then points",
standings_after=["""Every 4-1 start in league history has made the playoffs, nine for nine, and two of them won the title. A 3-2 start has gotten in 15 times in 24 tries,
with three champions. A 2-3 start is a coin flip (10 of 19) and has never produced a champion, and four teams are sitting there now. The only previous 0-5 team missed the playoffs."""],

luck_intro=["""Every team by how good it has actually been (all-play, across) against what the scoreboard has given it (win %, up). Teams above the diagonal have won more than their scores earned;
teams below it have earned more than they've won."""],
luck_title="The Sober Gang luck map · through Week 5",
luck_after=["""<b>jigri is the luckiest team in the league</b>: 4-1 on a 24-21 all-play, a win and a third ahead of what the scores earned. lmphm (4-1 on 26-19) is right behind.
Down in the robbed corner, <b>keveezy is 2-3 on a 30-15 all-play</b>, a win and a third short, and jasonle sits a full win below where 36-9 should have it.
donblood has the fairest record in the league: 3-2 on 27-18, luck exactly zero.""",
 # keeps the precedent feature's heading with its cards
 '<span style="display:block;break-before:page"></span>'],

feature_title="Five weeks, seven years of precedent",
feature_intro=["""Five weeks in, five teams are 3-2 or better and five are 2-3 or worse. The archive has something to say about both groups, and about two teams playing better than any Sober Gang team ever has at their record."""],
cards=[
 dict(cls="lucky", tag="NINE FOR NINE · lmphm and jigri", big="9 of 9",
      hl="Every 4-1 start has made the playoffs. Only one had a weaker all-play than these two.",
      body="""lmphm (26-19) and jigri (24-21) are the two luckiest teams in the league, and history doesn't care: all nine previous 4-1 starts reached the playoffs,
      two won the title and none finished last. Only one did it on a weaker all-play than either of them: <b>PutItOnYa in 2023, 4-1 on 23-22, who won the whole thing</b>.
      lmphm got here with the second-highest score in league history. jigri got here with Jared Goff's 115.00 points sitting on the bench all season."""),
 dict(cls="robbed", tag="THE BEST 3-2 EVER · jasonle", big="36-9",
      hl="The best all-play of any 3-2 start in league history, and the second-most points through five weeks.",
      body="""jasonle has 735.96 points, the most in the league and second only to donblood's 772.64 in 2020 for any team through five weeks. The 36-9 all-play ties dexclusive's 2022 start
      for the second-best ever, behind that same donblood team (37-8), and neither of those teams won the title. The 3-2 precedent cuts both ways: the previous best 3-2 start by all-play,
      <b>yckyb in 2021 (32-13), finished last</b>. The next best, keveezy in 2019 (31-14), won the championship. The sim makes jasonle the title favorite at 28.3%."""),
 dict(cls="robbed", tag="THE BEST 2-3 EVER · keveezy", big="30-15",
      hl="The best all-play of any 2-3 start in league history. No 2-3 team has ever won it.",
      body="""keveezy has the second-best all-play in the league and the worst luck, a win and a third short of what the scores have earned. Nineteen teams have started 2-3 here:
      ten made the playoffs, three finished last, none won the title. The closest comp is keveezy's own 2024 team, 2-3 on a 27-18 all-play, which finished 6-8 and in last place.
      This version just put up 162.76, the second-best score of Week 5, with Drake Maye (39.46) off the waiver wire for nothing. The sim has keveezy at 76.9% to make the playoffs, up from 62% a week ago."""),
],
feature_after=["""At the other end, <b>yckyb is the second team in league history to start 0-5</b>. The first, Abadahh last year, did it on a 5-40 all-play, the worst start in the archive,
and still finished 4-10 and seventh, not last. yckyb's 8-37 is better than that, but it is also the second-worst five-week all-play on record here, and the sim gives yckyb a 0.4% playoff chance.
Abadahh's 11-34 this year is the third-worst. And the defending champion, anth0nyng, is 2-3 on a 21-24 all-play in a league that has never had a repeat winner."""],

power={
 "jasonle":"""The best team in the league, at 3-2: a 36-9 all-play, 735.96 points, and Jahmyr Gibbs (153.70), the top scorer in the league.
 Won last week's title-game rematch with PutItOnYa by 2.98. <span class="inj">A.J. Brown on IR, Kyle Monangai Out</span>. The 2022 champion.""",
 "keveezy":"""The most robbed team in the league: 2-3 on a 30-15 all-play. Amon-Ra St. Brown (104.20) and Chris Olave (98.70) carry it, and waiver add Drake Maye (39.46)
 had Week 5's best started game. <span class="inj">Saquon Barkley Out, Aaron Jones Questionable, Jadarian Price on IR</span>. The 2019 champion.""",
 "donblood":"""Lost to anth0nyng and slid from first to 3-2, but a 27-18 all-play says this is about right: luck, exactly zero. CeeDee Lamb (115.10) and Derrick Henry (111.80) lead.
 <span class="inj">Lamb and McConkey Questionable, Montgomery and Coker Out, Jordan Mason on IR</span>. The closest comp, anth0nyng last year (3-2 on 27-18), won the title.""",
 "lmphm":"""4-1, first in the standings and fresh off 200.20, but a 26-19 all-play keeps lmphm fourth here. Josh Allen (146.96) is the league's second-highest scorer.
 <span class="inj">DeVonta Smith Out, Jayden Reed on IR</span>. Two playoff trips in seven Sober Gang seasons, and not a single add this year.""",
 "PutItOnYa":"""3-2, and 3.26 points from 5-0: the losses were by 0.28 to jigri and 2.98 to jasonle. The sharpest lineup-setter in the league (94.7%), with Bijan Robinson (121.20) doing the work.
 <span class="inj">Travis Etienne and Jonathon Brooks on IR, Marvin Harrison Out</span>. The career wins leader.""",
 "jigri":"""4-1 on a 24-21 all-play, the luckiest record in the league. Jaxon Smith-Njigba (139.46) is the league's third-highest scorer; Jared Goff's 115.00 sits on the bench, none of it started.
 <span class="inj">JSN and Quinshon Judkins Questionable, Jordan Addison and KC Concepcion Out</span>. Two titles, and runner-up last year.""",
 "anth0nyng":"""The defending champion beat donblood 139.24 to 121.14 and is 2-3 on a 21-24 all-play (38.1% playoff shot). Davante Adams (95.10) and Christian McCaffrey (91.30) lead,
 and free kicker Spencer Shrader has 54.00 started points. <span class="inj">Rashee Rice and Ollie Gordon Questionable, Michael Pittman on IR</span>.""",
 "dexclusive":"""2-3 on a 16-29 all-play, and the only team with two lineup calls that cost games (Weeks 2 and 3). Christian Watson (109.40, a seventh-round pick) and Jonathan Taylor (97.40) lead.
 Biggest FAAB spender ($45). <span class="inj">DJ Moore, Stefon Diggs and Deebo Samuel Out, Zach Charbonnet on PUP</span>.""",
 "Abadahh":"""2-3 on an 11-34 all-play, the worst all-play of any 2-3 start in league history. The two wins came by a combined 7.52 points. Ja'Marr Chase (79.90) and Drake London (76.20) lead a lineup
 without <span class="inj">Breece Hall, TreVeyon Henderson and Quentin Johnston, all Out</span>.""",
 "yckyb":"""0-5, fewest points (509.44), an 8-37 all-play, and a 103.64-point loss to lmphm in Week 5. Brock Purdy is the roster's top scorer at 118.64, and 17.16 of those came in the lineup.
 <span class="inj">Lamar Jackson Out (ankle), De'Von Achane on IR</span>. Runner-up in 2019; last in 2021 and 2022.""",
},

motw_head="jasonle (3-2) vs lmphm (4-1)",
motw_body=["""The best all-play in the league against the best record, and the top two teams in the title odds. jasonle has the points and the sim; lmphm has the wins and,
since Week 5, the second-highest score Sober Gang has ever seen. The model makes <b>jasonle a 57% favorite</b>.""",
"""The series could hardly be closer. lmphm leads it 7-5 and won the last meeting (108.04 to 79.90, Week 14 of 2025), but across all twelve games <b>jasonle has outscored lmphm by 0.64 points</b>,
1,485.96 to 1,485.32. They have never met in the playoffs. Something has to give."""],
motw_series="Series: lmphm leads 7-5 · total points 1,485.96 to 1,485.32, jasonle · never met in the playoffs",
elsewhere=["""<b>Elsewhere:</b> donblood (3-2) gets jigri (4-1) in a rematch of the 2020 final, which jigri won 147.92 to 135.98; jigri leads the series 6-5 and has won three straight.
keveezy (2-3) and PutItOnYa (3-2) are tied 7-7, and keveezy has won the last two, the latest in last year's playoffs (159.28 to 137.62). anth0nyng gets winless yckyb (6-6 all-time),
and dexclusive (7-3 against Abadahh) gets the battle of 2-3s.""",
"""<b>Last week's follow-ups:</b> jasonle beat PutItOnYa 144.18 to 141.20 in the title-game rematch, so PutItOnYa's series lead is down to 8-6. lmphm's win cut yckyb's lead in that series to 6-5,
jigri broke the 6-6 tie with dexclusive, and anth0nyng now leads donblood 7-3."""],

hardware=[
 ("HIGH SCORE OF THE SEASON, AND OF WEEK 5", """lmphm, 200.20 (Week 5). Only one score in the league's 1,058-score history is higher: Abadahh's 212.58 in 2021. Puka Nacua had 37.70 of it.
 donblood's 182.10 from Week 1 is now the season's second-best."""),
 ("LOW SCORE OF WEEK 5", """yckyb, 96.56, on the other side of the 200.20."""),
 ("LOW SCORE OF THE SEASON", """Abadahh, 78.48 in Week 4, a loss to jigri."""),
 ("BIGGEST BLOWOUT", """lmphm over yckyb by 103.64 (Week 5), the third-largest margin in 529 games of league history."""),
 ("MOST POINTS IN A LOSS", """jasonle, 155.46 in Week 1, to donblood's 182.10. Week 5's best losing score: PutItOnYa's 141.20, by 2.98 to jasonle."""),
 ("CLOSEST GAME", """jigri 139.10, PutItOnYa 138.82 (Week 1). Decided by 0.28."""),
 ("DRAFT STEAL / BUST", """Steal: Brock Purdy, pick 149 (yckyb), 118.64 points, fifth among all drafted players. <b>A correction:</b> last issue called Purdy the top scorer of any drafted player.
 He was seventh; he led only the picks from round 6 on. Bust: A.J. Brown, pick 20 (jasonle), 5.60 points, on IR."""),
 ("TOP PERFORMANCE", """Tetairoa McMillan, 45.20 (jasonle, Week 4). Week 5's best: Drake Maye, 39.46 for keveezy in his first week on the roster."""),
],

coach_intro=["""Efficiency is points scored divided by the best lineup possible from the same roster, using Sleeper's own optimal-lineup totals, the same numbers the live Almanac shows.
Benched is the gap. Higher efficiency is better.""",
"""<b>A correction.</b> Last issue's coach table ran on an older lineup calculation that has since been fixed, and it put yckyb's benched total at 102.96 after four weeks. That figure was wrong.
On the corrected measure, through five weeks, yckyb has left 149.66 points on the bench, still the most in the league by a distance."""],
coach={
 "PutItOnYa":"Sharpest in the league, again",
 "lmphm":"Started the 200",
 "Abadahh":"Clean, with less to choose from",
 "anth0nyng":"Fine",
 "donblood":"Good",
 "keveezy":"One call cost Week 1",
 "jasonle":"One call cost Week 3",
 "jigri":"One call cost Week 2; Goff never started",
 "dexclusive":"Two calls cost two games",
 "yckyb":"One call cost Week 1; Purdy mostly benched",
},
coach_after=["""<b>The lineup calls that flipped results.</b> No new ones in Week 5, so the list still stands at six games lost by less than the gap between a benched player and an eligible starter:
yckyb in Week 1 (Isaiah Likely 27.80 over Colston Loveland 0.00, lost by 7.00), keveezy in Week 1 (Chuba Hubbard 23.70 over Saquon Barkley 9.00, lost by 13.36), jigri in Week 2
(Jared Goff 29.78 over Trevor Lawrence 7.16, lost by 4.16), dexclusive in Weeks 2 and 3 (Stefon Diggs, then Brock Bowers), and jasonle in Week 3 (Michael Wilson 25.90 over Tetairoa McMillan 3.70, lost by 0.52).
Flip all six and jigri is 5-0, jasonle 4-1, lmphm 2-3 and Abadahh 0-5.""",
"""<b>The two best late-round picks in the league have spent most of the season on the bench.</b> Brock Purdy (pick 149) has 118.64 points on yckyb's roster, 17.16 of them in the lineup.
Jared Goff (pick 146) has 115.00 on jigri's, none of them in the lineup, while all 89.86 of Trevor Lawrence's points have come as the starter."""],

cellar_title="The cellar",
cellar_intro=["""Five weeks in, the bottom of the table reads:"""],
cellar_items=[
 """<b>yckyb</b> (10th, 0-5), fewest points and a 0.4% playoff chance. The only other 0-5 start, Abadahh's last year, finished seventh, so last place isn't settled yet.
 yckyb has finished last twice (2021, 2022), tied with Abadahh for the most in league history.""",
 """<b>Abadahh</b> (9th, 2-3), the worst 2-3 team by all-play the league has seen (11-34), with an 8.2% playoff chance. Last place in 2020 and 2023.""",
 """<b>dexclusive</b> (8th, 2-3), a 16-29 all-play and 20.5% playoff odds, two lineup calls away from 4-1.""",
 """<b>anth0nyng</b> (7th, 2-3), the defending champion, at 38.1%. No Sober Gang champion has repeated, and the worst title defense so far is ninth, anth0nyng's own in 2022.""",
 """<b>Last year's last-place finisher:</b> donblood, now 3-2 and fourth. 2-3 starts have finished last three times in nineteen, and four teams are 2-3 now.""",
],

rivalry_items=[
 """<b>The scoring crown didn't flip.</b> Last issue said anth0nyng's all-time points lead over jigri (15.62) could go this week. Instead anth0nyng scored 139.24 in Week 5 to jigri's 135.74,
 and the lead grew to <b>19.12</b>: 14,353.84 to 14,334.72. PutItOnYa is third at 14,123.06.""",
 """<b>Most career wins:</b> PutItOnYa (68-46, .596) is two from 70. jigri has 66, anth0nyng 65, and they share the title lead with two each.""",
 """<b>A new nemesis:</b> anth0nyng's Week 5 win made it 7-3 over donblood, two straight. donblood did win their one playoff meeting.""",
 """<b>The most-played rivalry</b> is still anth0nyng vs jigri: 17 games, jigri leads 9-8, four playoff meetings split 2-2. Next is keveezy vs yckyb: 16 games, yckyb leads 11-5,
 but keveezy is 2-1 in the playoffs, the 2019 final included.""",
 """<b>Most lopsided:</b> jigri is 10-1 against Abadahh (six straight), PutItOnYa 11-3 against Abadahh (eight straight) and 10-2 against yckyb, anth0nyng 10-3 against lmphm,
 and dexclusive 8-2 against keveezy (five straight). Going the other way: lmphm is 7-2 against jigri.""",
 """<b>The record nobody wants:</b> Abadahh has 67 career losses and a .368 win rate, both the worst in league history. The next win is career No. 40.""",
],

odds_intro=["""Four thousand simulated rest-of-seasons from current records: the live Almanac's own simulation, same seed, so these are the numbers on the site. Six of ten make it. Nine weeks to go."""],
odds_after=["""<b>The field has split in two.</b> Six teams are at 76.9% or better to make the playoffs; the next, anth0nyng, is at 38.1%. lmphm has the best playoff (96.9%) and 1-seed (34.4%) odds,
but the sim still makes <b>jasonle the title favorite at 28.3%</b>, with lmphm second at 21%. donblood, jigri, PutItOnYa and keveezy are bunched between 10.3% and 13.3%."""],

ends=[
 """<b>Still zero trades.</b> Five weeks, not one deal. The Week 11 deadline is the only clock.""",
 """<b>Free agency:</b> 56 adds so far. dexclusive leads the FAAB spending ($45), keveezy is next ($35); donblood, PutItOnYa, lmphm and Abadahh still haven't spent a dime, and lmphm hasn't made a single add.
 The best pickups were free: dexclusive's Bryce Young (60.18 started points) and anth0nyng's kicker Spencer Shrader (54.00).""",
 """<b>Bench crime of the week:</b> yckyb started DK Metcalf (5.30) and Mike Gesicki (7.40) with Isaiah Likely (32.40) on the bench. It didn't decide anything at a 103.64 margin,
 but Likely has now scored 85.40 for yckyb, only 11.60 of it in the lineup.""",
 """<b>The model's record:</b> 15 of 20 picks right this season.""",
],
closer="""lmphm has the record and the 200. jasonle has the all-play, the points and the best title odds. Next week the scoreboard and the sim settle it head to head.""",
footer="""Records, lineups, injuries, draft picks, FAAB and every weekly result pulled live from Sleeper through Week 5 (injury designations as of Oct 13).
History from the combined Yahoo (Nooblets, 2019 to 2023) and Sleeper (2024 to 2025) archive: 7 seasons, 529 games, consolation games excluded. Coach ratings use Sleeper's optimal-lineup totals;
last issue's coach table used an older calculation, corrected above. Power-ranking movement is measured against last issue.
Odds from the live Almanac's 4,000 simulated rest-of-seasons, a forecast, not a promise.""",
)
