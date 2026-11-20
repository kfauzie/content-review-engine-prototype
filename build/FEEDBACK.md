# Prototype feedback, next round (noted, not yet applied)

Kevin's feedback on the built prototype (`build/mvp.html`). Nothing below is applied yet: it waits for Kevin's go. Later points replace earlier ones where they conflict.

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