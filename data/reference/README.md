# Reference tables

Candidate lists were scraped from original country websites, using webpage and PDF sources, and checked by the programmer and country experts. The glossaries were manually reviewed, and the project included final checks of every row by multiple political-science and country experts.

These files are CSV exports of the supplied working snapshots. Source file, sheet and row are retained. No public person's party or identity has been updated to today's values.

`candidates.csv` is the newer candidate reference: 1,833 nonempty rows. Two trailing empty spreadsheet rows are omitted. `parties.csv` has 573 nonempty rows; formatting extends the worksheet to row 1,002 but those extra rows are empty.

`versions/` preserves earlier tables and the shared/cleaned glossaries. The old 2,128-row candidate table mixes schemas: after its initial candidate/party/country section, many rows act as alias/canonical-name/party mappings under the old headers. It is retained for comparison and is not loaded by the portable matcher.

`glossaries/` contains the ten later country dictionaries, 2,006 rows in total. Blank entries, historical mistakes, duplicate identities, unknown countries and different party labels are retained. A country filename describes the originating response collection; it is not necessarily the actor's nationality.

The candidate and party tables do not contain source URLs or time-bounded affiliation records. Add those with the curation templates when they can be recovered. No blanket licence is assigned to third-party source material.
