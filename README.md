# rugby-conversion

Does try location matter? Analysis of conversion probability and expected points by lateral try position in rugby union.

## Data

**Quarrie & Hopkins (2014)** — 13,338 conversion attempts from international and top-tier matches, 2000–2012, distributed via [Wharton Sports Analytics and Business Initiative (WSABI)](https://wsb.wharton.upenn.edu/).

Paper: [Evaluation of goal kicking performance in international rugby union matches](https://pubmed.ncbi.nlm.nih.gov/24598404/) — Quarrie & Hopkins, *Journal of Science and Medicine in Sport*, 2015.

Data file: `goal_kicking_data.csv` (not in public repo).

## Files

| File | Description |
|---|---|
| `goal_kicking_data.csv` | Raw data (private) |
| `conversion_probability.py` | Conversion rate vs lateral distance — basic curve |
| `expected_points_pitch.py` | Expected points visualised on a top-down pitch |
| `naive_model_pitch.py` | Illustrative naive mental model for comparison |
| `kicking.R` | R script (exploratory) |
| `blog.md` | Full blog post source |
| `blog_outline.md` | Post outline / notes |

## Public repo

Scripts and plots only (no data): [rugby-conversion-public](https://github.com/tyler-martin-12/rugby-conversion-public)
