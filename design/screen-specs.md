# Design (pm-4): screen specs

> Illustrated on 8 synthetic transcripts. Nothing here is Dialectica's data, policy or tool.

**Revised after Kevin's feedback on the first scorecard:**
- Lead with the review screen, so the numbers can be trusted.
- Then a scorecard that starts from volume, as a funnel per issue type.
- Missed by AI is the primary error and false alarm the secondary, shown separately but connected.
- Raw numbers only: no status labels and no miss-rate bar. No "missed by analysts".
- Every count opens its passages, and a miss carries a root cause and an over-redaction marker.
- The user is to be confirmed.

**Where the AI verdicts come from:** a blind AI reviewer. A subagent saw only `data/eval/blind_input.md`: profiles, declarations and transcripts, with no answer keys and no transcript titles. Its verdicts are in `data/eval/ai_verdicts_blind.json`.

**Where the human verdicts come from:** the test set's answer key.

**The rules baseline:** a made-up engine that flags company names. It's used only in design 3, to show what a miss drill-down looks like, because the blind AI missed nothing in this sample.

**Design system:** Dialectica's isn't available, so these are neutral defaults with one hue per meaning:
- **Red:** missed by AI
- **Amber:** false alarm
- **Purple:** what the AI said
- **Blue:** what the human said
- **Green:** AI and human agree
- **Indigo:** the main action

**Patterns borrowed** (from public help pages and search summaries; product sites couldn't be opened to study screenshots):
- **Counts of agreement with expert labels per criterion, each opening its disagreements:** eval tools such as Langfuse and Pydantic Logfire.
- **The document in the centre, with facts about it in a side card:** Relativity's review interface.
- **Every flag carries an explanation of where the risk is:** Global Relay.

## Screen 1: Review screen ([design/1-review.png](1-review.png))

**User:** a compliance reviewer checking the AI's work.
**Job to be done:** check, passage by passage, what the AI flagged and why, against the human verdict.

| | |
|---|---|
| **Example input** | Synthetic transcript 5 (medical devices): its 6 expert answers, the profile and declaration, the blind AI's verdicts and the human verdicts |
| **Expected output** | Every expert answer with the AI's verdict and reason, and the human's verdict, side by side. The words the AI relied on are highlighted, in the passage and in the declaration. An outcome on each answer: both cleared, rightly flagged, missed by AI, false alarm, or action differs. The transcript decision from each side. A queue of the 8 transcripts with a one-line summary each |
| **Happy path** | Pick a transcript from the queue. Read the flagged answers first (marked on the left edge), then the clears, each with a one-line reason. Go to the next transcript |
| **Edge cases** | **The AI flags a different type than the human:** both are shown, along with any other types the AI listed. **Both flag the passage but choose different actions:** marked "action differs" (3 of 7 in this run). **No human verdict yet:** the AI verdict only, marked "awaiting review". **An AI-led interview:** labelled in the queue |
| **Acceptance criteria** | Quotes are verbatim, generated from the data by `design/fill_review_mock.py`. Every AI verdict has a reason, including clears. Colour is never the only signal: every outcome has a text label. One primary button |
| **Handoff** | The checked verdicts feed the scorecard. Disagreements go to failure analysis |

## Screen 2: Scorecard ([design/2-scorecard.png](2-scorecard.png), miss state [design/3-scorecard-misses.png](3-scorecard-misses.png))

**User:** whoever decides the AI is ready to run. **To confirm:** the Chief Legal & Regulatory Officer, a compliance operations lead, or both.
**Job to be done:** judge, issue type by issue type, whether the AI is good enough to run.

| | |
|---|---|
| **Example input** | One eval run (the blind AI reviewer) over 51 passages with human verdicts |
| **Expected output** | **The funnel first:** 51 passages reviewed by a human, then AI flagged 7, then human acted on 7 and cleared 0. **Missed by AI**, the primary error and the biggest number: 0 of 7. **False alarms**, secondary: 0 of 7. **A table by issue type** in two groups: misses (human acted on, missed by AI) and false alarms (AI flagged, human acted on, human cleared). The action agreement on rightly flagged passages, 4 of 7. **A drill-down** on the selected count |
| **Happy path** | Read the funnel and the two errors, then scan the misses column by type. Click any count to read its passages, each showing the quote, the declaration, the human verdict and the AI's reason. Set a root cause on each miss |
| **Edge cases** | **A miss that was the human over-redacting:** the eval reviewer marks it in the drill-down, without a headline of its own. **An engine whose flags have no type:** the false-alarm columns say so (design 3). **The AI flags a passage under a different type:** counted as "flagged under another type", not as a miss, and shown in the drill-down |
| **Acceptance criteria** | Raw numbers only. Numbers and quotes are generated from `notebooks/eval.py` by `design/fill_scorecard_mock.py`. Within each type, AI flagged equals human acted on plus human cleared. Missed by AI is the most prominent figure |
| **Handoff** | Misses, each with its root cause, go to failure analysis and prioritisation. The decision to let the AI run is made by the person to be confirmed |

## Style sheet (copy review)
- **Terms, one name per thing:** passage · AI · human verdict · missed by AI · false alarm · rightly flagged · human acted on · human cleared · root cause · over-redacted · declaration.
- **Issue type names:**
  - Material non-public information
  - Current-employer confidential
  - Declaration conflict
  - Source disclosure
  - Confidentiality breach
  - Personal data
- **Writing rules:** sentence case. No em dashes. Buttons start with a verb.
