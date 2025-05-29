import argparse
import json
from pathlib import Path
from .matching import Resolver, read_csv


def main():
    p = argparse.ArgumentParser(description="Link already extracted political mentions to names and parties.")
    p.add_argument("--input", type=Path, required=True)
    p.add_argument("--output", type=Path, required=True)
    p.add_argument("--data", type=Path, default=Path("data"))
    p.add_argument("--mode", choices=["review", "historical"], default="review")
    p.add_argument("--swedish-greens", action="store_true")
    a = p.parse_args()
    rows = read_csv(a.input)
    if any(not ("mention" in r or "NER" in r) for r in rows):
        p.error("Input needs mention or NER; use source_country or Country for context.")
    resolver = Resolver.from_directory(a.data, a.mode)
    a.output.parent.mkdir(parents=True, exist_ok=True)
    count = 0
    with a.output.open("x", encoding="utf-8") as f:
        for i, row in enumerate(rows):
            result = resolver.resolve(row.get("mention", row.get("NER", "")), row.get("source_country", row.get("Country", "")), a.swedish_greens)
            result["record_id"] = row.get("record_id", str(i))
            f.write(json.dumps(result, ensure_ascii=False, allow_nan=False) + "\n")
            count += result["needs_review"]
    print(f"Wrote {len(rows)} mentions; {count} flagged for review.")


if __name__ == "__main__":
    main()
