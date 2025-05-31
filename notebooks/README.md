# Working notebooks

These are the five recovered notebooks. Their code cells keep the original order; cell numbers in the method guide are zero-based. Outputs, execution counts, personal machine paths and hardcoded credentials have been removed. An `import os` was added to the first code cell for environment-based keys.

| Notebook | What I used it for |
|---|---|
| `acc_names.ipynb` | Prepare account responses, local NER and handle classification experiments |
| `ner_code.ipynb` | Prompted extraction, 275 manual aliases, person/party matching, country/EU enrichment and plots |
| `adding_glossary.ipynb` | Combine outputs, collect variants and write glossary sheets |
| `bulgaria_test.ipynb` | Merge/split/delete notes, name correction suggestions and candidate checks |
| `new_glossary_2025.ipynb` | Apply correction maps and try the threshold-60 glossary pass |

They are exploratory files, not a clean run-all pipeline. Some cells depend on missing intermediate correction JSON, manually edited workbooks, or a previous cell's dataframe. `output_results.json` refers to different schemas in different folders. API calls are optional and can incur charges when explicitly run with a key.

Use the package and scripts from the root README for the portable workflow. Keep original research responses outside Git in `data/private/`.
