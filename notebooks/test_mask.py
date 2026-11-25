"""Masking tests (synthetic data). Run after build_data.py: python3 notebooks/test_mask.py"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from mask import VAULT_PATH, Masker, build_vault, tags_for  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
fail = 0


def t(name, ok, got=None):
    global fail
    fail += not ok
    print(f"{'PASS' if ok else 'FAIL'} {name}{': ' + str(got) if got is not None else ''}")


v = build_vault(["Sanjay Mehta", "Daniel Reyes"], ["Sophie Laurent"])
M = Masker(v)
sid, did, n = v["people"]["Sanjay Mehta"], v["people"]["Daniel Reyes"], v["companies"]["Northwind Biomedical"]
t("IDs have a role prefix and four digits", sid.startswith("Expert ") and v["people"]["Sophie Laurent"].startswith("Reviewer ")
  and v["people"]["Daniel Kerr"].startswith("Person ") and n.startswith("Company ") and len(n.split()[1]) == 4)
t("IDs are stable: the same inputs give the same vault", build_vault(["Daniel Reyes", "Sanjay Mehta"], ["Sophie Laurent"]) == v)
t("a short name maps to the same ID as the full name", v["companies"]["Northwind"] == n)
t("full name and company masked", M.text("Sanjay Mehta left Northwind Biomedical.") == f"{sid} left {n}.")
t("first name masked only where that person is in context", M.text("Thanks, Sanjay.", M.context("Sanjay Mehta")) == f"Thanks, {sid}."
  and M.text("Thanks, Sanjay.") == "Thanks, Sanjay.")
t("two people with the same first name each keep their own ID", M.text("Hi Daniel", M.context("Daniel Reyes")) == f"Hi {did}")
t("possessives keep working", M.text("Northwind's results") == f"{n}'s results")
t("emails become [EMAIL]", M.text("Write to sanjay.mehta@northwind-bio.com today") == "Write to [EMAIL] today")
t("phone numbers become [PHONE]", M.text("Call +44 20 7946 0958 or (020) 7946-0958.") == "Call [PHONE] or [PHONE].")
t("dates, years, prices and figures are left alone", M.text("On 2026-11-04, 2018 to 2022, £40, 31.4%, 1,000 calls") == "On 2026-11-04, 2018 to 2022, £40, 31.4%, 1,000 calls")
tags = tags_for("Expert 0001. CFO, Company 0002 (2016 to 2022). Advisor, Company 0003 (2023 to present).",
                "Left Company 0002 (listed company) in 2022.", "Company 0004 is strong. Person 0005 told me.", {"Company 0002": "listed"})
t("tags keep the role: listed former employer, current employer, named company, third party",
  tags == {"Company 0002": ["listed", "expert's former employer (left 2022)"], "Company 0003": ["expert's current employer"],
           "Company 0004": ["named in the call"], "Expert 0001": ["the expert"], "Person 0005": ["third party named in the call"]}, tags)

# leak scan on the built outputs, with the real vault
real = Masker(json.loads(VAULT_PATH.read_text()))
for f in ["data/benchmark.json", "build/mvp.html", "data/eval/test_set_masked.md", "data/eval/release_gate.json",
          *[str(p.relative_to(ROOT)) for p in sorted((ROOT / "data/eval/versions").glob("*.json"))]]:
    leaks = real.leaks((ROOT / f).read_text())
    t(f"no real names in {f}", not leaks, leaks or None)
t("the vault is gitignored and not embedded in the page", "data/private/" in (ROOT / ".gitignore").read_text()
  and "vault" not in (ROOT / "build/mvp.html").read_text().lower())
print(f"{fail} FAILED" if fail else "All tests pass")
sys.exit(1 if fail else 0)
