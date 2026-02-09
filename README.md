# EU Political NER

This is my work on identifying political actors in TikTok and Instagram research notes across ten European countries. I worked on it during December 2024–May 2025, mainly on CSC. The aim was to connect the names people actually wrote to the right person, party and country.

**The country glossaries are one of the biggest contributions of this project.** They bring together months of collecting references, searching names one by one, checking affiliations and reviewing the results with country experts. The examples below show why that work was needed and how to reuse it.

[Browse the glossaries](data/reference/glossaries/) · [See the example results](examples/example_results.jsonl) · [Try the matching code](#try-the-matching-code)

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

## Try the matching code

Python 3.10 or newer:

```bash
python -m pip install -e .
python -m political_ner --input examples/mentions.csv --output outputs/matches.jsonl --swedish-greens
python scripts/build_glossary.py --input outputs/matches.jsonl --output outputs/glossary.csv
python -m unittest discover -s tests -v
```

Input needs `mention` and, where available, `source_country`. Existing `NER` and `Country` columns also work. Output includes the name, party, actor country, scores, alternatives and review flags. Use a new output filename for each run.

The default `review` mode keeps competing identities and leaves unresolved ties for checking. `--mode historical` follows the original matching decisions, including its tie and party-override behaviour. A new automatic run produces matching suggestions; it does not repeat the project's manual searches or final expert reviews.

To prepare the original account-response workbook locally:

```bash
python -m pip install -e '.[spreadsheets]'
python scripts/prepare_accounts.py --input 'data/private/research_notes.xlsx' --output outputs/accounts.csv
```

For the local XLM-R extraction route:

```bash
python -m pip install -r requirements-ner.txt
python scripts/extract_mentions.py --input outputs/accounts.csv --output-dir outputs/extraction
python -m political_ner --input outputs/extraction/mentions.csv --output outputs/account_matches.jsonl
```

This route downloads model weights. The checkpoint has an English CoNLL-03 NER fine-tuning task, even though XLM-R itself is multilingual. It needs evaluation on the actual languages and handles used here.

## Where to look

| Folder | Contents |
|---|---|
| `notebooks/` | Original exploratory code, with outputs and hardcoded keys removed |
| `data/reference/` | Candidate and party tables, earlier versions and country glossaries |
| `data/curation/` | Manual aliases, review instructions and templates for new decisions |
| `political_ner/` | Reusable matching code |
| `scripts/` | Input preparation, local extraction and glossary export |

Raw research responses stay in `data/private/`, which Git ignores. The example inputs are illustrative strings, not respondent records.

## Review and reproducibility

The project used full manual review coverage, including every final row. This describes the review process; it is not a measured claim of perfect accuracy. The supplied files do not include a separate held-out accuracy study or a complete record of every expert decision.

The repo keeps working snapshots from different stages. A fresh model or matching run still needs the manual review steps above. The reusable scripts preserve alternatives and mark cases for attention to support that work.

The candidate lists were scraped from country source websites and PDFs. The complete set of collection scripts and source URLs is not included in this export, so that collection stage cannot yet be rerun end to end. The manually corrected EP groups are part of the project workflow; the current matching CLI does not generate an `ep_group` field automatically.
