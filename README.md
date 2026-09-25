# EU Political NER

The aim here to map the names people actually wrote in thier observational notes about parties and political actors they saw on Instagram and Tiktok to the right person, party and country. People many times use the wrong spelling, make up shortforms of the name and rarely ever write the full name, party and country affiliations together. WHile is extremly useful information for research, asking data gatherers to do to this and maintain high accuracy is very hard. Hence this repo does the work for you -- It takes the EU Political entities data gathers might have seen and makes it uniform, **ready for interpretations**!

**The country glossaries is one of the biggest contributions of this project.** It bring together months of collecting references, searching names one by one, checking affiliations and reviewing the results with country experts. The examples below show why that work was needed and how to reuse it.

[Browse the glossaries](data/reference/glossaries/) · [See the example results](examples/example_results.jsonl) · [Run the replication guide](#replication-guide)

## The country glossaries

The ten glossaries cover **Bulgaria, Croatia, Finland, France, Germany, Hungary, Poland, Portugal, Spain and Sweden**. Together, the CSVs contain **2,006 rows and 3,401 recorded variant items**.

A name can appear in a different order, without accents, as initials, as a surname or with several spelling mistakes. The glossaries keep those observed forms together with a canonical entry, recorded party affiliation and actor country. They also retain the source workbook, sheet and row, so an entry can be traced back to its working reference.

Here are some actual entries. The variants are copied from the CSVs; for the longer entries, only a selection is shown.

| Canonical entry | Some recorded variants | Variant items in that row | Glossary |
|---|---|---:|---|
| Péter Magyar | `Magyar Péter`, `Magyar Peter`, `magyar peter`, `magyar péter` | 4 | [Hungary](data/reference/glossaries/hungary.csv) |
| Ursula von der Leyen | `U. VdL`, `Ursula vdL`, `Urs. VDL`, `van der Leyen`, `vDL` | 12 | [Germany](data/reference/glossaries/germany.csv) |
| Jean-Luc Mélenchon | `J L Melenchon`, `JL Melemchon`, `Jl Melanchon`, `Jean Luc Mélenchon`, `Mélenchon`, `Jean-Luck Mélenchon` | 13 | [France](data/reference/glossaries/france.csv) |
| Jordan Bardella | `Jordna Bardella`, `Jordan Badrella`, `Jondan Bardella`, `Bordella`, `Bardellat` | 12 | [France](data/reference/glossaries/france.csv) |
| Boyko Borissov | `Boyko Borisov`, `B. Borissov`, `Borssiov`, `Boyko Borrisov`, `Boyko Borisssov` | 11 | [Bulgaria](data/reference/glossaries/bulgaria.csv) |
| Emmanuel Macron | `Emmanuel Macron`, `Emanuel Macron`, `Macron`, `E Macron` | 6 | [France](data/reference/glossaries/france.csv) |
| Ben Zyskowicz | `Ben Zyskowicz`, `Ben Z`, `Ben Z.` | 3 | [Finland](data/reference/glossaries/finland.csv) |
| Pedro Sánchez | `Pedro Sánchez`, `Pedro Sanchez`, `pedrosanchez`, `peedro sanchez` | 6 | [Spain](data/reference/glossaries/spain.csv) |
| Carles Puigdemont | `Puigdemont`, `Puigdemonnt`, `puigdemont` | 3 | [Spain](data/reference/glossaries/spain.csv) |

This is the practical value of saving the manual work: the next person can inspect and reuse the recorded variants instead of starting every name search from scratch. The files can support dictionary building, matching and review in another project.

The counts describe rows and comma-separated variant items, including differences in case and repeated actors across country files. They are not counts of unique politicians. A glossary's filename identifies the originating country collection; it can include a foreign politician mentioned there. Affiliations are kept as recorded in the research snapshot.

## The manual work behind the dictionaries

Candidate lists were scraped from the original country websites, using webpages or PDFs depending on the country. The programmer and country experts collected and checked this reference material. The programmer also manually reviewed the initial NER output for people and parties.

Spelling corrections, short names, party information and EP group corrections were researched **one entry at a time**. The glossaries were manually reviewed too. Finally, **every row went through checks by multiple political-science and country experts across the ten countries**. The [review table](docs/manual_review.md) shows who worked on each stage.

Alongside the country glossaries, the repo includes **1,833 candidate-reference rows**, **573 party-reference rows**, **275 manual alias rows** and **162 review instructions**. The aliases and review notes preserve more of the decisions made along the way.

## Examples: from a mention to a useful result

The [14 example mentions](examples/mentions.csv) and their [complete saved results](examples/example_results.jsonl) are a quick way to see what the matching code does. They cover name order, initials, misspellings, party abbreviations, foreign actors and ambiguous surnames.

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

Each result preserves the original mention and includes the proposed identity, party, actor country, similarity scores, competing matches and review flags. These are illustrative inputs and automatic matching results. A new research run still goes through manual checking.

## Replication guide

This guide reproduces the example results and exports a small draft glossary. You need **Git and Python 3.10 or newer**. The matching demo runs locally after installation, with **no API key, model download or CSC access required**. Installation needs access to the Python package index.

Run the commands below in a Linux or macOS terminal. On Windows PowerShell, use `python` in place of `python3` and activate the environment with `.venv\Scripts\Activate.ps1`.

### 1. Get the repository

```bash
git clone https://github.com/econvaibhav/EU-Political-NER.git
cd EU-Political-NER
```

If you already have it, open that folder instead. Run the remaining commands from the repository root, where `README.md` and `pyproject.toml` are located.

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

This comparison block uses Linux/macOS shell syntax. It can also be run by copying the Python lines between the two `PY` markers into a `.py` file.

### 5. Export a draft glossary

```bash
python scripts/build_glossary.py --input outputs/demo_matches.jsonl --output outputs/demo_glossary.csv
```

Open `outputs/demo_glossary.csv` in a spreadsheet or text editor. It groups mentions by entry, party and actor country, and collects their variants. The exporter skips flagged results by default. This small demo export is separate from the ten country glossaries created during the project; review its entries before reuse.

The scripts keep existing outputs safe. To repeat a run, choose a new output filename, such as `outputs/demo_matches_02.jsonl`, and use that same filename as the input to the next step.

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

The default `review` mode preserves competing identities and leaves unresolved ties for checking. Add `--mode historical` to reproduce the original matching decisions, including the original tie and party-override behaviour.

The matcher loads `data/reference/candidates.csv`, `data/reference/parties.csv` and `data/curation/manual_aliases.csv`. The ten country glossary CSVs are separate outputs for inspection and reuse; they are not automatically loaded by this command.

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

For repeatable extraction, pass a fixed model commit hash with `--revision`. For another run, choose a new extraction output directory.

If you have the original research workbook layout, `scripts/prepare_accounts.py` can create the document CSV first:

```bash
python -m pip install -e '.[spreadsheets]'
python scripts/prepare_accounts.py --input data/private/research_notes.xlsx --output outputs/accounts.csv
```

Use `outputs/accounts.csv` as the extraction input in that case. The preparation script expects the original column labels defined in `scripts/prepare_accounts.py`.

EP group assignments were researched manually. The CLI's `EU` field describes country membership, and EP group information belongs in a separate reviewed field.

## Where to look

| Location | What is there |
|---|---|
| [Country glossaries](data/reference/glossaries/) | Ten reusable dictionaries of entries and observed variants |
| [Reference tables](data/reference/) | Candidates, parties and earlier working versions |
| [Manual curation](data/curation/) | Aliases, review instructions and templates for new corrections and sources |
| [Examples](examples/) | Fourteen example inputs and their complete matching results |
| [Matching package](political_ner/) | Reusable person and party matching code |
| [Scripts](scripts/) | Input preparation, optional local NER and glossary export |
| [Notebooks](notebooks/) | Original exploratory work, with outputs and hardcoded keys removed |
| [Review table](docs/manual_review.md) | Who collected, checked and reviewed each stage |
| [Output fields](docs/data_schema.md) | Explanation of the fields in a matching result |

The runnable guide covers the packaged extraction, matching and export steps. The original website/PDF collection scripts and complete source URL log are not included. The manual searches and expert reviews are part of the research work that surrounds these commands.
