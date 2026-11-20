# Design (pm-4): AI performance benchmark, round 6

> Illustrated. The counts are made up for a 1,000-transcript sample (Kevin's call). The examples are in `data/examples_illustrative.json`: missed issues and unneeded flags. 7 quote the synthetic test set word for word, and 25 were written for the design. 32 people, no one appears twice. All call dates are invented. Nothing here is Dialectica's data.

| Page | Shows | Design |
|---|---|---|
| 1. Benchmark | **Header:** "AI performance benchmark" in large type, then "1,000 transcripts · 262 issues found by human reviewers · AI caught 239 · missed 23". "Missed 23" is the most prominent number. **Secondary, top right:** 187 unneeded flags, tagged "Operational cost". **Missed issues by type:** high priority (material non-public information, current-employer confidential, declaration conflict) in red-brown, then medium and low priority (source disclosure, former-client confidential, personal data) in slate. Each category shows its name in larger type, a short description in smaller type, and the missed count. Below it is a carousel of 3 example cards at a time, each with the quote, the expert's initials and name, and the call date and timestamp | [1-summary.png](1-summary.png) |
| 2. Transcript | Opened from a card. **Call context:** topic, expert, call date, role and what they declared. **The full transcript,** with the missed passage highlighted, its issue type labelled, the reviewer's comment and why the AI didn't flag it | [2-transcript.png](2-transcript.png) |

**Round 6 changes:**
- **More examples in the top two missed categories.** Made-up misses moved to them, with the total kept at 23: material non-public information 5, current-employer confidential 4, declaration conflict 0, source disclosure 4, former-client confidential 3, personal data 7. Every miss has an example card, and each card is from a different person.
- **Unneeded flags by category.** 187 split across the six types (60, 30, 9, 8, 20, 60) as a secondary amber section. The top two categories have carousels, and each card says why the reviewer cleared it. The rest show a count only.
- **Clickable cards.** Only cards in the top categories (material non-public information and current-employer confidential) open a transcript, in both sections. They carry an arrow.
- **The transcript page.** The reviewer's comment is blue. The AI analysis is purple, titled "Why the original AI didn't flag it" with the subtitle "Analysis by an independent agent, from the original AI's log".

**The transcript page:** uses synthetic transcript 5. The made-up rules engine missed the passage at 01:24 (`notebooks/eval.py`). The reviewer's comment is the answer key's rationale for that passage, and the root cause is my judgement.

**For the build:** 18 clickable cards need a transcript (9 missed, 9 unneeded). The test set covers 5 of them (transcripts 2, 3, 4, 5 and 7), so 13 short synthetic transcripts still need writing, each with a reviewer comment and a root cause.
