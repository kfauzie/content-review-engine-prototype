"""Write the input for a blind AI reviewer: profiles, declarations and transcripts only.
Strips the answer keys, the transcript titles (they name the planted issues) and the summary table.
Run from the run folder: python3 notebooks/make_blind_input.py
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from data_review import SRC, parse  # noqa: E402

OUT = Path(__file__).resolve().parent.parent / "data" / "eval" / "blind_input.md"


def main():
    T = parse(SRC.read_text())
    lines = ["# Expert call transcripts for content review", "",
             "Fictional transcripts. Each has the expert's profile, their onboarding declaration and the transcript.",
             "Answer IDs are T<transcript>-<mm:ss> of the expert's answer.", ""]
    for t in T:
        lines += [f"## Transcript {t['num']}" + (" (AI-led interview)" if t["ai_led"] else ""), "",
                  f"**Expert profile:** {t['profile']}", "", f"**Onboarding declaration:** {t['declaration']}", ""]
        for ts, who, txt in t["turns"]:
            tag = f"T{t['num']}-{ts // 60:02d}:{ts % 60:02d}"
            lines.append(f"[{tag}] {who}: {txt}" if who == "EXPERT" else f"[{ts // 60:02d}:{ts % 60:02d}] {who}: {txt}")
            lines.append("")
    OUT.write_text("\n".join(lines))
    text = OUT.read_text()
    assert "Answer key" not in text and "answer key" not in text.lower().replace("answer ids", "")
    assert not re.search(r"overall_decision|expected_action|Over-flag|Clear MNPI|Grey case", text)
    print(f"wrote {OUT.relative_to(OUT.parent.parent.parent)}: {len(T)} transcripts, {text.count('] EXPERT:')} expert answers")


if __name__ == "__main__":
    main()
