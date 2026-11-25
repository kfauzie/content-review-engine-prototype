"""PII masking for the prototype (synthetic data). Every person and company gets a stable numbered ID, the same in every
transcript, table and log: Expert 0142, Person 0217, Reviewer 0318, Company 0031. Emails become [EMAIL], phone numbers [PHONE].

Each ID keeps its role as tags (listed or private; the expert's current or former employer; a third party named in the
call), so the eval can still judge MNPI and declaration conflicts without seeing a real name.

The vault (real name -> ID) is written at build time to data/private/vault.json, which is gitignored. Neither the eval
nor the page reads it; only the masking step and the leak test do.
"""
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
VAULT_PATH = ROOT / "data/private/vault.json"

# Companies named anywhere in the data, with the short forms used in speech. Each short form maps to the same ID.
COMPANIES = {
    "Brightmere Grocers": ["Brightmere"], "Halbrook Logistics": ["Halbrook"], "Marlow Haulage": ["Marlow"],
    "Corvane Freight": ["Corvane"], "Teallight Software": ["Teallight"], "Orbisoft": [], "Quillon Payments": ["Quillon"],
    "Brisk Invoicing": ["Brisk"], "Northwind Biomedical": ["Northwind"], "Marrow Analytics": ["Marrow"],
    "Ardent Foods": ["Ardent"], "Kestrel Advisory": ["Kestrel"], "Pellow Insurance": ["Pellow"], "Fairhaven Credit": ["Fairhaven"],
    "Pellham Biosciences": ["Pellham"], "Ashgrove Regulatory Partners": ["Ashgrove"], "Torvane Pharma": ["Torvane"],
    "Brannholt Automotive": ["Brannholt"], "Stellan Packaging": ["Stellan"], "Corran Engineering": ["Corran"],
    "Kelsall Home Products": ["Kelsall"], "Quayside Retail Software": ["Quayside"], "Plinth Systems": ["Plinth"],
    "Fenmore Legal Services": ["Fenmore"], "Harrowgate Partners": ["Harrowgate"], "Hollin Stores": ["Hollin"],
    "Calder Facilities Services": ["Calder"], "Dunmore Logistics": ["Dunmore"], "Ellery & Pike": ["Ellery"],
    "Velmora Home Appliances": ["Velmora"], "Albaro Elettrodomestici": ["Albaro"], "Marchbank Building Materials": ["Marchbank"],
    "Ashby Aggregates": ["Ashby"], "Tidewell Software": ["Tidewell"], "Corbridge Systems": ["Corbridge"],
    "Brayfield Telecom": ["Brayfield"], "Hartwell Pumps": ["Hartwell"], "Ridgeway Industrial Supply": ["Ridgeway"],
    "Penrose Distribution": ["Penrose"], "Nordvik Rubber": ["Nordvik"], "Thornbury Plastics": ["Thornbury"],
    "Fenwick Cartons": [], "Fenwick Telecom": [], "Harlow Foods": ["Harlow"], "Brennick Steel": ["Brennick"], "Tavish Bank": ["Tavish"],
}
# People named in a call who aren't the expert (colleagues, contacts, clients' staff).
THIRD_PARTIES = ["Aisha Rahman", "Anna Berg", "Carla", "Daniel Kerr", "Jamie Holt", "Mark Doyle", "Mark Ellison",
                 "Pieter van Dam", "Rachel Lim", "Tom Reyes"]

EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+")
PHONE = re.compile(r"(?<![\w.])\+?\(?\d[\d ()-]{7,}\d(?!\w|\.\d)")
ID = re.compile(r"\b(?:Expert|Person|Reviewer|Company|Client|Staff) \d{4}\b")


def _id(prefix, name, taken):
    n = int(hashlib.sha256(f"{prefix}:{name}".encode()).hexdigest(), 16) % 9999 + 1
    while (prefix, n) in taken:
        n = n % 9999 + 1
    taken.add((prefix, n))
    return f"{prefix} {n:04d}"


def build_vault(experts, reviewers):
    """Real name -> ID for every person and company. Deterministic: the same inputs give the same IDs."""
    taken, people, companies = set(), {}, {}
    for prefix, names in (("Expert", experts), ("Reviewer", reviewers), ("Person", THIRD_PARTIES)):
        for name in sorted(set(names)):
            assert name not in people, f"{name} has two roles"
            people[name] = _id(prefix, name, taken)
    for name in sorted(COMPANIES):
        companies[name] = _id("Company", name, taken)
        for alias in COMPANIES[name]:
            companies[alias] = companies[name]
    return {"people": people, "companies": companies}


def _phone(m):
    return "[PHONE]" if sum(ch.isdigit() for ch in m.group()) >= 9 else m.group()


class Masker:
    def __init__(self, vault):
        self.vault = vault
        self.people, self.companies = vault["people"], vault["companies"]

    def context(self, *objs):
        """People whose full name appears in these objects. Their first name alone (a greeting, "Carla told me") is
        masked too, but only here, so 'Daniel' maps to the right Daniel."""
        text = json.dumps(objs, ensure_ascii=False)
        return {p for p in self.people if re.search(rf"\b{re.escape(p)}\b", text)}

    def text(self, s, ctx=()):
        s = EMAIL.sub("[EMAIL]", s)
        s = PHONE.sub(_phone, s)
        table = dict(self.companies)
        table.update(self.people)
        for p in ctx:
            first = p.split()[0]
            if first != p:
                table.setdefault(first, self.people[p])
        keys = sorted(table, key=len, reverse=True)
        pattern = re.compile(r"(?<![\w-])(" + "|".join(map(re.escape, keys)) + r")(?![\w-])")
        return pattern.sub(lambda m: table[m.group(1)], s)

    def obj(self, x, ctx=()):
        if isinstance(x, str):
            return self.text(x, ctx)
        if isinstance(x, list):
            return [self.obj(v, ctx) for v in x]
        if isinstance(x, dict):
            return {k: self.obj(v, ctx) for k, v in x.items()}
        return x

    def name(self, real):
        return self.people[real]

    def leaks(self, text):
        """Real names still present in masked text (should be none)."""
        found = [n for n in list(self.people) + list(self.companies) if re.search(rf"(?<![\w-]){re.escape(n)}(?![\w-])", text)]
        firsts = {p.split()[0] for p in self.people if " " in p}
        found += [f for f in firsts if re.search(rf"\b{f}\b", text)]
        return sorted(set(found))


def tags_for(profile, declaration, turns_text, listed):
    """Role tags for each ID in one transcript, read from the masked profile and declaration only."""
    tags = {}
    for cid in dict.fromkeys(ID.findall(profile + " " + declaration + " " + turns_text)):
        t = tags.setdefault(cid, [])
        if cid.startswith("Company") and cid in listed:
            t.append(listed[cid])
    for cid, start, end in re.findall(r"(Company \d{4}) \((\d{4}) to (present|[A-Za-z]* ?\d{4})\)", profile):
        tags[cid].append("expert's current employer" if end == "present" else f"expert's former employer (left {end})")
    for cid in re.findall(r"[Cc]urrently employed by (Company \d{4})", declaration):
        if "expert's current employer" not in tags[cid]:
            tags[cid].append("expert's current employer")
    for cid in re.findall(r"Left (Company \d{4})", declaration):
        if not any("employer" in x for x in tags[cid]):
            tags[cid].append("expert's former employer")
    for cid, t in tags.items():
        if cid.startswith("Expert"):
            t.append("the expert")
        elif cid.startswith("Person"):
            t.append("third party named in the call")
        elif cid.startswith("Company") and not any("employer" in x for x in t):
            t.append("named in the call")
    return {k: v for k, v in sorted(tags.items())}


def listed_status(*texts):
    """Company ID -> 'listed' or 'private', where a declaration or profile says so."""
    out = {}
    for s in texts:
        for cid, kind in re.findall(r"(Company \d{4}) \((listed|private) company\)", s):
            out[cid] = kind
    return out


def save_vault(vault):
    VAULT_PATH.parent.mkdir(parents=True, exist_ok=True)
    VAULT_PATH.write_text(json.dumps(vault, indent=1, ensure_ascii=False) + "\n")
