# Design (pm-4): screen specs

> Illustrated on 8 synthetic transcripts. Nothing here is Dialectica's data, policy or tool. The engine under test is made up for the demo.

Two screens for two users, so two screens rather than one page: Legal decides what the engine may do, and an analyst clears a transcript. Most important first.

**Design system:** Dialectica's isn't available (Figma isn't connected and there's no `design-system.md`). These are neutral defaults: greyscale, one accent for the main action, and one hue per meaning.

**Patterns borrowed** (from public help pages and search summaries; this session couldn't open product sites to study screenshots):
- **Counts of agreement with expert labels, per criterion, and a click from any count into its disagreements:** eval tools such as Langfuse's per-criterion alignment view and Pydantic Logfire's case comparison, which shows the evaluator's reason.
- **The document in the centre, with a coding panel and a card of facts about it beside it:** Relativity's review interface.
- **Every flag carries an explanation of where the risk is:** Global Relay's surveillance alerts.

## Screen 1: Eval scorecard (designed first)

**User:** the Chief Legal & Regulatory Officer, with Kevin (Lead AI Product Developer) running the eval.
**Job to be done:** decide, one issue type at a time, whether the engine can be trusted to do more, and see why.

| | |
|---|---|
| **Example input** | 8 synthetic transcripts (51 expert answers). The flags of a made-up engine that flags every answer naming a company. Analysts' verdicts, which here are the test set's answer key (7 issues). |
| **Expected output** | Three numbers: missed by the engine (4 of 7 issues), false alarms (5 of 8 flags), missed by analysts (0 until Legal rules otherwise). A one-line diagnosis. A table by issue type showing issues, rightly flagged, missed by the engine, missed by analysts, the miss-rate bar, evidence needed against evidence held, and status. A list of the 9 disagreements awaiting a ruling. |
| **Happy path** | Read the three numbers and the diagnosis, then scan the types. Open a disagreement to see the passage, the declaration and both verdicts, then record a ruling, and the numbers update. Set the miss-rate bar for each type, then save the rulings. |
| **Edge cases** | **A passage with no analyst verdict:** left out and counted as "not reviewed". **A ruling that the engine was right where analysts cleared:** the passage becomes an issue, missed by analysts. **A ruling that analysts over-flagged:** the issue is removed. **A type with no issues:** "No issues yet". **An engine that doesn't assign types:** false alarms are shown as a total, not by type. **Quitting midway:** rulings are kept. |
| **Acceptance criteria** | Every count opens the passages behind it. Rightly flagged plus missed by the engine equals issues. Flags equal rightly flagged plus false alarms. The bar sets the evidence needed at 3 in n, so 60, 150 or 300 issues. The synthetic-data line is always visible. |
| **Handoff** | Status by type goes to Legal for sign-off. Misses and false alarms go to failure analysis, prioritised by the cost of a mistake. Any passage opens in screen 2. |

## Screen 2: Review screen (designed after screen 1 is agreed)

**User:** a junior compliance analyst.
**Job to be done:** clear a transcript without letting a high-impact issue through, and without leaving the screen to check the declaration.

| | |
|---|---|
| **Example input** | Synthetic transcript 4 (payments lending). The expert left his former employer in 2021, names it twice and cites public sources. |
| **Expected output** | The declaration beside the transcript. On each answer, facts found by code with their source: "Names Quillon: former employer, left 2021 (profile)", "Cites a public source: investor day". A decision on each answer with a fact (clear, redact or escalate). A transcript decision. An audit trail. |
| **Happy path** | Pick the transcript from the queue and read it with the declaration beside it. At each answer with a fact, decide. Then record the transcript decision, which writes the audit trail. |
| **Edge cases** | **No declaration on file:** a warning to review every line and refer the expert to vetting. **A leaving date that comes only from the expert's own declaration:** said in the fact. **An AI-led interview:** labelled as such. **Quitting midway:** decisions kept as a draft. |
| **Acceptance criteria** | No declaration check needs another system. Every fact names its source and is a fact, not a verdict: people decide. In the real build, an AI adds a one-line reason, and this prototype says so. One primary button. Every decision lands in the audit trail with who or what, and when. |
| **Handoff** | Escalations go to a senior compliance manager, then Legal. Declaration conflicts go to the vetting team. Decisions flow back into the eval as analysts' verdicts. |

## Style sheet (copy review)
- **Terms, one name per thing:** issue type · engine · analysts' verdict · ruling · rightly flagged · false alarm · missed by the engine · missed by analysts · miss-rate bar · declaration.
- **Issue type names:**
  - Material non-public information
  - Current-employer confidential
  - Declaration conflict
  - Insider source named
  - Former-client confidential
  - Personal data
- **Writing rules:** sentence case, numbers as digits, "%" in tables. No em dashes. Buttons start with a verb. Confirmations are in the past tense.
