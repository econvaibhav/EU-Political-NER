# Who reviewed what

The project combined automated extraction and matching with repeated manual review. The stages below document the project author's account of the completed research workflow, clarified on 25 September 2026. The notebooks and tables preserve working snapshots of that process.

| Stage | Work and checks | Who did it |
|---|---|---|
| Candidate collection | Scrape candidate lists from original country websites; use webpage and PDF sources | Programmer and country experts |
| Reference review | Manually check the collected names and affiliation information | Programmer and country experts |
| Initial NER review | Manually check all extracted people and parties | Programmer |
| Name and affiliation correction | Search entries one by one; correct spelling, identify the person, check party information and correct EP group assignments where relevant | Programmer's manual research, with country expertise in the wider review process |
| Glossary review | Check canonical entries and their observed spelling variants; revisit duplicate, mixed or incorrect entries | Programmer, followed by the final expert checks |
| Final review | Check every row; make further corrections and feed them back into the data and glossary | Multiple political-science and country experts across the ten countries |

The study countries were Bulgaria, Croatia, Finland, France, Germany, Hungary, Poland, Portugal, Spain and Sweden. This describes multiple reviewers across the project; it does not imply that a reviewer from every country individually read every country's row, or establish a fixed number of reviewers per row.

## Why the manual work matters

Name order, missing accents, misspellings and short forms make string matching difficult. Country context helps with party abbreviations, but the model does not settle every identity or affiliation. Manual searches resolved those cases, and the dictionaries preserved those decisions for reuse. The expert review also supplied political and country knowledge that is not captured by a fuzzy score.

The point is that review was built into each stage, rather than being a small check at the end. All rows were included in the final review according to the project workflow.

## How to describe the coverage

Use: **“All extracted entities, reference lists and glossaries were manually reviewed, and every final row underwent expert review across the ten study countries.”**

“100% of final rows reviewed” describes coverage. “100% accuracy” is a different empirical claim. Full review does not itself establish an error-free result, and no independent accuracy estimate is included in the supplied materials. The diagram therefore states the full review coverage without assigning an accuracy percentage.

## What a fresh run produces

The packaged CLI reproduces the matching stage and supports review. Its output is not automatically a new expert-reviewed release. `needs_review=false` only means that none of the implemented software checks fired. It is not a review sign-off.

EP group corrections belong to the manual enrichment process. The current CLI does not infer or emit `ep_group`. The historical `EU` field is a country-based flag, so it should never be renamed to EP group. The updated decision-log template includes a separate `ep_group` column for recording reviewed values where applicable.

Use `data/curation/decisions_template.csv` to record new corrections and reviewer roles, and `source_log_template.csv` to record sources. These are blank templates for future/recovered records; they do not reconstruct missing historical review logs.
