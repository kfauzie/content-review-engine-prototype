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