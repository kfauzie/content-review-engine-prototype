# Design (pm-4): AI review check

> Illustrated. The counts are made up for a 1,000-transcript sample (Kevin's call), and the example comes from a synthetic test set. Nothing here is Dialectica's data.

The story: before we let the AI do more, check it against what reviewers already decided. There are three levels, each a click deeper. The numbers are raw counts and percentages, all counted in transcripts, with no status labels.

| Level | Shows | Design |
|---|---|---|
| 1. Summary | The title, "AI review check: 1,000 reviewed transcripts". **Missed by AI** comes first and largest: 23 transcripts, 8.8% of 262 real issues, and "High priority missed by AI: 2 (goal: 0)". Then a table in two groups, high priority (material non-public information, current-employer confidential, declaration conflict) and other (source disclosure, former-client confidential, personal data). Each row has a one-line description, missed, miss rate (missed ÷ real issues of that type) and share of all misses. **False alarms** come last, smaller and collapsed by default: 187, 43.9% of 426 AI flags. When opened, it has the same table structure (false alarms, rate against AI flags, share) | [1-summary.png](1-summary.png) |
| 2. Category | A category's description and stats line, then its examples: the topic, the time and the sentence with the problem | [2-category.png](2-category.png) |
| 3. Example | Two parts only: **Transcript** (the quote with speaker and timestamp, plus the question before it) and **Why the AI missed it** (the root cause) | [3-example.png](3-example.png) |

**Numbers:** `design/fill_check_mock.py` holds the made-up inputs for each category (real issues, missed, AI flags, false alarms) and computes every rate and share. It checks that rightly flagged plus missed equals real issues in every category, and that the totals are 23, 187 and 2. It assumes no transcript has misses in two categories.

**The example:** synthetic transcript 5 at 01:24, quoted word for word. A made-up rules engine missed it in `notebooks/eval.py`. The root cause is my failure-analysis judgement.

**Design system:** neutral defaults. Red is missed by AI, amber is false alarm.
