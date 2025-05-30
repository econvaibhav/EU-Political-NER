"""Group reviewed results into a reusable glossary without mixing affiliations."""
import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


def build(rows, include_flagged=False):
    groups = defaultdict(set)
    for row in rows:
        if row.get("needs_review", False) and not include_flagged:
            continue
        name, party = row.get("Names", ""), row.get("Party", "")
        if not (name or party):
            continue
        key = ("Name" if name else "Party", name or party, party,
               row.get("NER_country_cleaned", ""), row.get("EU"))
        if row.get("NER", "").strip():
            groups[key].add(row["NER"].strip())
    return [dict(Type=k[0], Entry=k[1], Variations=", ".join(sorted(v)), Party=k[2],
                 Country=k[3], EU="" if k[4] is None else k[4]) for k, v in sorted(groups.items(), key=lambda item: str(item[0]))]


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--include-flagged", action="store_true", help="Include unresolved review suggestions; inspect before reuse")
    a = p.parse_args()
    rows = [json.loads(line) for line in a.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    a.output.parent.mkdir(parents=True, exist_ok=True)
    with a.output.open("x", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["Type", "Entry", "Variations", "Party", "Country", "EU"])
        w.writeheader(); w.writerows(build(rows, a.include_flagged))
