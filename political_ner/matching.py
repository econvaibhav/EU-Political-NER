"""The notebook's matching rules, with an optional review mode.

Historical mode retains last-write alias lookup, first-best ties, party overrides,
the 82/85/90/95 thresholds and the old unknown-country EU flag. Review mode keeps
alias collisions, uses country only to break tied identities, and abstains on
remaining ties. Neither mode treats a fuzzy score as a probability.
"""
import csv
import string
from functools import lru_cache
from pathlib import Path

from thefuzz import fuzz

COUNTRY_CODES = dict(zip(
    "BG HR FI FR DE HU PL PT ES SE".split(),
    "Bulgaria Croatia Finland France Germany Hungary Poland Portugal Spain Sweden".split()))
EU_COUNTRIES_2025 = set("Austria Belgium Bulgaria Croatia Cyprus Denmark Estonia Finland France Germany Greece Hungary Ireland Italy Latvia Lithuania Luxembourg Malta Netherlands Poland Portugal Romania Slovakia Slovenia Spain Sweden".split()) | {"Czech Republic", "Czechia"}
SYNONYMS = {"french": "France", "german": "Germany", "swedish": "Sweden",
            "polish": "Poland", "spanish": "Spain", "finnish": "Finland"}


@lru_cache(maxsize=20000)
def normalize(text):
    """Original comparison form: lowercase, outer strip, remove ASCII punctuation."""
    return str(text or "").lower().strip().translate(str.maketrans("", "", string.punctuation))


def country_name(value):
    text = " ".join(str(value or "").lower().split())
    if text in {"", "unknown", "nan", "none"}:
        return ""
    return SYNONYMS.get(text, text.title())


def read_csv(path):
    with Path(path).open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


class Resolver:
    def __init__(self, candidates, parties, manual=(), mode="review"):
        if mode not in {"review", "historical"}:
            raise ValueError("mode must be review or historical")
        self.mode = mode
        self.candidates = list(candidates) + list(manual)
        self.people = {}
        self.parties = {}
        for row in self.candidates:
            identity = (row.get("Candidate", ""), row.get("Party", ""), row.get("Country", ""))
            for alias in [row.get("Candidate", ""), row.get("Famname", "")]:
                phrase = normalize(alias)
                if not phrase or not identity[0]:
                    continue
                if mode == "historical":
                    self.people[phrase] = [identity]
                elif identity not in self.people.setdefault(phrase, []):
                    self.people[phrase].append(identity)
        for row in parties:
            identity = (row.get("Party_English", ""), row.get("country_names", ""))
            for field in ["Party_English", "Paty_OwnLanguage", "Abbreviation"]:
                phrase = normalize(row.get(field, ""))
                if phrase and identity[0] and identity not in self.parties.setdefault(phrase, []):
                    self.parties[phrase].append(identity)

    @classmethod
    def from_directory(cls, path, mode="review"):
        path = Path(path)
        return cls(read_csv(path / "reference/candidates.csv"),
                   read_csv(path / "reference/parties.csv"),
                   read_csv(path / "curation/manual_aliases.csv"), mode)

    def person_matches(self, mention):
        best_score, best = 0, []
        for phrase, identities in self.people.items():
            if self.mode == "review" and len(phrase) <= 3 and normalize(mention) != phrase:
                continue
            score = fuzz.token_set_ratio(normalize(mention), phrase)
            if score < 82 or score < best_score:
                continue
            if score > best_score:
                best_score, best = score, []
            for identity in identities:
                if identity not in best:
                    best.append(identity)
        return best_score, best

    def party_matches(self, mention, source_country, current_party):
        potential = []
        for phrase, identities in self.parties.items():
            if self.mode == "review" and len(phrase) <= 3 and normalize(mention) != phrase:
                continue
            score = fuzz.token_set_ratio(normalize(mention), phrase)
            if score >= 85:
                potential.extend((score, party, country) for party, country in identities)
        local = [m for m in potential if m[2].lower().strip() == source_country.lower().strip()]
        eligible = local or (potential if not current_party else [])
        if not eligible:
            return 0, []
        best = max(m[0] for m in eligible)
        if best < (85 if current_party else 90):
            return 0, []
        return best, list(dict.fromkeys((p, c) for s, p, c in eligible if s == best))

    def legacy_country(self, name, party):
        def norm(x):
            return " ".join(str(x or "").lower().split())
        for r in self.candidates:
            if fuzz.ratio(norm(name), norm(r.get("Candidate"))) >= 95 and fuzz.ratio(norm(party), norm(r.get("Party"))) >= 95:
                return country_name(r.get("Country"))
        return ""

    def resolve(self, mention, source_country="", greens=False):
        mention = str(mention or "")
        reasons, alternatives = [], []
        name = party = actor_country = ""
        ns, people = self.person_matches(mention) if mention.strip() else (0, [])
        if self.mode == "review" and len(people) > 1 and country_name(source_country):
            local = [p for p in people if country_name(p[2]) == country_name(source_country)]
            if local:
                people = local
        if people:
            alternatives = [dict(name=n, party=p, country=c) for n, p, c in people]
            if len(people) > 1:
                reasons.append("tied_person_matches")
            if self.mode == "historical" or len(people) == 1:
                name, party, actor_country = people[0]
        ps, parties = self.party_matches(mention, source_country, party)
        if parties:
            if len(parties) > 1:
                reasons.append("tied_party_matches")
            if self.mode == "historical" or len(parties) == 1:
                selected_party, selected_country = parties[0]
                if name and normalize(selected_party) != normalize(party):
                    reasons.append("party_match_conflicts_with_person_affiliation")
                    if self.mode == "historical":
                        party = selected_party
                else:
                    party = selected_party
                    if not name:
                        actor_country = selected_country
        # This was a manual Sweden-specific pass, not a rule for all countries.
        if greens and country_name(source_country) == "Sweden" and max(fuzz.ratio(mention.lower(), x) for x in ["green", "greens"]) >= 90:
            name, party, actor_country = "", "Miljöpartiet de Gröna", "Sweden"
            reasons, alternatives, parties = [], [], [(party, actor_country)]
            ns, ps = 0, max(fuzz.ratio(mention.lower(), x) for x in ["green", "greens"])
        if self.mode == "historical":
            actor_country = self.legacy_country(name, party)
        actor_country = country_name(actor_country)
        eu_countries = EU_COUNTRIES_2025 - ({"Czechia"} if self.mode == "historical" else set())
        eu = int(actor_country in eu_countries) if actor_country else (0 if self.mode == "historical" else None)
        if not name and not party:
            reasons.append("unresolved")
        if not actor_country:
            reasons.append("unknown_actor_country")
        # A complete reference entry is still not independently verified evidence.
        if name and ns < 100:
            reasons.append("fuzzy_person_match")
        if party and ps and ps < 100:
            reasons.append("fuzzy_party_match")
        return {"NER": mention, "Country": source_country, "Names": name, "Party": party,
                "NER_country_cleaned": actor_country, "EU": eu, "name_score": ns,
                "party_score": ps, "mode": self.mode, "needs_review": bool(reasons),
                "review_reasons": reasons, "person_alternatives": alternatives,
                "party_alternatives": [{"party": p, "country": c} for p, c in parties]}
