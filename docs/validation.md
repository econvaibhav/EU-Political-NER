# Checks

The checks below validate the packaged software. The research workflow also involved manual review of the initial NER output, reference lists and glossaries, followed by final row-by-row expert review across the ten countries; see [manual review](manual_review.md). These are separate kinds of validation.

- Regression fixtures cover token-order matching, manual aliases, country-scoped party abbreviations, ambiguous surnames, foreign actors, missing EU values, empty input, conflicting parties, and the Sweden-specific Greens correction.
- A mocked local-NER response checks that the extraction wrapper retains the text span and no-entity documents without downloading a model.
- Historical mode is compared against the actual person and party functions extracted from notebook cell 5 on the illustrative mentions.
- The supplied research workbook is read locally to check the dimension workaround and separate platform headers. Raw rows are excluded from the public repository.
- A history-builder dry run and a complete temporary Git import check that every commit changes files and the final tracked tree matches the packaged repository.

No remote model calls were made, no model weights were downloaded, and no scraping jobs were run. The LaTeX source was provided without rendering a PDF, as requested. There is no measured precision, recall or F1 score in this release.
