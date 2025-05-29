# Political actor NER

Finding a name was only the first part. I also needed to work out **who the person was, their party and EP group where relevant, and which country the mention referred to**. The main part of this project was the repeated manual checking around those steps.

This is my work on political actor names in TikTok and Instagram research notes. I worked on it during December 2024–May 2025, mainly on CSC. A lot of the time went into scraping candidate lists from the original country websites, checking webpages and PDFs with country experts, and searching for corrections one by one. The reference lists, NER output and glossaries were all manually reviewed. Every row then went through a final check by multiple political-science and country experts across the ten countries.

The ten study countries are Bulgaria, Croatia, Finland, France, Germany, Hungary, Poland, Portugal, Spain and Sweden. The references also include international actors who came up in those countries' responses.

## Why I needed more than NER

People do not all write political names in the same way. They use surnames, initials, account names, local spellings, missing accents and sometimes just a typo. Name order also varies. A party abbreviation can mean something different in another country.

| What came up | What I used to handle it |
|---|---|
| `Magyar Péter` and `Péter Magyar` | Order-insensitive token matching and saved variants. This is not a rule that blindly swaps everyone's name. |
| `Ursula vdL`, `Ben Z.`, `Kaleta` | Manually added aliases linked to a full name and party. |
| `Puigdemonnt`, `Torockay`, `Wiedel` | Observed misspellings in the manual dictionary, plus fuzzy matching. |
| `PS` in Finland or Portugal | Party names in English and local languages, abbreviations, and country context. |
| `Greens` in a Swedish response | A separate country-specific correction. |
| The same surname referring to several people | Manual checking; a high string score alone is not enough. |
| A US politician mentioned in France | Keep the response country and the actor's country separately. |

## What is here

- Five working notebooks, including the main matching code and later glossary experiments.
- A candidate reference with **1,833 nonempty rows** and a party reference with **573 rows**.
- **275 manual alias rows**, covering 196 distinct candidate labels. These include initials, surnames, spelling variants and some account-style names.
- Ten country glossaries with **2,006 rows** and **3,401 comma-separated variant items**. These are row/item counts, not unique politicians or accuracy scores.
- **162 review instructions** to merge, split, delete or check entries.
- Portable scripts, examples, tests and a LaTeX diagram.

The reference files keep their recorded spellings and affiliations. They are a research snapshot, so a party label here should not be read as someone's current affiliation.

## How the original process worked

1. **Build the country references.** Candidate lists came from the original websites for the ten countries, sometimes as webpages and sometimes as PDFs. The programmer and country experts worked on the collection and manually checked the reference material.
2. **Prepare the responses and extract names.** Correct known identifier typos and keep the response country and platform. The notebooks use local XLM-R extraction and separate prompted extraction experiments for people, parties, abbreviations and handles.
3. **Review the NER output.** The programmer manually checked all extracted people and parties before using them in the matching and correction work.
4. **Link people and parties.** Match names and recorded aliases, attach the candidate's party, and use country context to resolve party names and abbreviations. The exact **82 / 85 / 90 / 95** rules are in [the method](docs/method.md).
5. **Search and correct entries one by one.** Resolve misspellings and short names, correct party information and EP group assignments where relevant, and build the glossary from the checked variants. This was manual research, with the glossary itself reviewed too.
6. **Review every final row.** Multiple political-science and country experts across the ten countries checked the final results. Corrections went back into the data and glossaries.
7. **Keep the reviewed results for reuse.** Save the corrected identities, affiliations and reusable country dictionaries.

The review was the core contribution: it covered the reference material, the initial NER output, the glossary and every final row. See [who reviewed what](docs/manual_review.md).

The notebook's `EU` flag describes country membership. The EP group corrections were a separate manual step; `EU` must not be treated as an EP group label.

