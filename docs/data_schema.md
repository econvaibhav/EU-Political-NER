# Output fields

| Field | Meaning |
|---|---|
| `record_id` | Input row identity; the CLI supplies a sequential fallback if absent |
| `NER` | Observed mention, preserved rather than replaced |
| `Country` | Response or run context |
| `Names` | Proposed canonical person name |
| `Party` | Recorded affiliation for that person, or matched party entity |
| `NER_country_cleaned` | Country of the selected reference identity |
| `EU` | 1/0 for known country classification; review mode uses null for unknown |
| `name_score`, `party_score` | String similarity scores, not confidence probabilities |
| `person_alternatives`, `party_alternatives` | Competing best-scoring reference choices |
| `needs_review`, `review_reasons` | Checks that fired; not a substitute for adjudication |
| `mode` | `review` or `historical` |

EP group assignments were researched and corrected manually in the project. The current CLI does not emit `ep_group`; record it separately in the final review table where applicable. The `EU` flag is country-based and is not an EP group label.

Affiliations are copied from the historical reference snapshot. The schema does not yet have valid-from/valid-to dates or a reliable source URL for each affiliation. Avoid interpreting a match as a current fact about that person.
