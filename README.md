# EU Political NER

The aim here to map the names people actually wrote in thier observational notes about parties and political actors they saw on Instagram and Tiktok to the right person, party and country. People many times use the wrong spelling, make up shortforms of the name and rarely ever write the full name, party and country affiliations together. While is extremly useful information for research, asking data gatherers to do to this and maintain high accuracy is very hard. Hence this repo does the work for you -- It takes the EU Political entities data gathers might have seen and makes it uniform, **ready for interpretations**!

**The country glossaries is one of the biggest contributions of this project.** It bring together months of collecting references, searching names one by one, checking affiliations and reviewing the results with country experts. The data was also scraped from multiple offical country websites. The examples below show why that work was needed and how to reuse it.

[Browse the glossaries](data/reference/glossaries/)


[See the example results; refer to review needed key too as it is important part of this project -- CODE + HUMAN REVIEW](examples/example_results.jsonl) 


[Run the replication guide](#replication-guide)

<img width="827" height="690" alt="image" src="https://github.com/user-attachments/assets/4dc6b9c8-6d22-4d95-a140-fd7554722fc2" />


## The country glossaries

The ten glossaries cover **Bulgaria, Croatia, Finland, France, Germany, Hungary, Poland, Portugal, Spain and Sweden**. Together, the CSVs contain **2,006 rows and 3,401 recorded variant items**.

Any name can appear in a different order, without accents, as initials, as a surname or with several spelling mistakes. The glossaries keep those observed forms together with a canonical entry, recorded party affiliation and actor country. They also retain the source workbook, sheet and row, so an entry can be traced back to its working reference. The glossary refers to persons/parties seem for specific country accounts in IT/TK. Hence, they have the country column! 

Here are some actual entries. The variants are copied from the CSVs; for the longer entries, only a selection is shown.

| Canonical entry | Some recorded variants | Variant items in that row | Glossary |
|---|---|---:|---|
| Péter Magyar | `Magyar Péter`, `Magyar Peter`, `magyar peter`, `magyar péter` | 4 | [Hungary](data/reference/glossaries/hungary.csv) |
| Ursula von der Leyen | `U. VdL`, `Ursula vdL`, `Urs. VDL`, `van der Leyen`, `vDL` | 12 | [Germany](data/reference/glossaries/germany.csv) |
| Jean-Luc Mélenchon | `J L Melenchon`, `JL Melemchon`, `Jl Melanchon`, `Jean Luc Mélenchon`, `Mélenchon`, `Jean-Luck Mélenchon` | 13 | [France](data/reference/glossaries/france.csv) |
| Boyko Borissov | `Boyko Borisov`, `B. Borissov`, `Borssiov`, `Boyko Borrisov`, `Boyko Borisssov` | 11 | [Bulgaria](data/reference/glossaries/bulgaria.csv) |
| Ben Zyskowicz | `Ben Zyskowicz`, `Ben Z`, `Ben Z.` | 3 | [Finland](data/reference/glossaries/finland.csv) |
| Pedro Sánchez | `Pedro Sánchez`, `Pedro Sanchez`, `pedrosanchez`, `peedro sanchez` | 6 | [Spain](data/reference/glossaries/spain.csv) |

This is the practical value of saving the manual work: the next person can inspect and reuse the recorded variants instead of starting every name search from scratch. The files can support dictionary building, matching and review in another project.

## The manual work behind the dictionaries

Candidate lists were scraped from the original country websites, using webpages or PDFs depending on the country. The programmer and country experts collected and checked this reference material. The programmer also manually reviewed the initial NER output for people and parties.

Spelling corrections, short names, party information and EP group corrections were researched **one entry at a time**. The glossaries were manually reviewed too. Finally, **every row went through checks by multiple political-science and country experts across the ten countries**. The [review table](docs/manual_review.md) shows who worked on each stage.

Alongside the country glossaries, the repo includes **1,833 candidate-reference rows**, **573 party-reference rows**, **275 manual alias rows** and **162 review instructions**. The aliases and review notes preserve more of the decisions made along the way.

## Examples: 

| Mention | Response country | Result in the example output |
|---|---|---|
| `Magyar Péter` / `Péter Magyar` | Hungary | Péter Magyar; Respect and Freedom Party |
| `Ursula vdL` | Germany | Ursula von der Leyen; Christian Democratic Union |
| `Ben Z.` | Finland | Ben Zyskowicz; National Coalition Party |
| `Puigdemonnt` | Spain | Carles Puigdemont; Together for Catalonia |
| `PS` | Portugal | Socialist Party |
| `PS` | Finland | Finns Party |
| `PS` | Missing | Keeps competing party matches for review |
| `Greens` | Sweden | Miljöpartiet de Gröna, with the Swedish correction enabled |
| `Donald Trump` | France | Donald Trump; Republican Party; actor country: United States |
| `Le Pen` | France | Keeps competing people for review |

Each result preserves the original mention and includes the proposed identity, party, actor country, similarity scores, competing matches and review flags. These are illustrative inputs and automatic matching results. **A new research run still goes through manual checking.**

## Replication guide

### 1. Get the repository

```bash
git clone https://github.com/econvaibhav/EU-Political-NER.git
cd EU-Political-NER
```

### 2. Create an environment and install the package

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

### 3. Check that the code works

```bash
python -m unittest discover -s tests -v
```

Expected result: **14 tests pass**, ending with `OK`.

### 4. Reproduce the example matches

```bash
python -m political_ner --input examples/mentions.csv --output outputs/demo_matches.jsonl --swedish-greens
```

Expected message:

```text
Wrote 14 mentions; 4 flagged for review.
```

`--swedish-greens` enables the Sweden-specific correction used in the saved example results. `outputs/demo_matches.jsonl` contains one JSON object per input mention.

To compare every result with the saved example output, run:

```bash
python - <<'PY'
import json
from pathlib import Path


def read_results(filename):
    return [json.loads(line) for line in Path(filename).read_text(encoding="utf-8").splitlines() if line.strip()]


actual = read_results("outputs/demo_matches.jsonl")
expected = read_results("examples/example_results.jsonl")
if actual != expected:
    raise SystemExit("Results differ. Check the package versions, data and command flags.")
print(f"All {len(actual)} results match the saved examples.")
PY
```

### 5. Export a draft glossary

```bash
python scripts/build_glossary.py --input outputs/demo_matches.jsonl --output outputs/demo_glossary.csv
```

Open `outputs/demo_glossary.csv` in a spreadsheet or text editor. It groups mentions by entry, party and actor country, and collects their variants. 

### 6. Run your own mentions

Create a UTF-8 CSV with this structure:

```csv
record_id,mention,source_country
mine01,Ursula vdL,Germany
mine02,Magyar Péter,Hungary
mine03,PS,Portugal
```

`mention` is required. `record_id` identifies each row, and `source_country` supplies context where known. Use full country names such as `Hungary` or `Portugal`. Existing input columns called `NER` and `Country` are also supported.

Save your CSV as `data/private/my_mentions.csv`, creating `data/private/` first if needed. That folder is excluded from Git. Then run:

```bash
python -m political_ner --input data/private/my_mentions.csv --output outputs/my_matches.jsonl --swedish-greens
```

Review the suggested identities and affiliations, including `person_alternatives`, `party_alternatives` and `review_reasons`. `needs_review=false` means that no automatic review flag fired; every row still belongs in the manual review process.

### Optional: start from full text

If your input contains full responses rather than extracted names, use the local NER script first. Prepare a CSV at `data/private/documents.csv` with these columns:

```csv
document_id,text,source_country
text01,"Péter Magyar and Viktor Orbán were mentioned.",Hungary
```

Install the optional dependencies and extract mentions:

```bash
python -m pip install -r requirements-ner.txt
python scripts/extract_mentions.py --input data/private/documents.csv --output-dir outputs/extraction
```

This step downloads model weights and runs the local XLM-R checkpoint. Its NER fine-tuning task is English CoNLL-03; check the extracted names carefully for your study languages. The output folder contains `mentions.csv` and `extraction_report.json`, including documents where no entities were found.

Manually check `outputs/extraction/mentions.csv`, then match the reviewed mentions:

```bash
python -m political_ner --input outputs/extraction/mentions.csv --output outputs/text_matches.jsonl --swedish-greens
```
