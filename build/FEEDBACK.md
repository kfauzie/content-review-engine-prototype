# Prototype feedback, round 22 (applied)

- **Removed:** the Meridian Pro/Swift comparison line, the "simulated answers" note and the kill-switch sentence.
- **Runs on all 1,000 reviewed transcripts:** the same set as the Current AI performance page.
  - **Production:** it reproduces that page exactly: 262 issues, 23 missed (5, 4, 0, 4, 3, 7), 187 false alarms (98, 41, 27, 21). Each production miss is one of the page's example misses, in the same transcript.
  - **New versions:** outputs are simulated item by item by stated rules (see `notebooks/release_gate.py`). On the 8 test-set transcripts, v1.1 keeps the blind reviewer's verdicts.
  - **v1.1 results:** 9 lower-priority misses, all named people, since it adds no check for them. 138 false alarms: it clears those about long-ago employers and public market talk. Ready.
  - **v1.2 results:** misses the hedged MNPI hint. Not ready, 1 high-priority miss.
- **v1.2 "What's changed":** "flags by issue type" is gone. It now reads "Model: Meridian Pro → Meridian Swift", "Reads: same as v1.1…", "Instructions: same as v1.1" and "Settings: same".
- **Result:** "Ready" with "0 high-priority misses", or "Not ready" with "N high-priority misses". Nothing else.
- **Sections:** each compare section is its own card with a coloured band (slate, amber, blue, rose) and a divided header. "What's changed" is a section of its own.
- **Last section:** headed "All current misses and false alarms". It lists every miss with its quote, and every false alarm by type with its transcript IDs.
- **Transcript IDs everywhere:** examples on the Current AI performance page cite the transcript ID ("Transcript 0702 · 12 Nov 2026 · 01:24") instead of the expert ID. Transcript pages carry the ID as their eyebrow.

---

# Prototype feedback, round 21 (applied): second light polish

**Structure**
- **Tabs:** two tabs, "Current AI performance" (the benchmark of the version in production) and "Compare a new version". The repeated breadcrumb is gone.
- **Compare page:** a one-line description, "Run a new version on the same reviewed transcripts and compare it with current production." The release log and the results header are removed.

**Compare a new version**
- **Models:** fictional names, Meridian Pro (current) and Meridian Swift, with one line on the difference.
- **What's changed:** shows only what differs from production. Changed lines are highlighted (e.g. "Model: Meridian Pro → Meridian Swift"); unchanged lines are muted (e.g. "Settings: same").
- **Misses table:** Issue type | Priority | Current production missed | New version missed. It's sorted by priority, has an "All types" total and small transcript links in the cells.
- **False alarms table:** titled "False alarms: flagged by AI, not an actual issue", with numbers only in the cells.

**Current AI performance**
- **Improvements:** each has its own colour (blue, teal, terracotta) on its top rule, number and labels.
- **Expert quotes:** italic on a light grey background with a thin left rule.
- **Type sizes:** the missed-by-AI and false alarm sections now use the same sizes.

**Content**
- **Clearer quotes:** 16 quotes were reworded, and the test set, written transcripts, highlights and simulated outputs were updated to match. Examples: "on sick leave for months after a mental breakdown", "knee replacement devices", "price list", "forecast" for "guided", "per user" for "a seat", "selling off part of their business" for "carve-out".
- **Improvement 2:** now "Flag named people: insider sources and personal details".
- **First missed example (transcript 5):**
  - **Reviewer comment:** names the knee replacement device and drops "hedging". It's in two paragraphs.
  - **AI note:** says the reviewer relied on a fact not in the transcript (that the company is listed), probably taken from the declaration.
- **First false alarm example (transcript 7):** the AI note now says to check figures against approved public sources, such as company filings and earnings call transcripts.

---

# Prototype feedback, round 20 (applied): light polish, copy, colour, version testing

1. **Copy, rewritten as a senior lawyer would write it.** This covers all 20 human reviewer comments, all 20 "Why the original AI didn't flag it" notes, the 18 "Cleared" reasons, the category and false alarm descriptions, the fix copy, the note subtitles and the legend.
   - **Style:** short sentences, plain words, and jargon explained ("its published forecast (its guidance)").
   - **Reviewers:** comments don't name the company we work for. Reviewers are labelled as human and internal: the box is "Human reviewer's comment", signed e.g. "Reviewer 6689, Legal Counsel (internal)".
   - **Fix titles (Kevin's wording):** "Give the AI the expert's declaration", "Flag possible insider contacts", "Check if the cited source is already public".
2. **One colour system with soft tints.**
   - **Purple:** only the Run button, links, the selected tab and the selected version.
   - **Masked IDs:** experts light blue, companies light amber, people light grey.
   - **Passage notes:** the human reviewer's comment is light green; the AI note is light rose.
   - **Priority tags:** high red, medium amber, low grey. Source disclosure and personal data are medium; former-client confidential is low.
   - **Layout:** each section is a white card on a very light grey page.
3. **List hierarchy:** the issue type is bold and the description normal weight. Quotes have a thin left rule, and there's more space between issues. The list layout is unchanged.
4. **Version page, "Test a new version against current production".** The term "release gate" is gone from the screen.
   - **Order:** the picker and Run button, the selected version's description, the comparison, the results, then the release log.
   - **Version labels:** "Current production (v1.0)", "New version: reads the expert's declaration (v1.1)", "New version: cheaper model (v1.2)".
   - **Loading state:** "Running on 8 transcripts…".
   - **Results:** green "Ready for shadow testing", or red "Not ready: missed MNPI in transcript 5" with a link to the passage. It's transcript 5, not 4: the line comes from the scoring.
5. **Comparison as two measures, current production next to the new version.**
   - **Misses:** "N of 7 actual issues caught" and "N missed (N high priority)", with misses by issue type underneath.
   - **False alarms:** "N false alarms", with the count by type of non-issue underneath (public source cited, harmless company mention, public market talk).
   - **Zeros:** every number is labelled, e.g. "0 missed".
   - **v1.1:** now catches all 7 issues and raises 2 false alarms. The results list shows each one with the answer key's note and what v1.1 said.
   - **Source of the numbers:** all of them come from the scoring code, and a test checks the page against the Python eval.

---

# Prototype feedback, round 19 (applied): release gate and PII masking

Kevin asked for a release gate on the benchmark, with names masked everywhere. Existing pages keep working.

1. **Agent versions:** a picker with three versions, each with a one-line description, model, prompt summary and settings.
   - **v1.0, current production:** flags any answer naming a company.
   - **v1.1, candidate:** also reads the declaration to work out "we", "us" and "their".
   - **v1.2, candidate:** v1.1 on a cheaper, faster model.
   - **Outputs and scoring:** outputs are pre-generated and labelled simulated. The scoring is real: the eval code and the page compute the same results, and a test checks they match.
2. **Release gate, at the top after a run.**
   - **Rule:** zero misses in MNPI, current-employer confidential and declaration conflict, and no more misses in the other types than v1.0.
   - **v1.1:** green "Release gate: passed. v1.1 can go to shadow mode."
   - **v1.2:** red "Release gate: blocked. v1.2 missed MNPI in transcript 5 (hedged hint about a listed company)." It links to the passage, which shows the answer key next to v1.2's output.
   - **Correction:** the hedged hint is in transcript 5, not 4.
   - **Baseline comparison:** a table shows misses by type, false alarms and flags for v1.0 and the candidate. Every count links to its passages.
3. **Release log:** date and time, version, result, reason and who ran it. It's prefilled with v1.0's release (Staff 0004). Each run adds a row ("Staff 0001 (you)"), and the rows are kept in this browser.
4. **PII masking:**
   - **IDs:** every person and company has a stable numbered ID, the same across all transcripts, tables and logs: Expert, Person (third parties), Reviewer, Staff and Company.
   - **Role tags:** each ID keeps its role, e.g. "Company, listed, expert's former employer (left March 2026)". Tags show as hover text on the ID chips and in a "Masked names in this call" box on each transcript.
   - **Emails and phone numbers:** these become [EMAIL] and [PHONE]. None appear in the synthetic data.
   - **Client IDs:** no client names appear in the data, so no Client IDs are issued yet.
   - **The vault:** the table mapping names to IDs is written only at build time to a gitignored file. Neither the eval nor the page reads it.
   - **Initials:** the example rows and cards now show the expert ID in place of initials.
5. **Copy under the gate:** "In production, the same check runs on live spot-checks. A miss in a high-priority type triggers the kill switch, and that type goes back to full human review."

---

# Prototype feedback, round 18 (applied): category examples as rows

Kevin agreed to switch the category examples from carousels to rows, the convention in comparable products (Braintrust and LangSmith trace tables, inbox lists).

- **Each row:** the initials, the quote at full width with its highlight (plus the "Cleared" reason for false alarms), the date and call time on the right, and an arrow only when the row opens a transcript.
- **No paging:** every example in a category is visible, and clicking the category header still hides or shows them.
- **Phone:** the time moves under the quote.
- **Unchanged:** the recommendation examples stay as cards, as do all words, numbers, highlights and links.

---

# Prototype polish, round 17: example cards toned down (presentation only)

**The convention found:** comparable products keep list items neutral and use one highlight colour on the trigger words. Status colour goes on the container, not the item.
- **Braintrust and LangSmith:** one row per trace, in a plain, filterable table.
- **Microsoft Purview:** the condition that caused the flag appears in a yellow banner.
- **Mimecast:** highlights matches in the message subject and body.
- **Veritas/Cohesity:** highlights hot words.
- **Smarsh:** is adding whole-sentence highlights.
- **Inbox list guidance:** a neutral avatar, a title and preview, and muted time.

**Applied to the example cards (and the recommendation examples, which share the component):**
- **Cards:** white, with a fine neutral border and no coloured edge.
- **Highlight:** one soft yellow marker on the telling phrase.
- **Avatars, dates and arrows:** grey.
- **"Cleared" line:** muted grey.
- **Category containers:** keep their status edge.

No words, numbers or layout changed.

---

# Prototype feedback, round 16 (applied)

1. **Three more examples in each of the last three false alarm types.** The expert's own opinion goes from 0 to 3, former employer left long ago from 1 to 4, and public market talk from 1 to 4. All 9 are written for the design, from fictional experts, each with a highlight and a "Cleared" reason.
   - **Filing:** each is filed under an issue category outside the top two (what the AI plausibly flagged it as), so fix 1 and fix 3's false alarm estimates (12 and 78) are unchanged.
   - **Transcripts:** under the existing rule, these cards don't open a transcript.
2. **Header copy:**
   - **Top bar:** "Content review engine · AI benchmark".
   - **Badge:** "Illustrative · synthetic data".
   - **Title:** "Content review AI: performance benchmark" (also the browser tab).
   - **Subtitle:** "We compared the content review AI with human reviewers across 1,000 transcripts to see where it misses compliance risks, and where it raises false alarms."
   - **Phone:** the top bar wraps the badge onto its own line.

---

# Prototype feedback, round 15 (applied)

**False alarms are grouped by type of false alarm, not by issue type.** Nothing else on the page changed.

| Type | False alarms (made up) | Examples |
|---|---|---|
| Public source cited | 98 | 7 (Robert Chen, Laura Bennett, Arjun Mehra, Chloe Martin, Ibrahim Yusuf, Ruth Okonkwo, Marco Rossi) |
| The expert's own opinion or estimate | 41 | none in the test set (count only) |
| Former employer, left long ago | 27 | 1 (Tom Fairley) |
| Public market talk | 21 | 1 (Daniel Reyes) |

- **Totals:** the types sum to 187, the same total as before, and a check enforces it.
- **Rows:** each shows the count "of 187" with "of all false alarms" beneath. They open and close like the issue rows, and every example opens its transcript.
- **Unchanged:** fix 3's impact (78 fewer false alarms) still comes from the same tagged examples.

---

# Prototype feedback, round 14 (applied)

1. **One font again:** the serif from round 13 is removed, and Inter is used throughout. The rest of the polish stays (paper neutrals, hairline surfaces, marker-style highlights). A check confirms one font family.
2. **Subtitle under "Possible improvements":** "Based on the human reviewers' comments and independent agents' analysis of the original AI's logs".
3. **Category example cards match the recommendation examples:** no names, a highlighted phrase, initials, date and call time, in the same card component. All 32 cards now have a highlight, and a check confirms each appears word for word in its quote. Cards that are also recommendation examples use the same phrase. False alarm cards keep their "Cleared: …" line, which is content.
4. **The top boxes are clickable:** the compliance box scrolls to "Missed by AI, by type", and the false alarm box scrolls to "False alarms, by type". Each has a down arrow and a hover state. They work with the keyboard (Enter or Space), and the scroll is smooth unless the device asks for reduced motion.

---

# Prototype polish, round 13 (presentation only)

Kevin asked for a review of legal AI interfaces and a light visual polish, with no change to any number or text. The diff touches only the stylesheet and the font link: one added CSS block, and Newsreader added to the Google Fonts request.

**Research:** web search turned up positioning for Harvey, Legora and Spellbook, and reviews praising Luminance's "clean interface" and clause highlighting. The product sites are blocked from this container, so the traits applied are Claude's read of the category, not a study of their screens.

**Applied:**
- **Type:** an editorial serif (Newsreader) for the title, section headings, card headings, category names and fix titles. Quotes are in serif, so they read like documents. Numbers stay in Inter.
- **Colour:** warm paper neutrals (background #f6f4ef, cards #fffefb) with deep ink navy. Colour is kept for meaning: deep red for missed, amber for false alarms, green for found, violet for the fixes, blue for reviewers.
- **Surfaces:** hairline borders in place of shadows, and a coloured top rule on the summary panel (red for liability, amber for cost). The "Liability risk" tag is solid red, and the "Operational cost" tag is outlined.
- **Example and fix quotes:** cards with a coloured left rule. Highlights use a marker-style underline, the way a lawyer marks up a document.
- **Transcript:** a document column with serif text for the expert's answers, sans-serif for the interviewer, and outlined tags.

---

# Prototype feedback, round 12 (applied)

1. **Fixes section title:** "Possible improvements", with the "Estimated from…" note removed.
2. **The top layout, based on common dashboard guidance:** one summary panel split about 70/30 by a divider. The primary metric sits top-left, largest and highest contrast. The secondary metric sits beside it at medium emphasis, on a quieter amber tint, at the same height, centred. This replaces two separate cards of different heights. Guidance sources: Improvado, Klipfolio, Geckoboard, Splunk Dashboard Studio (vendor guides, not research). No "Also measured" label.
3. **The compliance zone:** headed "262 compliance risks found in the transcripts". The big red 23 "missed by AI" with "Liability risk" beside it. The 239 is no longer a big number: it's a small caption under the bar, "239 found by AI", with a green dot. A main number needs context beside it, not a rival.
4. **Reviewer comments** carry a date and time ("Sophie Laurent, Legal Counsel · 13 Nov 2026, 09:42"). They're made up, one or two days after the call, during Athens office hours.
5. **Recommendation examples** show the call date and timestamp ("4 Nov 2026 · 01:34"), matching the card and the transcript passage.

---

# Prototype feedback, round 11 (applied)

Kevin rewrote the fix copy in plain terms for a senior lawyer. It's applied word for word:
- **Titles:** "Read each answer in context", "Check for people and sources, not just companies", "Check the expert's cited source before flagging".
- **Section labels:** "Why the AI missed it" (fixes 1 and 2), "Why the AI raised a false alarm" (fix 3), "Examples", "What we'll change".
- **Impact lines:** "10 fewer risks missed by AI, 7 of them high priority", "12 fewer false alarms", "11 fewer risks missed by AI", "78 fewer false alarms". The numbers still come from the code. This also ends the earlier ambiguity, where "10" and "7 high priority" could read as "107".

---

# Prototype feedback, round 10 (applied)

1. **The false alarm box:** much smaller than the main box (about a quarter of the width), sized to its own content, not the same height.
2. **The fix examples:** clickable through to their transcripts. Fix 2's examples are now Elena Vasquez and Hannah Booth, test-set passages with full transcripts (transcripts 6 and 8), so no new transcripts were invented. Their carousel cards became clickable too.
3. **Example counts:** varied at 3, 2 and 4 per fix, not 2 each.
4. **Each fix has three labelled parts:** Root cause, Examples (the quote boxes) and Next steps. The Expected impact boxes are smaller.
5. **Issue categories:** "5 of 38" with "in this category" in small type beneath.

---

# Prototype feedback, round 9 (applied)

1. **The compliance box:** a bigger label ("Compliance risks found in transcripts", 20px) and a bigger box than the false alarm box, because liability risk matters more than operational cost. It shows "239 found by AI" in green and "23 missed by AI" in big red with "Liability risk" beside it. The bar is green and red.
2. **The false alarm box:** shows only "187 false alarms", "flagged by AI, marked as non-risk by human reviewers" and the "Operational cost" tag. No 239 and no bar.
3. **More colour:** green for found by AI, a red tint on the compliance box, an amber tint on the false alarm box, and violet for the fixes.
4. **The fixes:** the general description is replaced by two concrete examples each. Each example is a highlighted quote with the expert's initials and the call date, and it isn't clickable. Short quotes are shown in full; long ones show the sentence with the highlight.
5. **An "Expected impact" box in each fix,** with separate boxes: "Reduces missed by AI by N" (red, high-priority count beneath) and "Cuts false alarms by N" (amber). The grey "no change" and "not estimated" boxes are removed.
6. **Issue categories:** the bars are removed. Each row shows the number big, with "out of N" smaller beside it. For false alarms, N is the AI's flags in that category (correct plus false alarms).

---

# Prototype feedback, round 8 (applied)

Kevin's feedback on the built prototype (`build/mvp.html`). Applied after Kevin's go; tests and the headless check updated and passing.

**Choices made while applying:**
- **Right card heading:** "Flags raised by the AI", to mirror the left card.
- **Card widths:** both cards are now equal, so each pair of numbers sits side by side.
- **Reviewers:** the names and titles are made up and rotate across the transcripts. Possible material non-public information goes to Legal.
- **Fix impact:** misses are counted exactly (one card per miss). False alarms are estimated per category from the tagged examples, and only the top two categories have examples. Fix 2's false-alarm impact is shown as "not estimated".
- **Uncovered misses:** 2 misses (Mateo Alvarez, Siobhan Kelly) aren't addressed by any of the three fixes.
- **Reduced motion:** the page now turns off its animations when the viewer's device asks for reduced motion.

## Header
1. **Subtitle under the title:** "We compared AI and human review across 1,000 transcripts to see where the AI misses compliance risks, and where it raises false alarms"

## Compliance card (left)
2. **Heading:** "Compliance risks found in the transcripts" (replacing "Compliance risks").
3. **Numbers:** 262, smaller, labelled "found by human reviewers". 23, the big red number, labelled "missed by AI".
4. **Tag:** "Liability risk" sits next to the 23, not next to the heading.
5. **Legend:** remove "Caught by AI 239 · Missed by AI 23" below the bar. It repeats the numbers above it.

## False alarm card (right)
6. **239** is styled like the 262 in the left card: smaller and in a quieter colour, labelled "risks correctly flagged by AI".
7. **187** is the big number, labelled "false alarms".
8. **Tag:** "Operational risk" becomes "Operational cost" and sits next to the 187.
9. **Legend:** remove the legend at the bottom ("Confirmed 239 · False alarms 187"). "Confirmed" disappears everywhere, and the hover text on the category bars says "correct".

## Transcript page
10. **Reviewer's comment:** replace the subtitle "Compliance reviewer" with the reviewer's name and title (made up, labelled illustrative like the rest).

## New: three highest-impact fixes
11. **Content:** based on the human reviews and the independent agents' analysis, name the 3 fixes with the highest potential impact. Each gets a short "how" (some detail, not too much) and its expected impact on both numbers: missed by AI (23) and false alarms (187).
EOF
git add build/FEEDBACK.md && git commit -q -m "Update noted prototype feedback (not applied yet)

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_016JoguZ56suePFwdTFDaiob" && git push 2>&1 | tail -1