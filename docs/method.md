# What the code actually does

The overall research process included manual review of the scraped references, all initial NER output, the glossaries and every final row. The programmer checked the NER output and researched corrections one by one; the programmer and country experts checked the reference material; multiple political-science and country experts performed the final review across all ten countries. EP group corrections were part of that manual work. See [who reviewed what](manual_review.md).

The sections below trace the **automated and exploratory notebook steps** within that wider process. They should not be read as the entire review procedure.

Cell numbers below are zero-based, as in the supplied notebook JSON. The source notebooks preserve this numbering. They contain experiments and hardcoded paths, so they should be read as working notebooks rather than run top to bottom without checking the inputs.

## 1. Prepare account responses

`acc_names.ipynb`, cells 0–3:

- Load the research-notes workbook. There are 1,608 data rows and 40 columns. Its stored sheet dimensions incorrectly say `A1:A1`; the portable reader resets the dimensions before reading.
- Rename the two account questions to `accountnames_tiktok` and `accountnames_instagram`. Their source headers differ by a trailing newline, so stripping both before renaming would collapse their identities.
- Apply the recorded ID corrections: `DE§ → DE3`, `BG4 → BG3`, `F13 → FI3`, `HRO/HRS → HR2`, `HU0 → HU3`. The original `.replace({' ': ''})` only replaces a whole cell equal to one space; it does not remove embedded spaces.
- Use the first two identifier characters to derive a study country. Keep the response ID and platform when melting the two columns into rows.
- Drop missing response values and replace comma/semicolon separators with a consistent delimiter. Export one file per country.

The main people/party-visibility responses and the account-name responses are separate branches. Counts from one should not be added to the other without checking IDs and question columns.

## 2. Extract mentions

**Local model route — `acc_names.ipynb`, cells 4–5.** XLM-R large, fine-tuned on English CoNLL-03, with `aggregation_strategy='simple'`. Keep `PER` and `ORG`. The original output retains the response ID, original text and entity string, but loses the model label, score and offsets. Responses without an extracted entity disappear from that table.

**Prompted route — `ner_code.ipynb`, cells 1–5.** Reduce the imported table to unique original texts, then ask GPT-4o-mini to extract people, parties, abbreviations and account names. The surviving prompt is focused on Sweden but explicitly permits other EU and US actors. It asks to preserve misspellings and complete handles. Parameters are temperature 0 and a 10-second timeout. Results are expected as a JSON `NER` list, joined with commas and later split into entity rows.

This is an extraction prompt, not evidence that the system infers the correct country from every ambiguous sentence. The country in the source code is also manually set for each run. Deduplicating by response text can remove repeated observations; inserting an API error into `NER` can accidentally send an error message to the matcher.

**Handle classification — `acc_names.ipynb`, cells 7–8.** Separate GPT-4o-mini experiments classify whole mentions or whitespace tokens as handle/not-handle. Tokens lose sentence context, failures default to 0, and the final filename says TikTok even though the loop does not filter the input platform. A handle prediction does not verify official account ownership.

## 3. Link people and attach their party

`ner_code.ipynb`, cell 5:

1. Load the newer candidate table (`mep_party_cleaned3 (1) (1).xlsx`). Append the 275 inline `additional_candidates` records.
2. Each candidate contributes its full name; the manual rows also contribute `Famname`. Here `Famname` is an alias field, not a reliable surname parser: it contains initials, nicknames, full names, typos and handles.
3. Lowercase and trim each string and remove ASCII punctuation. TheFuzz then applies its own default preprocessing; there is no separate, general transliteration or Unicode-normalisation system in the notebook.
4. Build a dictionary from each comparison phrase to `(Candidate, Party, Country)`. A repeated phrase overwrites the previous value.
5. Score every mention against every phrase with `fuzz.token_set_ratio`. Accept a score **≥82**, replacing the best result only when the score is strictly higher. Equal scores therefore retain the first best phrase in iteration order.
6. Save the selected full name and its recorded party. Although the dictionary contains country, the person-scoring loop ignores it.

Token-set matching is insensitive to token order. That explains support for name-order variants such as `Magyar Péter` / `Péter Magyar`; there is no per-country parser that decides which token is a surname. Token subsets can also score 100, so surnames and common first names can create ties. Alias collisions and surname ambiguity are distinct problems.

## 4. Match parties with country context

`ner_code.ipynb`, cell 5, `process_party_row`:

- Build phrases from `Party_English`, `Paty_OwnLanguage` (the original header spelling) and `Abbreviation`.
- Retain a list of party/country pairs for each phrase. This preserves repeated abbreviations across countries.
- Collect potential matches with token-set score **≥85**.
- If there are matches from the response country, choose the highest-scoring one among those.
- Otherwise, consider other-country matches **only if the current party is empty**.
- Apply a selected match at **≥90**; a score of **85–89** is applied only when a party is already present. Otherwise retain the existing party.

The local-country preference comes before selecting the best score. This means a local 86 can outrank a foreign 100 for candidate selection, even if the later 90 rule prevents filling an empty party. A same-country party match can also overwrite the party attached during the person pass. Both behaviours are preserved in historical mode.

`PS` is a useful example: the party reference contains entries for Finland and Portugal. The context country is a disambiguating clue. It is not proof that an actor mentioned in a response must come from that country.

## 5. Manual country corrections and enrichment

`ner_code.ipynb`, cells 8–18:

- A separate Sweden correction matches `green`/`greens` exactly or at `fuzz.ratio ≥90`, clears `Names`, and writes `Miljöpartiet de Gröna` to `Party`. One subsequent output path names Hungary despite the Swedish input and rule. The portable option scopes this to Sweden.
- Look up the resolved name and party together in the candidate references, later extended with the manual candidates.
- Require both name and party to match at `fuzz.ratio ≥95`, or exactly after case/whitespace normalisation. Return the first qualifying country.
- Map `french`, `german`, `swedish`, `polish`, `spanish`, and `finnish` to country names. Other values receive simple title casing.
- Set `EU=1` for countries in the notebook's EU list; everything else, including unknown country, becomes 0.

`Country` is the response/run context. `NER_country_cleaned` is the inferred actor country. `EU` describes that country-based classification; it does not identify an EP political group. Person-based country lookup leaves party-only rows without a country. All 196 party-tagged rows in the saved country glossaries have `Country=Unknown` and `EU=0`.

## 6. Manual review and dictionary building

`bulgaria_test.ipynb`, cells 1–8, records **162 instructions**: 122 merge lines, 23 separate/divide lines, 15 delete lines and two other checks. Despite the notebook's filename, it reads the shared glossary from the Spain workbook. That shared glossary contains all countries.

Only lines containing `merge` are programmatically selected. Numbers are extracted by regex and used with `df.iloc`: they are positional, zero-based references, not stable IDs. The remaining 40 instructions are not applied by that loop. The notebook requests spelling/diacritic suggestions from GPT-3.5-turbo for each merge group. A suggestion is not independent factual verification.

Another experiment (`bulgaria_test`, cell 10) asks GPT-4o-mini to check candidate/party/country consistency, return English labels, domestic party names, abbreviations and alliances. It requests English spellings for Bulgarian candidates and permits native-language names elsewhere. The supplied text files record 1,593 `all_correct` lines and 535 `incorrect` lines; those labels are model judgements, and the incorrect path also includes request failures. The script does not preserve corrected fields in those text logs.

Manual effort is also visible in the separate Finnish and Polish `NER`/`NER2` versions. After confirming unchanged source columns, 64 Finnish rows and 274 Polish rows have changed name or party fields. These are observable corrections, not a count of hours or individual editing sessions.

## 7. Build and reuse glossaries

`adding_glossary.ipynb` groups raw `NER` variants by resolved `Names`. If no name exists but a party does, it groups by `Party`. Later exports include `Type`, `Entry`, `Variations`, `Party`, `Country`, and `EU`. Exact duplicate glossary rows are removed.

The older ten country workbooks each contain the same 1,889-row shared glossary. They are not ten distinct vocabularies. The later ten country glossaries total 2,006 rows, including ten blank entries, and 3,401 comma-separated variant items.

The earlier merge script scans all `.xlsx` files in its output folder. That can re-import existing combined outputs and multiple country versions. It is a concrete duplication risk, but it does not prove that every duplicated output row came from that cause.

`new_glossary_2025.ipynb` first applies an `Original → CorrectedName` correction map, then drops duplicate `Entry` values. A later cell creates a list of canonical entries and comma-separated variations, and calls `process.extractOne` on whole `Persons` and `Parties` strings with **threshold 60**. The default scorer is WRatio, not the main matcher's token-set scorer. This pass has no type or country restriction and can lose conflicting mappings through a single-value dictionary.

There are two different files called `output_results.json` in these experiments. The supplied one has 4,988 rows with `Original`, `Persons`, `Parties`, `corrected_persons`, and `corrected_parties`; it is not the missing `Original`-as-list / `CorrectedName` correction file. It also contains non-standard JSON `NaN` values (26 person corrections and 208 party corrections). Do not interchange the two schemas or treat either as a validation set.

## Collection and scraping

Candidate lists were scraped from the original country websites, using webpages or PDFs depending on the country. The programmer and country experts worked on the collection and manually reviewed the reference material. This provenance was clarified by the project author.

The supplied export includes the collected references and manual dictionary, but not the complete candidate scrapers, PDF collection scripts or source-by-source URL log. The generic Google-search experiment in the main notebook is a separate fragment, not a record of the whole collection process. `data/curation/source_log_template.csv` provides a place to add recovered URLs and dates.

## What these files do not measure

The author reports complete manual review coverage, including every final row and repeated expert review. That review procedure is distinct from an independently measured accuracy estimate. There is no separate gold-labelled held-out test set, precision/recall/F1 report, or verified handle-ownership benchmark in the supplied files. The changes address real error types, but the size of any accuracy improvement is unknown. Stored party affiliations are snapshots without validity intervals and need dates/sources before longitudinal analysis.
