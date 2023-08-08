import unittest

from pyhpo.annotations import Decipher
from pyhpo.parser.diseases import all_decipher_diseases
from pyhpo.parser.diseases import add_decipher_to_term
from pyhpo.parser.diseases import add_negative_decipher_to_term
from pyhpo.parser.diseases import _add_decipher_to_ontology

from tests.mockontology import make_ontology, make_decipher


class DecipherTests(unittest.TestCase):
    def setUp(self):
        Decipher.clear()

    def tearDown(self):
        Decipher.clear()

    def test_decipher_disease_building(self):
        a = Decipher(diseaseid=1, name="Gaucher type I")
        self.assertEqual(a.name, "Gaucher type I")
        self.assertEqual(a.id, 1)
        self.assertEqual(a.hpo, set())

    def test_singleton_handling(self):
        d1a = Decipher(diseaseid=1, name="Gaucher")
        # ID present, will be used
        d1b = Decipher(diseaseid=1, name="Fabry")
        # No name present, ID will be used as well
        d1c = Decipher(diseaseid=1, name="")

        # New ID, new Name => New Disease
        d2a = Decipher(diseaseid=2, name="Fabry")
        # ID present, Matching by ID
        d2b = Decipher(diseaseid=2, name="Gaucher")
        # ID present, Matching by ID
        d2c = Decipher(diseaseid=2, name="")

        # New ID but existing name => New disease
        d3a = Decipher(diseaseid=3, name="Gaucher")

        self.assertIs(d1a, d1b)
        self.assertIs(d1a, d1c)

        self.assertIsNot(d1a, d2a)
        self.assertIs(d2a, d2b)
        self.assertIs(d2a, d2c)

        self.assertIsNot(d1a, d3a)
        self.assertIsNot(d2a, d3a)

    def test_indexing(self):
        def subindex_length(x):
            return (
                len(x.keys()),
                len(x._indicies.keys()),
            )

        self.assertEqual(subindex_length(Decipher), (0, 0))
        _ = Decipher(diseaseid=1, name="Gaucher")
        self.assertEqual(subindex_length(Decipher), (1, 1))
        _ = Decipher(diseaseid=2, name="Fabry")
        self.assertEqual(subindex_length(Decipher), (2, 2))
        Decipher.clear()
        self.assertEqual(subindex_length(Decipher), (0, 0))

    def test_get_decipher(self):
        d1 = Decipher(diseaseid=1, name="Gaucher")
        d2 = Decipher(diseaseid=2, name="Fabry")

        self.assertEqual(Decipher.get(1), d1)
        self.assertEqual(Decipher.get(2), d2)
        self.assertEqual(Decipher.get("1"), d1)

        self.assertRaises(ValueError, lambda: Decipher.get("Fabry"))
        self.assertRaises(KeyError, lambda: Decipher.get(12))

    def test_json(self):
        g = Decipher(diseaseid=1, name="Foo")

        self.assertEqual(g.toJSON(), {"id": 1, "name": "Foo"})

        self.assertEqual(g.toJSON(verbose=True), {"id": 1, "name": "Foo", "hpo": set()})

    def test_equality(self):
        g = Decipher(diseaseid=1, name="Foo")
        self.assertEqual(g, 1)
        self.assertEqual(g, "Foo")

    def test_string_representation(self):
        d = Decipher(diseaseid=1, name="Foo")
        self.assertEqual(str(d), "Foo")


class DecipherAnnotationParsing(unittest.TestCase):
    def setUp(self):
        Decipher.clear()
        self.ontology = make_ontology()
        self.decipher_diseases = make_decipher(5)

    def tearDown(self):
        Decipher.clear()

    def test_gene_global_singleton(self):
        assert len(all_decipher_diseases()) == 5

    def test_annotating_hpo_terms(self):
        assert self.ontology[1].decipher_diseases == set()
        assert self.ontology[11].decipher_diseases == set()
        assert self.ontology[21].decipher_diseases == set()
        assert self.ontology[31].decipher_diseases == set()
        assert self.ontology[12].decipher_diseases == set()
        assert self.ontology[41].decipher_diseases == set()
        assert self.ontology[13].decipher_diseases == set()

        add_decipher_to_term(self.decipher_diseases[0], self.ontology[21])

        assert self.ontology[1].decipher_diseases == set([self.decipher_diseases[0]])
        assert self.ontology[11].decipher_diseases == set([self.decipher_diseases[0]])
        assert self.ontology[21].decipher_diseases == set([self.decipher_diseases[0]])
        assert self.ontology[31].decipher_diseases == set()
        assert self.ontology[12].decipher_diseases == set()
        assert self.ontology[41].decipher_diseases == set()
        assert self.ontology[13].decipher_diseases == set()

        assert self.ontology[1].decipher_excluded_diseases == set()
        assert self.ontology[11].decipher_excluded_diseases == set()
        assert self.ontology[21].decipher_excluded_diseases == set()
        assert self.ontology[31].decipher_excluded_diseases == set()
        assert self.ontology[12].decipher_excluded_diseases == set()
        assert self.ontology[41].decipher_excluded_diseases == set()
        assert self.ontology[13].decipher_excluded_diseases == set()

    def test_annotating_hpo_terms_multiple_parents(self):
        add_decipher_to_term(self.decipher_diseases[0], self.ontology[31])

        assert self.ontology[1].decipher_diseases == set([self.decipher_diseases[0]])
        assert self.ontology[11].decipher_diseases == set([self.decipher_diseases[0]])
        assert self.ontology[21].decipher_diseases == set([self.decipher_diseases[0]])
        assert self.ontology[31].decipher_diseases == set([self.decipher_diseases[0]])
        assert self.ontology[12].decipher_diseases == set([self.decipher_diseases[0]])
        assert self.ontology[41].decipher_diseases == set()
        assert self.ontology[13].decipher_diseases == set()

    def test_negative_annotation(self):
        add_negative_decipher_to_term(self.decipher_diseases[0], self.ontology[21])

        assert self.ontology[1].decipher_diseases == set()
        assert self.ontology[11].decipher_diseases == set()
        assert self.ontology[21].decipher_diseases == set()
        assert self.ontology[31].decipher_diseases == set()
        assert self.ontology[12].decipher_diseases == set()
        assert self.ontology[41].decipher_diseases == set()
        assert self.ontology[13].decipher_diseases == set()

        assert self.ontology[1].decipher_excluded_diseases == set()
        assert self.ontology[11].decipher_excluded_diseases == set()
        assert self.ontology[21].decipher_excluded_diseases == set(
            [self.decipher_diseases[0]]
        )
        assert self.ontology[31].decipher_excluded_diseases == set(
            [self.decipher_diseases[0]]
        )
        assert self.ontology[12].decipher_excluded_diseases == set()
        assert self.ontology[41].decipher_excluded_diseases == set(
            [self.decipher_diseases[0]]
        )
        assert self.ontology[13].decipher_excluded_diseases == set()

    def test_negative_annotation_all(self):
        add_negative_decipher_to_term(self.decipher_diseases[0], self.ontology[1])

        assert self.ontology[1].decipher_diseases == set()
        assert self.ontology[11].decipher_diseases == set()
        assert self.ontology[21].decipher_diseases == set()
        assert self.ontology[31].decipher_diseases == set()
        assert self.ontology[12].decipher_diseases == set()
        assert self.ontology[41].decipher_diseases == set()
        assert self.ontology[13].decipher_diseases == set()

        assert self.ontology[1].decipher_excluded_diseases == set(
            [self.decipher_diseases[0]]
        )
        assert self.ontology[11].decipher_excluded_diseases == set(
            [self.decipher_diseases[0]]
        )
        assert self.ontology[21].decipher_excluded_diseases == set(
            [self.decipher_diseases[0]]
        )
        assert self.ontology[31].decipher_excluded_diseases == set(
            [self.decipher_diseases[0]]
        )
        assert self.ontology[12].decipher_excluded_diseases == set(
            [self.decipher_diseases[0]]
        )
        assert self.ontology[41].decipher_excluded_diseases == set(
            [self.decipher_diseases[0]]
        )
        assert self.ontology[13].decipher_excluded_diseases == set(
            [self.decipher_diseases[0]]
        )

    def test_annotating_hpo_terms_mutliple_decipher_diseases(self):
        add_decipher_to_term(self.decipher_diseases[0], self.ontology[31])
        add_decipher_to_term(self.decipher_diseases[1], self.ontology[41])

        assert self.ontology[1].decipher_diseases == set(
            [self.decipher_diseases[0], self.decipher_diseases[1]]
        )
        assert self.ontology[11].decipher_diseases == set(
            [self.decipher_diseases[0], self.decipher_diseases[1]]
        )
        assert self.ontology[21].decipher_diseases == set(
            [self.decipher_diseases[0], self.decipher_diseases[1]]
        )
        assert self.ontology[31].decipher_diseases == set(
            [self.decipher_diseases[1], self.decipher_diseases[0]]
        )
        assert self.ontology[12].decipher_diseases == set(
            [self.decipher_diseases[1], self.decipher_diseases[0]]
        )
        assert self.ontology[41].decipher_diseases == set([self.decipher_diseases[1]])
        assert self.ontology[13].decipher_diseases == set()

    def test_full_annotation(self):
        self.decipher_diseases[0].hpo.add(31)
        self.decipher_diseases[1].hpo.add(41)
        self.decipher_diseases[2].negative_hpo.add(12)
        _add_decipher_to_ontology(self.ontology)

        assert self.ontology[1].decipher_diseases == set(
            [self.decipher_diseases[0], self.decipher_diseases[1]]
        )
        assert self.ontology[11].decipher_diseases == set(
            [self.decipher_diseases[0], self.decipher_diseases[1]]
        )
        assert self.ontology[21].decipher_diseases == set(
            [self.decipher_diseases[0], self.decipher_diseases[1]]
        )
        assert self.ontology[31].decipher_diseases == set(
            [self.decipher_diseases[1], self.decipher_diseases[0]]
        )
        assert self.ontology[12].decipher_diseases == set(
            [self.decipher_diseases[1], self.decipher_diseases[0]]
        )
        assert self.ontology[41].decipher_diseases == set([self.decipher_diseases[1]])
        assert self.ontology[13].decipher_diseases == set()

        assert self.decipher_diseases[0].hpo == set([31])
        assert self.decipher_diseases[1].hpo == set([41])

        assert self.ontology[1].decipher_excluded_diseases == set()
        assert self.ontology[11].decipher_excluded_diseases == set()
        assert self.ontology[21].decipher_excluded_diseases == set()
        assert self.ontology[31].decipher_excluded_diseases == set(
            [self.decipher_diseases[2]]
        )
        assert self.ontology[12].decipher_excluded_diseases == set(
            [self.decipher_diseases[2]]
        )
        assert self.ontology[41].decipher_excluded_diseases == set(
            [self.decipher_diseases[2]]
        )
        assert self.ontology[13].decipher_excluded_diseases == set()

        assert self.decipher_diseases[0].negative_hpo == set()
        assert self.decipher_diseases[1].negative_hpo == set()
        assert self.decipher_diseases[2].negative_hpo == set([12])
