# Design (pm-4): AI performance benchmark, round 4

> Illustrated. The counts are made up for a 1,000-transcript sample (Kevin's call). The transcript is from a synthetic test set. Nothing here is Dialectica's data.

**Wording:** everything reads as caught against missed, out of what reviewers found. No "real issues", no percentages, no rates.

**Look:** a dashboard. Light grey background, white cards, red for missed, amber for unneeded flags. Hierarchy comes from type size, with minimal text.

| Page | Shows | Design |
|---|---|---|
| 1. Benchmark | **Above the headline:** "AI performance benchmark · 1,000 transcripts". **Headline:** "Reviewers found 262 issues. The AI caught 239 and missed 23." with a bar split into caught and missed beneath it. **Card "Issues by type":** high priority first (material non-public information, current-employer confidential, declaration conflict), then other (source disclosure, former-client confidential, personal data). Each row has the name, a one-line description and "caught X of Y, missed Z". A row opens in place to list its missed examples. **Small amber card:** "The AI also flagged 187 passages reviewers cleared." | [1-summary.png](1-summary.png) |
| 2. Transcript | Opened from a missed example. **Call context:** the call topic, the expert, their role and what they declared. **The full transcript,** with the missed passage in red and the issue type labelled beside it | [2-transcript.png](2-transcript.png) |

**Numbers:** `design/fill_check_mock.py` holds the made-up figures for each category (found by reviewers, missed by AI), works out caught as found minus missed, and checks the totals are 262, 239 and 23.

**The example:** synthetic transcript 5 at 01:24, which the made-up rules engine missed when scored against the test set's answer key in `notebooks/eval.py`.
