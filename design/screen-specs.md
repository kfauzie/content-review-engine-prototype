# Design (pm-4): AI performance benchmark, round 5

> Illustrated. The counts are made up for a 1,000-transcript sample (Kevin's call). The examples are in `data/examples_illustrative.json`: 4 quote the synthetic test set word for word, and 14 were written for the design. All call dates are invented. Nothing here is Dialectica's data.

| Page | Shows | Design |
|---|---|---|
| 1. Benchmark | **Header:** "AI performance benchmark" in large type, then "1,000 transcripts · 262 issues found by human reviewers · AI caught 239 · missed 23". "Missed 23" is the most prominent number. **Secondary, top right:** 187 unneeded flags, tagged "Operational cost". **Missed issues by type:** high priority (material non-public information, current-employer confidential, declaration conflict) in red-brown, then medium and low priority (source disclosure, former-client confidential, personal data) in slate. Each category shows its name in larger type, a short description in smaller type, and the missed count. Below it is a carousel of 3 example cards at a time, each with the quote, the expert's initials and name, and the call date and timestamp | [1-summary.png](1-summary.png) |
| 2. Transcript | Opened from a card. **Call context:** topic, expert, call date, role and what they declared. **The full transcript,** with the missed passage highlighted, its issue type labelled, the reviewer's comment and why the AI didn't flag it | [2-transcript.png](2-transcript.png) |

**Examples per category:** never more than the category's made-up miss count. Personal data has 7 (11 missed), source disclosure 5 (6), former-client confidential 4 (4), material non-public information 1 (1), current-employer confidential 1 (1), and declaration conflict none (0). The generator checks this.

**The transcript page:** uses synthetic transcript 5. The made-up rules engine missed the passage at 01:24 (`notebooks/eval.py`). The reviewer's comment is the answer key's rationale for that passage, and the root cause is my judgement.

**For the build:** full transcripts exist only for the 4 test-set examples. Cards written for the design have no transcript behind them yet.
