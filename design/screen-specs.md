# Design (pm-4): AI performance benchmark

> Illustrated. The counts are made up for a 1,000-transcript sample (Kevin's call). The transcript is from a synthetic test set. Nothing here is Dialectica's data.

**Headline:** "AI and human review compared on 1,000 transcripts". **Subtitle:** "Where the AI misses issues, and where it over-flags."

**The two errors, named by what they cost:**
- **Missed issues (compliance risk):** a reviewer found an issue the AI didn't flag. This is the main focus.
- **Unneeded flags (operational cost):** the AI flagged something a reviewer cleared. Visible, but lighter and lower on the page.

**Counting rules:** counts only, shown as "x of y", in transcripts throughout. No percentages, no targets, no status labels, no instructions.

| Level | Shows | Design |
|---|---|---|
| 1. Summary | The headline. Missed issues: 23 of 262 real issues, with 2 high priority. Unneeded flags: 187 of 426 AI flags. Then counts by category for each error, high priority first (material non-public information, current-employer confidential, declaration conflict), then other (source disclosure, former-client confidential, personal data). A thin bar shows each count | [1-summary.png](1-summary.png) |
| 2. Category | The category, its count ("1 of 38 real issues missed") and a one-line description, then its transcripts | [2-category.png](2-category.png) |
| 3. Transcript | The whole transcript, with every passage marked: flagged correctly (green), missed (red, with the root cause under it), unneeded flag (amber). A three-item key | [3-transcript.png](3-transcript.png) |

**Where the numbers come from:** `design/fill_check_mock.py` holds the made-up inputs for each category. It checks that rightly flagged plus missed equals real issues in every category, and that the totals are 23 of 262, 187 of 426 and 2.

**Where the transcript marks come from:** synthetic transcript 5, scored by `notebooks/eval.py` against the test set's answer key. The engine is the made-up rules run (it flags company names), because it's the only run with misses and unneeded flags. The blind AI reviewer got all 7 issues right, so its transcripts would show green only. The root cause is my failure-analysis judgement.
