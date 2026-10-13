COPY = dict(
doc_title="The Aggtown Almanac, Week 6 2026",
kicker="WEEK 6 DISPATCH · FIVE WEEKS IN · THE LOGJAM EDITION",
title="The Aggtown<br>Almanac",
subtitle="State of the league after Weeks 1 to 5 · 2026 season · checked against every game since 2010",
lede="""From 0-5 to 5-0. A year after the second-worst five-week all-play in league history <span style="white-space:nowrap">(4-51)</span>, lmphm is the only unbeaten
team and just hung 187.70 on wabaki, the season's high score. Seven teams are stuck at 3-2 behind them, and in seasons built like this one, 7 of 12
such starts made the playoffs. At the bottom, the champion is 0-5 and wabaki is 1-4 with the third-best all-play in the league; no 0-5 or 1-4 team
in those seasons got in. Next for the unbeaten: jimbo817, who won the last meeting by 36.52.""",

standings_intro=["""Record is what happened. All-play (your record if you played all eleven opponents every week) is what should have happened.
The last column counts how many teams with the same record after five weeks made the playoffs, in seasons built like this one only: twelve teams
and six playoff spots, which means 2013 and 2022 to 2025.""",
"""That is a correction. Last issue's column pooled every season from 2015 on, including seven with eight playoff teams, which is where "31 of 35"
for a 3-1 start and "11 of 33" for 1-3 came from. Of the five Yahoo seasons now added (2010 to 2014), only 2013 had this shape."""],
standings_cap="Aggtown through Week 5 · sorted by record, then points · same start: record after Week 5, in 2013 and 2022 to 2025",
standings_after=["""Read the last column top to bottom. lmphm's 5-0 has two precedents in this format: lmphm's own 2022 team made the
playoffs, and wabaki's 2013 team did not. The seven 3-2 teams have a bit better than a coin flip (7 of 12), and Odeh1121 at 2-3 about the same
(10 of 18). Below that the column goes to zero: none of the eight 1-4 starts and none of the five 0-5 starts reached the playoffs."""],

luck_intro=["""Every team by how good its scores have been (all-play, across) against what the scoreboard paid out (actual win %, up).
Above the diagonal you have more wins than your scores earned; below it, fewer."""],
luck_title="The Aggtown luck map · through Week 5",
luck_after=["""<b>Seven teams sit on one line</b>, the 60% row, spread from PutItOnYa's 19-36 all-play to DVTV's 40-15. Same record, very different teams. <b>lmphm is still the luckiest team in the league</b> (1.82 wins above what the
scores earned), with PutItOnYa next (1.27). <b>wabaki is the most robbed by a distance</b>: 2.36 wins short, more than keveezy (1.27 short) at 0-5."""],

feature_title="Five weeks in, five seasons that count",
feature_intro=["""The precedent changes with the column above: these cards count only the five seasons with this league's shape (twelve
teams, six playoff spots): 2013 from the Yahoo years, and 2022 to 2025. It is a small sample, and it has strong opinions at both ends."""],
cards=[
  dict(cls="lucky", tag="THE 5-0 START · lmphm", big="1 of 2",
      hl="Two 5-0 starts in this format before this one. One made the playoffs, and it was lmphm's.",
      body="""lmphm's 2022 team started 5-0 on a 34-21 all-play, went 12-2, took the top seed and finished 4th. The other is the warning:
      wabaki started 5-0 in 2013 on a 32-23 all-play, went 7-6 and finished 10th. This one has the best all-play of the three (35-20) and leads the
      league in points (697.76), with Josh Allen (146.96) at the controls. The real story is the swing: twelve months ago lmphm opened <b>0-5 on a
      4-51 all-play, the second-worst five-week start in league history</b> (only Josh's 3-52 in 2013 was worse), and finished 11th."""),
 dict(cls="robbed", tag="THE 1-4 PROBLEM · wabaki", big="0 of 8",
      hl="No 1-4 start in this format has made the playoffs. None of them had wabaki's all-play.",
      body="""The eight 1-4 teams finished 7th at best. wabaki's 37-18 all-play is the best of the nine, and the closest comp is a warning: donblood
      started 1-4 on 35-20 last season and finished 3-11. But wabaki has the second-most points in the league (673.66), the sharpest lineups (96.2%
      efficiency) and the third-most points scored against it (670.56), and two of the four losses came down to a single lineup call (see Coach ratings).
      The archive says no. The sim says 43.1%."""),
 dict(cls="robbed", tag="THE 0-5 FLOOR · keveezy", big="0 of 5",
      hl="Five 0-5 starts in this format. No playoff trips, and two finished last.",
      body="""The best of them finished 7th (ramzz, 2022, on a 23-32 all-play); the two that finished last were Josh's in 2013 and wabaki's a year ago.
      keveezy's 14-41 is third of the six, with the second-fewest points in the league (527.26) and the most scored against (706.48). Then there is the
      champion's curse: nobody has ever repeated, and no defending champion has finished last. The worst title defense was kholabear's 9th in 2019.
      keveezy's own title defenses ended 3rd (2012) and 8th (2021). The sim gives the champ a 0.4% playoff shot."""),
 dict(cls="good", tag="THE 3-2 LOGJAM · seven teams", big="7 of 12",
      hl="Seven of the twelve 3-2 starts in this format made the playoffs, and two won it. This year there are seven 3-2 teams.",
      body="""Both champions are a warning to the field: jimbo817's own 2013 team started 3-2 on a 37-18 all-play and won the title, and so did
      keveezy's 2025 team on 42-13, the only 3-2 start with a better all-play than DVTV (40-15) and jimbo817 (39-16) have now. At the other end,
      oooEcho started 3-2 in 2024 on 17-38 and finished 9th. The repeat customers are the tell: PutItOnYa and anth0nyng were both 3-2 after five
      weeks in 2024 and 2025 and made the playoffs both years. oooEcho was 3-2 both years and missed both times."""),
],
feature_after=["""One more correction. Last issue said DVTV's all-play was the third-best of the 35 teams who had started 3-1; that sample
pooled every season from 2015 on. In this format, DVTV's 40-15 trails only last year's champion among 3-2 starts. And with the archive back to 2010,
the title count has changed: keveezy (2011, 2020, 2025) and donblood (2012, 2014, 2021) have three each, DVTV and wabaki (2010, 2022) two each, and nobody has ever won
back-to-back."""],

power={
 "DVTV":"""Still #1, on the best all-play in the league (40-15). The 3-2 is last week's matchup of the week going the other way: donblood 153.14,
 DVTV 136.46, the most points in a loss this season. Derrick Henry (111.80) and James Cook (89.30) carry the offense;
 <span class="inj">Jalen Coker Out, Jadarian Price on IR, Ladd McConkey Questionable</span>. Second in title odds (18.4%).""",
 "jimbo817":"""Up one after a 159.40 that buried the champ. A 39-16 all-play, and <span class="good">Jahmyr Gibbs (153.70) has more started points
 than any player in the league</span>. <span class="inj">Caleb Williams and Deebo Samuel Out</span>. Gets the unbeaten team on Sunday, and lmphm is
 11-3 against jimbo817 all-time.""",
 "wabaki":"""Down one, and the most robbed team in the league: 1-4 on a 37-18 all-play, 2.36 wins below what the scores earned. Second in points
 (673.66), first in lineup efficiency, and beaten in Week 5 by the season's high score. Kenneth Walker (110.10) and the $0 pickup Brock Purdy (96.54)
 do the work; <span class="inj">Stefon Diggs Out</span>. Last place a year ago.""",
 "lmphm":"""Fourth in power because the all-play (35-20) still trails the record, but the points have caught up: <b>a league-high 697.76</b> and
 the season's best score, 187.70. Josh Allen (146.96) is the engine, with Javonte Williams (96.00) and Jaylen Warren (83.30) behind him.
 <span class="inj">Aaron Jones Questionable, Jonah Coleman on IR</span>. 66.4% to be the 1 seed.""",
 "donblood":"""Up one after winning the matchup of the week, 153.14 to 136.46. Bijan Robinson (121.20) and Davante Adams (95.10) lead. The bench is
 still the story: <b>146.96 points left there, the most in the league by 47.62</b>, and the league's lowest efficiency (81.7%).
 <span class="inj">Kyle Monangai Out</span>.""",
 "anth0nyng":"""Up two: 3-2 on a 29-26 all-play, about what a 3-2 should look like. Garrett Wilson (86.40) leads, and the $1 pickup Jared Goff has
 started for 68.78. <span class="inj">Breece Hall Out, Alec Pierce on IR, Ollie Gordon Questionable</span>. The career wins leader (140, four clear of
 keveezy), and has beaten this week's opponent, DVTV, five straight.""",
 "bvincenttt":"""Down three, the biggest drop of the week, because a 122.50 was only the eighth-best score of Week 5. Jaxon Smith-Njigba (139.46) is
 <span class="inj">Questionable</span>, and the depth chart is thin: <span class="inj">David Montgomery, Jordan Addison, Roman Wilson and KC Concepcion Out</span>.
 The Week 1 loss to donblood was a lineup call; the Week 5 win over kholabear was someone else's. Call it even.""",
 "oooEcho":"""Down one after the week's low score, 71.40 against PutItOnYa. 3-2 on a 24-31 all-play, and this spot has burned oooEcho before:
 3-2 after five weeks in 2024 and in 2025, no playoffs either time. CeeDee Lamb (115.10) is <span class="inj">Questionable</span>;
 <span class="inj">Travis Etienne on IR, T.J. Hockenson and Marvin Harrison Out, Zach Charbonnet on PUP</span>.""",
 "Odeh1121":"""2-3 on a 19-36 all-play, with Jonathan Taylor (97.40) and Ashton Jeanty (84.60) leading and <span class="inj">A.J. Brown on IR</span>,
 the draft's biggest bust. One precedent worth holding onto: Odeh1121 started 2-3 on a worse all-play (16-39) in 2023, went 9-5 and finished 6th.
 This week, a rematch of last year's title game.""",
 "PutItOnYa":"""Three straight wins and 3-2 on a 19-36 all-play, <b>1.27 wins luckier than the scores</b>, helped by the fewest points against in the
 league (477.88). The last two weeks were real, though (139.18 and 138.62), and Kyren Williams (109.30) and Matthew Stafford (94.98) are a backbone.
 <span class="inj">Quinshon Judkins Questionable, Kenyon Sadiq Out, Jordyn Tyson on IR</span>. Seven seasons, seven playoff trips: the only current
 manager who has never missed.""",
 "keveezy":"""The champ, 0-5 and holding the sign. Amon-Ra St. Brown (104.20) and Trevor Lawrence (89.86) keep it respectable on paper; the rest is
 the injury report: <span class="inj">Saquon Barkley, DJ Moore and Rico Dowdle Out, Josh Jacobs NA, Rashee Rice Questionable</span>. Opponents have
 put up 706.48, the most in the league. 0.4% to make the playoffs.""",
 "kholabear":"""1-4, with the fewest points (510.54) and the worst all-play (13-42) in the league. Week 5 brought the best game of the week, from a
 $0 pickup: Drake Maye, 39.46. kholabear still lost by 7.04, with Woody Marks (12.50) on the bench for Omarion Hampton (4.90).
 <span class="inj">Lamar Jackson, DeVonta Smith and TreVeyon Henderson Out, Jordan Mason on IR</span>.""",
},

motw_head="lmphm (5-0) vs jimbo817 (3-2)",
motw_body=["""The only unbeaten team against the second-best team by all-play (39-16, #2 in power). lmphm brings the most points in the league
(697.76) and the season's high score; jimbo817 brings the league's top-scoring starter, Jahmyr Gibbs (153.70), and a 159.40 of its own last week.
The model barely picks a side: lmphm, 53%.""",
"""History is less shy. <b>lmphm leads the series 11-3</b>, won their one playoff meeting, and has outscored jimbo817 by 11.98 a game
across those fourteen meetings, but jimbo817 won the last one, 145.36 to 108.84 in Week 4 last season. jimbo817 is without
<span class="inj">Caleb Williams and Deebo Samuel (both Out)</span>; lmphm needs Aaron Jones (Questionable) and another week of Josh Allen.
And the record nobody wants is in play: jimbo817 is 108-124 all-time, the most career losses in league history."""],
motw_series="Series: lmphm leads 11-3 · lmphm 1-0 in the playoffs · jimbo817 won the last one",
elsewhere=["""<b>The title-game rematch:</b> Odeh1121 (2-3) vs keveezy (0-5). keveezy won last year's final 114.76 to 81.98 and leads the
series 9-5; the model still makes Odeh1121 a 57% favorite. Lose, and the champ is 0-6.""",
"""<b>The basement:</b> wabaki (1-4) vs kholabear (1-4). wabaki is a 78% favorite, the surest pick of the week, but kholabear won the last
meeting 157.74 to 77.34, and wabaki leads the series only 4-3.""",
"""<b>Streaks on the line:</b> anth0nyng has beaten DVTV five straight; PutItOnYa has beaten donblood three straight."""],

hardware=[
 ("HIGH SCORE OF THE SEASON, AND OF WEEK 5", """lmphm, 187.70 against wabaki, 20th of 2,818 scores in league history. The top eight, led by jimbo817's
 222.66 (2019), all came in 2021 or earlier, under older scoring."""),
 ("LOW SCORE OF THE SEASON", """kholabear, 71.34 in Week 3, a loss to PutItOnYa's 105.20."""),
 ("LOW SCORE OF WEEK 5", """oooEcho, 71.40 in a 67.22-point loss to PutItOnYa, six hundredths from the season low."""),
 ("BIGGEST BLOWOUT", """wabaki 161.62, keveezy 76.68 (Week 4): 84.94, the 23rd-largest margin of 1,409 games in league history."""),
 ("MOST POINTS IN A LOSS", """DVTV, 136.46 in Week 5, beaten by donblood's 153.14 in last week's matchup of the week."""),
 ("CLOSEST GAME", """donblood 119.80, bvincenttt 118.06 (Week 1), with Chuba Hubbard's 23.70 on bvincenttt's bench."""),
 ("DRAFT STEAL / BUST", """Steal: Christian Watson, pick 65 (DVTV), 109.40. Bust: A.J. Brown, pick 21 (Odeh1121), 5.60, on IR."""),
 ("TOP PERFORMANCE", """Tetairoa McMillan, 45.20 (Odeh1121, Week 4). Week 5's best: Drake Maye, 39.46 (kholabear)."""),
],

coach_intro=["""Efficiency is points scored divided by the best lineup possible from the same roster each week. Benched is the gap. Higher efficiency is better.
A note on that column: last issue's bench totals came from an older version of this calculation, so donblood's 134.96 then and 146.96 now are not a
before-and-after. These are the site's current numbers."""],
coach={
 "wabaki":"Best in the league, and still 1-4",
 "lmphm":"Sharp",
 "anth0nyng":"Sharp",
 "jimbo817":"Steady",
 "oooEcho":"Fine; the roster is the problem",
 "bvincenttt":"Week 1's call still stings",
 "Odeh1121":"Middling",
 "DVTV":"Talented, and careless with it",
 "kholabear":"Woody Marks cost Week 5",
 "PutItOnYa":"Sloppy, and winning anyway",
 "keveezy":"One call cost Week 1",
 "donblood":"Most points benched, by a distance",
},
coach_after=["""<b>The lineup calls that flipped results.</b> Five games this season were lost by less than the gap between a benched player and an
eligible starter: bvincenttt in Week 1 (Chuba Hubbard 23.70 on the bench, Jordan Addison 0.00 started, lost by 1.74), wabaki in Week 1 (Stefon Diggs
15.50 over Quentin Johnston 3.70, lost by 9.24) and Week 3 (Zay Flowers 15.40 over Dalton Schultz 6.00, lost by 6.18), keveezy in Week 1 (Jacory
Croskey-Merritt 12.60 over Rico Dowdle 4.10, lost by 3.06), and the new one, <b>kholabear in Week 5</b> (Woody Marks 12.50 over Omarion Hampton 4.90,
lost by 7.04). Fix all five and wabaki is 3-2, keveezy is 1-4, and DVTV, donblood and anth0nyng are each a game worse."""],

cellar_title="The punishment standings",
cellar_intro=["""The stakes for dead last: panhandle in public with an "I SUCK AT FANTASY FOOTBALL" sign until you've honestly earned $50, or one full
day at a bar, open to close. Five weeks in, the cellar reads:"""],
cellar_items=[
 """<b>Holding the sign: keveezy</b> (12th, 0-5). The reigning champion, with the second-fewest points (527.26) and the most against (706.48).
 Of the five 0-5 starts in this format, two finished last (Josh in 2013, wabaki a year ago). No defending champion has ever finished last
 the following season.""",
 """<b>kholabear</b> (11th, 1-4) is the long-term favorite for the sign: the fewest points (510.54), the worst all-play (13-42), a 1.1% playoff shot,
 and a starting quarterback who is Out. kholabear has been here before: 1-4 in 2024 on a 23-32 all-play, finished 3-11 and 11th. Four of the eight 1-4
 starts in this format finished 11th or 12th.""",
 """<b>wabaki</b> (10th, 1-4) finished last in 2025 and sits two spots from the bottom again, but no team in the league has been more robbed, and the sim
 has wabaki at 43.1% to make the playoffs.""",
 """<b>Sign history:</b> oooEcho has finished last three times (2018, 2020, 2021), the most in league history, and posted Week 5's low score (71.40).
 At 3-2, the sign is a long way off. For now.""",
],

rivalry_items=[
 """<b>Correction on the champ's rivalry.</b> Last issue had keveezy leading bvincenttt 7-6 all-time. With the archive back to 2010,
 <b>keveezy leads 12-7</b>, though bvincenttt has won the last four (including Week 3's 143.74 to 108.88); they are 1-1 in the playoffs.""",
 """<b>Career wins:</b> anth0nyng leads with 140, four clear of keveezy (136), with donblood third (128). DVTV is 98-98, two wins from 100, and plays
 anth0nyng this week. Among current managers, PutItOnYa owns the best career win rate (.585).""",
 """<b>The record nobody wants:</b> jimbo817 has 124 career losses, the most in league history and three more than donblood (121), and draws lmphm
 this week. Among current managers, the worst career win rate belongs to oooEcho (.414), with jimbo817 next (.466).""",
 """<b>The scoring crown:</b> donblood leads all-time with 30,120.80 points, the only manager past 30,000, 311.27 clear of keveezy (29,809.53),
 with anth0nyng (29,516.94) third.""",
 """<b>Most lopsided active rivalries:</b> DVTV and lmphm are both 8-2 against wabaki (lmphm with five straight), and wabaki is 12-5 against keveezy.
 lmphm is 11-3 against jimbo817 and 11-4 against donblood; keveezy is 11-4 against oooEcho. Last week's matchup of the week pushed donblood to <span style="white-space:nowrap">13-5</span>
 over DVTV. Four series have reached 24 meetings, the most in league history, and the even one is keveezy vs jimbo817: 12-12, and 3-3 in the playoffs.""",
],

odds_intro=["""Four thousand simulated rest-of-seasons: the live Almanac's own run, same seed, so these are the numbers on the site. Six of twelve make it.
Nine weeks to go."""],
odds_after=["""<b>lmphm is a 99.3% playoff bet</b>, 66.4% for the 1 seed and the title favorite at 29.5%, ahead of DVTV (18.4%) and jimbo817 (14.9%).
The row that argues with the archive is wabaki: 43.1% to make it from 1-4, something no 1-4 team in this format has done. At the bottom, kholabear (1.1%)
and keveezy (0.4%) are playing for the sign. A forecast, not a promise: the model's weekly picks are 10 for 24 since Week 2."""],

ends=[
 """<b>Still zero trades.</b> Five weeks, 87 adds, not one deal. The deadline is Week 11. donblood has 146.96 benched points to spare; kholabear has a
 quarterback Out.""",
 """<b>The one that got away:</b> kholabear drafted Brock Purdy in round 12 (pick 133) and let him go. wabaki picked him up for $0 in Week 1 and has
 started him for 96.54 points, the best add of the season. kholabear's quarterback, <span class="inj">Lamar Jackson, is Out</span>.""",
 """<b>FAAB:</b> anth0nyng is still the biggest spender ($60), with wabaki next ($53). kholabear and PutItOnYa have yet to spend a dime. Correction:
 last issue put donblood in that group; Sleeper has donblood at $10, spent on Tyreek Hill in Week 4.""",
],
closer="""lmphm has the record, the points and an 11-3 series lead going into Sunday. wabaki has the all-play and no precedent.
And seven teams at 3-2 are about to find out which side of the coin they landed on.""",
footer="""Records, lineups, injuries, draft picks, FAAB and every weekly result pulled live from Sleeper through Week 5 (injury designations as of Oct 13).
History from the combined Yahoo (2010 to 2022) and Sleeper (2023 to 2025) archive: 16 seasons, 1,409 games, consolation games excluded. Same-start precedent
counts only seasons with twelve teams and six playoff spots (2013 and 2022 to 2025). Passing TDs were worth 5 points from 2015 through 2021, and scoring
rules before 2015 aren't documented, so compare old scores loosely. Power-ranking movement is measured against the same board a week earlier. Odds from the
live Almanac's 4,000 simulated rest-of-seasons (the same seeded run as the site), a forecast, not a promise.""",
)
