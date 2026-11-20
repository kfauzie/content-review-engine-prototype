# Run: Dialectica Legal & Compliance, content review engine

> **All made up.** The call is a role-play, the transcripts are synthetic, and nothing is known about Dialectica's current tool. Kevin plays the Lead AI Product Developer reporting to Dialectica's Chief Legal & Regulatory Officer. The transcripts, experts and companies are fictional (Kevin's test set). Nothing here is Dialectica's data, policy or product.

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
| 3. Interview | Kevin | Notes in the Notion page | Done |
| 4. Research synthesis | `pm-1-data-discovery` (Answer) | Below; code in `notebooks/synthesis.py` | Done |
| 5. Solution concept | `pm-3-problem-to-solution-concept` | [Notion page](https://app.notion.com/p/41e8f31ef05f8137b4bbddec89a6656c): eval plan and dry run, solution after the eval | Revised |
| 6. Design | `pm-4-solution-design` | AI performance benchmark: [benchmark](design/1-summary.png), [transcript](design/2-transcript.png); spec in [design/screen-specs.md](design/screen-specs.md) | In review, not built |
| 7. Prototype | `pm-5-mvp-build` | | |
| 8. MVP review | `pm-6-mvp-review` | | |

## 1. Data review (pm-1, Initial review)

**The data:** 8 transcripts of 2:45 to 5:10 minutes each. Together they hold 51 expert answers (1,885 words) and 59 interviewer questions. Every transcript comes with the expert's profile and their onboarding declaration (where they work, when they left, what they may not discuss).

**First five rows** (expert answers): T1 00:21, 01:03, 01:44, 02:39 and 03:23. These are 42 to 73 words each, on UK grocery supply chains, and none has a marker.

**Data quality:**
- All 8 transcripts have a profile and a declaration, and the timestamps run in order.
- One profile (T6) takes its dates "per declaration": the only record of when she left comes from the expert herself.
- None of this changes the findings.

**How big the base is:** 8 synthetic transcripts, written as a test set (not Dialectica's). They show the kinds of passage reviewers meet, not how often each occurs. Every share below describes this sample, not Dialectica's volumes. The markers in Finding 1 are plain patterns I wrote after reading these transcripts, so how often they hit here is no evidence of how they'd do on real calls.

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

## 3. Interview
Kevin ran a role-play call with "Jason", and the notes and transcript are in the discovery page in Notion. **Treat it as hypotheses, not discovery.** Nothing below is a quote from the real Jason.

## 4. Research synthesis (pm-1, Answer)
Every number comes from `notebooks/synthesis.py`. Each hypothesis from the role-play was checked on its own. **The transcripts are synthetic test data, written for this exercise, so they can't support or rule out a hypothesis about Dialectica.** The verdicts only say whether the test set agrees with each hypothesis, which shows whether it's a fair test set for the eval.

| # | Hypothesis (role-play) | Choices made | Result | Verdict |
|---|---|---|---|---|
| 1 | Most of a transcript is harmless, but nobody knows which part matters until they've read it | Measured by expert answer and by word, using the four markers from Step 1 | 9 of 51 answers (17.6%) and 374 of 1,885 words (19.8%) carry a marker | **Consistent** with the test set (not evidence) |
| 2 | Experts often mention companies, and each mention sends the reviewer to the profile system | Counted answers that name any company | 8 answers, in 6 of 8 calls | **Consistent** with the test set (not evidence). The time cost can't be tested here |
| 3 | Personal data is usually a simple redaction | Answers naming a private person, and whether the same answer cites an insider source | 2 answers. T8 names a person. T6 names the insider who passed on information, so it's about the source, not only personal data | **Not consistent**: in the test set, 1 of 2 is more than a redaction |
| 4 | The current tool flags every company mention | Not testable | The data holds no output from the current tool | **Unknown**: nothing is known about the current tool. The engine in the eval demo is made up |

**Surprise:** in 1 answer, a current employee talks about their employer as "us" without naming it (T3 01:34). A check that starts only when a company is named would miss it.

## 5. Eval demo (after Kevin's feedback on the first concept)
`notebooks/eval.py` scores each expert answer against the answer key as rightly flagged, a false alarm or missed, by issue type. The fourth outcome, missed by the human, needs a separate human verdict, which this data doesn't have.

**This demonstrates the method, not a result.** The engine is made up, not a model of Dialectica's tool (nothing is known about how that works). It flags every answer that names a company, and the test transcripts were written with issues that don't name companies. So its score (3 rightly flagged, 5 false alarms, 4 missed) is built in, and says nothing about Dialectica's tool.

**Pipeline check only:** `data/eval/ai_reviewer_verdicts.json` holds verdicts written by Claude after it had seen the answer key. They only confirm that the scorer reads verdicts and computes the outcomes. The score isn't reported anywhere.

**Sizing the live test:** zero misses in n real issues of a type shows, with 95% confidence, a miss rate below 3 in n. That means 60 issues for 5%, 150 for 2% and 300 for 1%.

**Blind AI reviewer:** a subagent read only `data/eval/blind_input.md` (made by `notebooks/make_blind_input.py`: no answer keys, no transcript titles) and wrote `data/eval/ai_verdicts_blind.json`.
- **Flags:** all 7 passages the human acted on, each with the same issue type. No false alarms.
- **Actions:** the same as the human on 4 of 7. On the other 3, it rejected transcripts 5 and 8 where the human escalated or redacted, and escalated transcript 6 where the human rejected.

With 7 issues in a synthetic set, this shows the method works end to end, not that the AI is ready.

**Solution concept, revised:** [Notion page](https://app.notion.com/p/41e8f31ef05f8137b4bbddec89a6656c). The order is eval, failure analysis, prioritise, live test, and only then a solution.

## Decisions I made (and what I turned down)

| Decision | Why | What I turned down |
|---|---|---|
| Use Kevin's 8 transcripts, not data I generate | Real-looking passages beat invented volumes, and the test set covers the hard cases (hedges, public figures, declaration conflicts) | A synthetic month of scores and volumes, built before the data arrived |
| Hold back the answer key | Reviewers don't get one. Discovery should see what they see, and the key stays clean for testing the build | Reading the key's categories and expected actions into the findings |
| Eval before any solution (Kevin's feedback) | We don't know the real problem yet; an eval by issue type shows whether the tool is too cautious, not cautious enough, or keyed on the wrong signal | The first concept, which recommended declaration-aware review on role-play evidence |
| Present the dry run as a demo of the method, and drop the reviewer's score (Kevin's feedback) | The stand-in's misses were built into the test set, and a score from a reviewer that saw the answer key would invite the wrong questions | Leading with "missed 4 of 7" |
| Rulings on disagreements in the eval | Today's reviewers miss things too, so their verdicts can't count as the truth on their own | Scoring the tool against analysts' verdicts as they stand |
| Caught against missed, out of what reviewers found; issues by type, opening in place; full transcript with call context; dashboard look (Kevin's round 4) | Plain wording needs no "real issues" or rates; one page plus the transcript | Separate category pages, per-category unneeded flags |
| Frame it as an AI performance benchmark; name the errors by cost (missed issues: compliance risk; unneeded flags: operational cost); counts only, no percentages or targets; full transcript with every passage marked (Kevin's round 3) | The page should read on its own, without meta text, and show where the AI is right as well as wrong | Rates, shares, the zero target, a single-example detail page |
| Summary first, details one click deeper; misses by category, split into high priority and other, against a goal of zero high-priority misses (Kevin's feedback) | The decision is per category, and the reader sees the summary before the detail | A single screen listing every miss |
| One screen, one story (Kevin's feedback): three numbers and the list of AI misses | The point is the check before the AI does more; the reviewer workflow, declarations and rulings were cut | A review screen plus a scorecard funnel with drill-downs |
| Made-up top numbers for a 1,000-transcript sample (Kevin's call) | It shows the scale the check runs at; labelled as illustrative | Numbers computed from the 8-transcript test set |
| No estimates of time saved | No measured baseline; the figures came from a role-play | The 45-to-26-minute estimate and the hours saved per 1,000 transcripts |
| Findings as questions, not answers | 8 transcripts can't size the problem; the interview has to | Proposing an AI and human split before discovery |
