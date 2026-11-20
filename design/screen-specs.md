# Design (pm-4): one screen

> Illustrated. The numbers are made up, the misses are examples from a synthetic test set, and nothing here is Dialectica's data.

**The story:** "Before we let the AI do more, check it against what reviewers already decided."
**Cut to one screen** after Kevin's feedback: no reviewer workflow, no declarations panel, no rulings.

## The eval check ([design/1-check.png](1-check.png))

| | |
|---|---|
| **Example input** | A sample of 1,000 transcripts reviewers have already decided, with the AI run over each (made-up numbers) |
| **Expected output** | **Three numbers at the top, all counted in transcripts:** sample transcripts (1,000); missed by AI, where reviewers found a problem in a passage the AI didn't flag (23); false alarms, where the AI was overly cautious and flagged something reviewers cleared (187). Missed by AI is the most prominent. **Below:** the list of AI misses only. Each row shows the issue type, the sentence with the problem and where it is. Click a row to see the full quote and why the AI missed it |
| **Happy path** | Read the three numbers, then open the misses one by one |
| **Edge cases** | **No misses:** the list says so. **A miss that was the reviewer over-redacting:** a later need, not on this screen |
| **Acceptance criteria** | Quotes are verbatim, generated from the test set by `design/fill_check_mock.py`. The made-up numbers are labelled once as illustrative. Colour is never the only signal |
| **Handoff** | The misses and why they happened go to failure analysis and prioritisation |

**The example misses:** 4 passages from the synthetic test set that a made-up rules engine (it flags company names) missed (`notebooks/eval.py`). The "why" text is my failure-analysis judgement.
**Design system:** neutral defaults. Red is missed by AI, amber is false alarm, and one accent is kept for actions.
