# Blog Post Outline: Is Where You Score a Try Worth More Than You Think?

---

## Hook
- Set the scene: a winger dives over in the corner, crowd goes wild — but the conversion is a near-formality in the commentary box. Is it?
- Tease the finding: the penalty for scoring wide is smaller than most people assume, and almost entirely offset by elite kickers' ability to pick their spot

---

## 1. The Rules (for non-rugby readers)
- A try = 5 pts, scored by grounding the ball anywhere between the touchlines
- After a try, the scoring team gets a conversion attempt worth 2 additional pts
- **Key rule**: the kick must be taken from a point in line with where the try was grounded — but the kicker can move as far back from the try line as they want
- This is the crucial asymmetry vs. American football: the kicker has a continuous optimisation problem

---

## 2. Why Lateral Position Should Matter (the geometry)
- Brief intuition: wider try → narrower angle to the posts → harder kick
- Classic "optimal angle" result: there's a distance back that maximises the subtended angle for any lateral offset
- But geometry is just the floor — kicker skill, wind, pressure, and fatigue all sit on top

---

## 3. The Data
- Source: Quarrie & Hopkins dataset (via WhartonSABI), 13,338 conversion attempts from international and top-tier matches, 2000–2012
- Each attempt already reflects the kicker's own choice of distance back — so the empirical success rate is the best-case outcome for a given lateral position, not a fixed-distance estimate
- Note on age: this is 20+ year old data. Kicking technique and sports science have evolved significantly — modern specialists (e.g. dedicated kicking coaches, GPS-tracked biomechanics) may push these numbers up across the board, and the touchline penalty may be even smaller today

---

## 4. The Finding: The Plot
- Embed `expected_points_pitch.png`
- Walk through the curve: 6.64 expected pts under the posts → 5.94 pts at the touchline
- The gap is only ~0.7 pts — less than the value of a single penalty goal (3 pts)
- Contrast with the intuitive assumption (and naive geometric model) that touchline conversions are nearly impossible

---

## 5. Should Players Try to Score More Centrally?
- The ~0.7 pt swing sounds small, but at elite level margins matter
- However: **players rarely choose where to score** — tries are opportunistic. The corner is often the only gap available
- The more interesting question is for attacking line breaks near the posts: is it worth a player cutting inside to score more centrally vs. taking the easier path to the corner?
- Rough answer: the conversion bonus from going central is worth less than half a point — almost certainly not worth taking a harder line or risking the try at all
- **Takeaway**: trust your winger, trust your kicker

---

## 6. The American Football Comparison
- In the NFL, the PAT (point after touchdown) is kicked from a fixed spot — the 15-yard line — regardless of where the TD was scored
- Result: whether a receiver catches in the back of the end zone or dives the corner pylon, the conversion odds are identical (~94% at NFL level)
- Rugby's moving-kick rule is a deliberate design choice that partially compensates for wide tries — and the data suggests it works well
- Interesting side note: most NFL touchdowns happen on the edges/corners (slant routes, fades, scrambles to the pylon) precisely because defenses are compressed centrally — yet it costs the offense nothing on the PAT. Rugby defenders don't have this luxury; conceding a corner try is still meaningful.

---

## 7. Caveats & Open Questions
- **Data age**: 2000–2012 predates modern kicking specialists and GPS biomechanics analysis
- **Aggregation**: we're collapsing all kickers — a Beauden Barrett vs. a prop filling in are averaged together
- **Conditions**: no wind/weather controls in this dataset
- **Selection bias**: kickers may be more likely to attempt from optimal positions in comfortable games (score effects)
- What would this look like broken down by kicker, competition, or era?

---

## 8. Conclusion
- The corner try penalty is real but small — roughly half a point of expected value
- Elite kickers effectively arbitrage away most of the geometric disadvantage by choosing their distance back carefully
- The bigger lesson: rugby's conversion rule is cleverly designed to keep the conversion relevant without making try location overly deterministic
- Code and data: [github.com/tyler-martin-12/rugby-conversion](https://github.com/tyler-martin-12/rugby-conversion)
