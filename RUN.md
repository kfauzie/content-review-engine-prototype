# Run: Dialectica Legal & Compliance, content review engine

> **Role-play on synthetic data.** Kevin plays the Lead AI Product Developer reporting to Dialectica's Chief Legal & Regulatory Officer. The transcripts, experts and companies are fictional (Kevin's test set). Nothing here is Dialectica's data, policy or product.

## The ask, word for word
> "pretend for this role i am a lead ai developer reporting to chief legal officer. I want to balance between ai and human review. making sure there is never confidential information breach while not passing more to human reviews than needed"

> "pretend there is an existing content review engine but they are not that good and compliance and review still have to review line by line"

> "let's do discovery first"

## Context
- **Company context:** `context/company.md`. This is kept local and not committed. Its External section summarises Dialectica's public compliance framework: Legal & Compliance reviews content line by line, and an AI tool flags high-risk content. That matches the premise above.
- **Data:** `data/synthetic-expert-transcripts.md` contains 8 fictional transcripts (1 of them AI-led). Each has the expert's profile, onboarding declaration and transcript, plus an answer key.
- **The answer key is held back.** Discovery reads only what a reviewer sees. `notebooks/data_review.py` cuts the answer key off before parsing. The answer key is kept as a hidden test set for the build (`pm-5`) and the MVP review (`pm-6`).

| Step | Skill | Output | Status |
|---|---|---|---|
| 1. Data review | `pm-1-data-discovery` (Initial review) | Below; code in `notebooks/data_review.py` | Done |
| 2. Discovery guide | `pm-2-discovery-interview` | [Notion page](https://app.notion.com/p/41d8f31ef05f815a882bd2360ee212a3) | Done |
| 3. Interview | Kevin | Notes in the Notion page | |
| 4. Research synthesis | `pm-1-data-discovery` (Answer) | | |
| 5. Solution concept | `pm-3-problem-to-solution-concept` | | |
| 6. Design | `pm-4-solution-design` | | |
| 7. Prototype | `pm-5-mvp-build` | | |
| 8. MVP review | `pm-6-mvp-review` | | |

## 1. Data review (pm-1, Initial review)

**The data:** 8 transcripts of 2:45 to 5:10 minutes each. Together they hold 51 expert answers (1,885 words) and 59 interviewer questions. Every transcript comes with the expert's profile and their onboarding declaration (where they work, when they left, what they may not discuss).

**First five rows** (expert answers): T1 00:21, 01:03, 01:44, 02:39 and 03:23. These are 42 to 73 words each, on UK grocery supply chains, and none has a marker.

**Data quality:**
- All 8 transcripts have a profile and a declaration, and the timestamps run in order.
- One profile (T6) takes its dates "per declaration": the only record of when she left comes from the expert herself.
- None of this changes the findings.

**How big the base is:** 8 transcripts, written as a test set. They show the kinds of passage reviewers meet, not how often each occurs. Every share below describes this sample, not Dialectica's volumes. The markers in Finding 1 are plain patterns I wrote after reading these transcripts, so how often they hit here is no evidence of how they'd do on real calls.

### Findings

| # | Finding (one number, compared with what) | Why it might matter (guess) | The question it becomes |
|---|---|---|---|
| 1 | **Most answers give a reviewer nothing to stop at.** 42 of 51 expert answers (82.4%) contain none of four markers: a precise figure or period, timing that isn't public yet, an insider source, or a named private person. The other 9 answers hold 374 of the 1,885 words. | Reading every line spends most of the time on answers that are fine. | "In a sample of transcripts, 42 of 51 answers had nothing a reviewer would stop at. What's behind reading every line?" *Follow-up:* "How do you handle a transcript the engine has already flagged today?" |
| 2 | **Whether an answer is fine often depends on who's speaking.** In 4 of 8 calls the expert names their own employer (5 answers). In 2 of those calls the interviewer named the employer first. 3 of the 8 experts still work at the company their declaration covers. | The text alone can't settle these: the same sentence is fine from someone who left in 2021 and a breach from a current employee. | "In half the calls the expert talked about their own employer. How does a reviewer check what they said against their declaration today?" |
| 3 | **Answers that cite a public source still look sensitive.** 3 of the 4 answers that name a public source (investor day, annual results, an earnings call) also contain a precise figure, a date or the expert's own employer. | A check that stops at figures or employer names would stop at public information too. That may be why reviewers don't trust the engine's flags. | "Some answers quote exact figures from an earnings call. What happens today when the engine flags something that turns out to be public?" |
| 4 | **Some risk sits in how the expert knows, not what they say.** 3 answers cite a personal or insider source ("I still talk to people there", "my contact ... told me", "going around internally"), and 2 name a private person. | The problem can be the source, even when the claim sounds vague. | "A few experts said where they heard something. How do reviewers treat the source of a claim, as against the claim itself?" |

### Clarifications to confirm
1. What does the current engine put in front of a reviewer: flags on lines, a category, a score? Could we see a month of its flags next to the reviewers' final decisions?
2. How much content is reviewed in a month (call transcripts, AI interviews, industry reports), how many reviewers are there, and how long does a transcript take?
3. Which outcomes can a reviewer choose (publish, redact, escalate, reject the whole transcript), and who decides to reject one?
4. Are declarations checked against anything, or taken as the expert states them (as with T6's leaving date)?
5. Is 1 AI-led interview in 8 close to the real mix?

### Looked at, nothing to ask about
- **Hedges:** 5 answers have the expert hedging or limiting what they'll say. In some the hedge protects ("I'd rather talk about capabilities than name operators"). In others it comes right before something sensitive. My guess is that a hedge is a signal neither way.
- **The AI-led call:** with only 1 in the sample, there's too little to compare with interviewer-led calls.
- **Recent vs older:** not possible with 8 undated calls.

### Follow-ups Kevin can ask Claude Code
- Run the four markers on a month of real transcripts and compare them with reviewers' decisions.
- Break the current engine's flags down by kind: how many reviewers kept, redacted or escalated.
- Once the call is done, test each claim from the interview against the data (`pm-1` Step 2).

## Decisions I made (and what I turned down)

| Decision | Why | What I turned down |
|---|---|---|
| Use Kevin's 8 transcripts, not data I generate | Real-looking passages beat invented volumes, and the test set covers the hard cases (hedges, public figures, declaration conflicts) | A synthetic month of scores and volumes, built before the data arrived |
| Hold back the answer key | Reviewers don't get one. Discovery should see what they see, and the key stays clean for testing the build | Reading the key's categories and expected actions into the findings |
| Findings as questions, not answers | 8 transcripts can't size the problem; the interview has to | Proposing an AI and human split before discovery |
