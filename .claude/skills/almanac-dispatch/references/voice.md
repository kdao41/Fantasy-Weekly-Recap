# Voice

The Almanac reads like a sharp sports column written by someone in the league: confident, a little mean,
always backed by a number. It roasts records, not people.

## What makes a story

- **A gap between record and all-play.** "4-0 on a .545 all-play" or "1-3 with the second-best all-play".
  The luck map is the spine of every early-season issue.
- **Precedent.** The full archive is the edge over the live page. "Nine teams have started 0-4. None made the
  playoffs." "Eight 4-0 starts, eight playoff trips, zero titles." Use `history_comps` and `starts_like_these`.
  They count only seasons with this league's teams and playoff spots (the digest lists them), so say so when it
  narrows the sample: "since Aggtown went to six playoff teams".
  Give both faces when precedent splits (a 1-3 team that won it all and one that went 3-11).
- **Swings.** Last year's last place now in first; the defending champion winless; the worst start ever
  followed by an unbeaten one.
- **Decisions.** Lineup calls that cost a game (`costly_crimes`) turn "unlucky" into "self-inflicted".
- **Records in reach.** Career wins or losses near a round number, a scoring crown within one good quarter,
  a streak in this week's series.
- **Corrections.** When the archive contradicts something an earlier issue said, say so plainly:
  "The old Almanac called this series 1-0. With the archive, lmphm leads 7-1."

## Shape

- **Lede:** 4 to 6 sentences, the three or four biggest stories in one breath, ending on a hook.
  It opens with a drop cap, so the first word should be strong.
- **Section intros:** one or two sentences explaining the measure in plain words, then the table or chart.
- **After a table or chart:** one short paragraph that tells the reader what to see, with **bold** on the
  key phrase ("**lmphm sits alone at the top**").
- **Power-ranking blurbs:** 2 or 3 sentences: verdict, the numbers that justify it, the star player with
  points in parentheses, injuries in red (`<span class="inj">…</span>`), one history note when it earns it.
- **Cards** (precedent feature): a tag ("THE 0-4 FLOOR · keveezy"), a big number, a one-line headline, a
  dense paragraph.
- **Closer:** three short sentences that set up next week. "Regression is coming for somebody."

## Phrases the league knows

"Above the line you're a thief. Below it, you've been robbed." · "the luckiest .500 team in history" ·
"Something has to give." · "a forecast, not a promise" · "the record nobody wants" · "Holding the sign" ·
"Bench crime of the week" · "The scoreboard has lied about both of them, and the sim knows it."
Reuse sparingly; don't paste the same line into every issue.

## Hard rules

- **No em dashes, and no en dashes standing in for one.** The legacy PDFs used them heavily; we don't. Use a
  colon, comma, parentheses or two sentences. Write ranges as "Weeks 1 to 4".
- **Pronouns:** managers are referred to by handle or as "they". Never infer he or she from a name.
- **Every number traces to the digest.** No rounding drift between the prose and the tables on the same page.
- **Points to two decimals** (161.62, 0.28, 21,675.52), as Sleeper scores them. Take the exact value; never pad
  a rounded one with a zero. Percentages and records keep their own formats.
- **Scoring eras:** passing TDs were 5 points in Aggtown through 2021. Compare old scores loosely and say so
  when an all-time score rank is quoted.
- **Injuries:** use Sleeper's designation as of the fetch date (Out, IR, Questionable, Doubtful). Don't
  describe the injury itself unless it's in `injury_body_part` / `injury_notes`, and cite outside reporting
  in the footer if you use any.
- Handles are written exactly as Sleeper shows them (lmphm, PutItOnYa, anth0nyng).
