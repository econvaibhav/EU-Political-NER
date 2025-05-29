import importlib.util
import unittest
from pathlib import Path
from political_ner.matching import Resolver


def person(name, party, country, alias=""):
    return dict(Candidate=name, Party=party, Country=country, Famname=alias)


def party(name, country, abbreviation=""):
    return dict(Party_English=name, Paty_OwnLanguage="", Abbreviation=abbreviation, country_names=country)


class MatchingTests(unittest.TestCase):
    def test_order_invariance_from_token_set_matching(self):
        r = Resolver([person("Péter Magyar", "Respect and Freedom Party", "Hungary")], [])
        out = r.resolve("Magyar Péter", "Hungary")
        self.assertEqual(out["Names"], "Péter Magyar")
        self.assertEqual(out["name_score"], 100)

    def test_manual_alias_keeps_party(self):
        r = Resolver([], [], [person("Ursula von der Leyen", "Christian Democratic Union", "Germany", "Ursula vdL")])
        out = r.resolve("Ursula vdL", "Portugal")
        self.assertEqual((out["Names"], out["Party"], out["NER_country_cleaned"]), ("Ursula von der Leyen", "Christian Democratic Union", "Germany"))

    def test_same_country_party_abbreviation(self):
        r = Resolver([], [party("Finns Party", "Finland", "PS"), party("Socialist Party", "Portugal", "PS")])
        self.assertEqual(r.resolve("PS", "Portugal")["Party"], "Socialist Party")
        self.assertEqual(r.resolve("PS", "Finland")["Party"], "Finns Party")
        self.assertEqual(r.resolve("PS")["Party"], "")

    def test_collision_preserved_in_review_mode(self):
        rows = [person("Alpha Smith", "Party A", "France", "Smith"), person("Beta Smith", "Party B", "France", "Smith")]
        r = Resolver(rows, [])
        out = r.resolve("Smith", "France")
        self.assertEqual(out["Names"], "")
        self.assertEqual(len(out["person_alternatives"]), 2)
        self.assertIn("tied_person_matches", out["review_reasons"])

    def test_historical_alias_last_write_and_first_best(self):
        # Unique aliases collide without also being subsets of either full name.
        rows = [person("Alpha One", "Party A", "France", "pseudonym"), person("Beta Two", "Party B", "Germany", "pseudonym")]
        self.assertEqual(Resolver(rows, [], mode="historical").resolve("pseudonym")["Names"], "Beta Two")

    def test_country_tie_break_is_only_in_review_mode(self):
        rows = [person("Alpha Smith", "Party A", "France"), person("Beta Smith", "Party B", "Germany")]
        self.assertEqual(Resolver(rows, []).resolve("Smith", "Germany")["Names"], "Beta Smith")
        self.assertEqual(Resolver(rows, [], mode="historical").resolve("Smith", "Germany")["Names"], "Alpha Smith")

    def test_country_does_not_reject_clear_foreign_actor(self):
        out = Resolver([person("Donald Trump", "Republican Party", "United States")], []).resolve("Donald Trump", "France")
        self.assertEqual(out["NER_country_cleaned"], "United States")
        self.assertEqual(out["EU"], 0)

    def test_missing_context_cannot_break_a_person_tie(self):
        rows = [person("Alpha Smith", "Party A", ""), person("Beta Smith", "Party B", "Germany")]
        out = Resolver(rows, []).resolve("Smith")
        self.assertEqual(out["Names"], "")
        self.assertEqual(len(out["person_alternatives"]), 2)

    def test_unknown_eu_is_separate_from_non_eu(self):
        self.assertIsNone(Resolver([], []).resolve("unresolved")["EU"])
        self.assertEqual(Resolver([], [], mode="historical").resolve("unresolved")["EU"], 0)

    def test_empty_mention_cannot_link(self):
        out = Resolver([person("Alpha Smith", "Party A", "France")], []).resolve("")
        self.assertEqual(out["Names"], "")
        self.assertTrue(out["needs_review"])

    def test_short_party_alias_cannot_match_inside_an_unrelated_phrase(self):
        r = Resolver([], [party("Alliance", "Finland", "A")])
        self.assertEqual(r.resolve("not a known actor")["Party"], "")
        self.assertEqual(r.resolve("A", "Finland")["Party"], "Alliance")

    def test_swedish_greens_patch_is_scoped(self):
        r = Resolver([], [])
        self.assertEqual(r.resolve("Greens", "Sweden", greens=True)["Party"], "Miljöpartiet de Gröna")
        self.assertEqual(r.resolve("Greens", "Hungary", greens=True)["Party"], "")

    def test_person_party_conflict_is_retained_for_review(self):
        r = Resolver([person("Alpha Coalition", "Other Party", "France")], [party("Alpha Coalition", "France")])
        out = r.resolve("Alpha Coalition", "France")
        self.assertEqual(out["Party"], "Other Party")
        self.assertIn("party_match_conflicts_with_person_affiliation", out["review_reasons"])


class ExtractionTests(unittest.TestCase):
    def test_offsets_labels_and_empty_documents_are_preserved(self):
        path = Path(__file__).parents[1] / "scripts/extract_mentions.py"
        spec = importlib.util.spec_from_file_location("extract_mentions", path)
        module = importlib.util.module_from_spec(spec); spec.loader.exec_module(module)
        def fake(text):
            return [{"entity_group": "PER", "start": 0, "end": 4, "word": "Name", "score": 0.9},
                    {"entity_group": "LOC", "start": 5, "end": 9, "word": "City", "score": 0.9}]
        mentions, documents = module.extract(fake, [{"document_id": "a", "text": "Name City"}, {"document_id": "b", "text": ""}])
        self.assertEqual(len(mentions), 1)
        self.assertEqual(mentions[0]["mention"], "Name")
        self.assertEqual(documents[1]["status"], "no_entities")


if __name__ == "__main__":
    unittest.main()
