# Changes in the reusable code

The five notebooks are the original work, with source code retained and outputs, execution state, personal machine roots and hardcoded API keys removed. They still contain exploratory cells and dependencies on intermediate files. API cells use `OPENAI_API_KEY`; do not run every cell blindly.

The Python package and scripts organise the recovered workflow for reuse. They were prepared with this repository and are not claimed to be the exact environment used on CSC.

| Area | Historical mode / original notebook | Default review mode / portable scripts |
|---|---|---|
| Person aliases | Last value overwrites a duplicate phrase | Keep all competing identities |
| Person ties | First best phrase; no country tie break | Prefer same-country tied identities; leave remaining ties unresolved |
| Person threshold | Token-set ≥82 | Same threshold |
| Very short aliases | Can match as a token inside a longer phrase | Aliases of at most three characters must equal the whole normalised mention |
| Party thresholds | Gather ≥85; apply ≥90, or ≥85 with an existing party | Same thresholds; unresolved party ties are retained as alternatives |
| Person vs party conflict | Party pass can overwrite candidate affiliation | Keep the candidate affiliation and flag the conflict |
| Actor country | First name+party match at ≥95 | Carry country from the selected reference record, including party-only matches |
| Unknown EU | 0 | Missing (`null`), distinct from known non-EU 0 |
| Sweden's Greens | Manual cell, with a mismatched output path afterwards | Explicit `--swedish-greens`, applied only to Sweden |
| Empty input | May become a string or be dropped | Cannot resolve to a person; remains visible |
| Extraction output | Entity strings only; no-entity documents disappear | Keep offsets, scores, labels, model revision and no-entity status |
| Workbook dimensions | Original workbook needs a normal full read | Reset incorrect read-only sheet dimensions before parsing |
| Identifiers | Exact replacements | Also normalise identifier whitespace and case |
| Glossary | Groups by name, potentially mixing differing affiliations | Groups by type, name, party, country and EU state; skips flagged rows by default |
| Files | Hardcoded paths and repeated output filenames | CLI paths; refuse to overwrite result files |

Historical mode is intended to reproduce the core matching decisions, not byte-identical Excel files or remote-model responses. Blank reference rows are omitted, and exact duplicate party options are collapsed without changing the first-best selection. The glossary threshold-60 experiment remains in its original notebook; it is not the default matcher.

`needs_review=false` means none of the implemented checks fired. It does not mean a human verified the match. Review the reference data and keep a decision log before treating outputs as final analysis data.

The EU list is the project's 2025-era country classification. It is not a live geopolitical database. The portable normaliser also recognises `Czechia`; historical data used `Czech Republic`.
