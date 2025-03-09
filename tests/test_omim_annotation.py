import unittest

from pyhpo.annotations import Omim
from pyhpo.parser.diseases import (
    all_omim_diseases,
    add_omim_to_term,
    add_negative_omim_to_term,
)
from pyhpo.parser.diseases import _add_omim_to_ontology

from tests.mockontology import make_ontology, make_omim


class OmimTests(unittest.TestCase):
    def setUp(self):
        Omim.clear()

    def tearDown(self):
        Omim.clear()

    def test_omim_disease_building(self):
        a = Omim(diseaseid=1, name="Gaucher type I")
        self.assertEqual(a.name, "Gaucher type I")
        self.assertEqual(a.id, 1)
        self.assertEqual(a.hpo, set())

    def test_singleton_handling(self):
        d1a = Omim(diseaseid=1, name="Gaucher")
        # ID present, will be used
        d1b = Omim(diseaseid=1, name="Fabry")
        # No name present, ID will be used as well
        d1c = Omim(diseaseid=1, name=None)

        # New ID, new Name => New Disease
        d2a = Omim(diseaseid=2, name="Fabry")
        # ID present, Matching by ID
        d2b = Omim(diseaseid=2, name="Gaucher")
        # ID present, Matching by ID
        d2c = Omim(diseaseid=2, name=None)

        # New ID but existing name => New disease
        d3a = Omim(diseaseid=3, name="Gaucher")

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

        self.assertEqual(subindex_length(Omim), (0, 0))
        _ = Omim(diseaseid=1, name="Gaucher")
        self.assertEqual(subindex_length(Omim), (1, 1))
        _ = Omim(diseaseid=2, name="Fabry")
        self.assertEqual(subindex_length(Omim), (2, 2))
        Omim.clear()
        self.assertEqual(subindex_length(Omim), (0, 0))

    def test_get_omim(self):
        d1 = Omim(diseaseid=1, name="Gaucher")
        d2 = Omim(diseaseid=2, name="Fabry")

        self.assertEqual(Omim.get(1), d1)
        self.assertEqual(Omim.get(2), d2)
        self.assertEqual(Omim.get("1"), d1)

        self.assertRaises(ValueError, lambda: Omim.get("Fabry"))
        self.assertRaises(KeyError, lambda: Omim.get(12))

    def test_json(self):
        g = Omim(diseaseid=1, name="Foo")

        self.assertEqual(g.toJSON(), {"id": 1, "name": "Foo"})

        self.assertEqual(g.toJSON(verbose=True), {"id": 1, "name": "Foo", "hpo": set()})

    def test_equality(self):
        g = Omim(diseaseid=1, name="Foo")
        self.assertEqual(g, 1)
        self.assertEqual(g, "Foo")

    def test_string_representation(self):
        d = Omim(diseaseid=1, name="Foo")
        self.assertEqual(str(d), "Foo")


class TestOmimAnnotationParsing(unittest.TestCase):
    def setUp(self):
        Omim.clear()
        self.ontology = make_ontology()
        self.omim_diseases = make_omim(5)

    def tearDown(self):
        Omim.clear()

    def test_gene_global_singleton(self):
        assert len(all_omim_diseases()) == 5

    def test_annotating_hpo_terms(self):
        assert self.ontology[1].omim_diseases == set()
        assert self.ontology[11].omim_diseases == set()
        assert self.ontology[21].omim_diseases == set()
        assert self.ontology[31].omim_diseases == set()
        assert self.ontology[12].omim_diseases == set()
        assert self.ontology[41].omim_diseases == set()
        assert self.ontology[13].omim_diseases == set()

        add_omim_to_term(self.omim_diseases[0], self.ontology[21])

        assert self.ontology[1].omim_diseases == set([self.omim_diseases[0]])
        assert self.ontology[11].omim_diseases == set([self.omim_diseases[0]])
        assert self.ontology[21].omim_diseases == set([self.omim_diseases[0]])
        assert self.ontology[31].omim_diseases == set()
        assert self.ontology[12].omim_diseases == set()
        assert self.ontology[41].omim_diseases == set()
        assert self.ontology[13].omim_diseases == set()

        assert self.ontology[1].omim_excluded_diseases == set()
        assert self.ontology[11].omim_excluded_diseases == set()
        assert self.ontology[21].omim_excluded_diseases == set()
        assert self.ontology[31].omim_excluded_diseases == set()
        assert self.ontology[12].omim_excluded_diseases == set()
        assert self.ontology[41].omim_excluded_diseases == set()
        assert self.ontology[13].omim_excluded_diseases == set()

    def test_annotating_hpo_terms_multiple_parents(self):
        add_omim_to_term(self.omim_diseases[0], self.ontology[31])

        assert self.ontology[1].omim_diseases == set([self.omim_diseases[0]])
        assert self.ontology[11].omim_diseases == set([self.omim_diseases[0]])
        assert self.ontology[21].omim_diseases == set([self.omim_diseases[0]])
        assert self.ontology[31].omim_diseases == set([self.omim_diseases[0]])
        assert self.ontology[12].omim_diseases == set([self.omim_diseases[0]])
        assert self.ontology[41].omim_diseases == set()
        assert self.ontology[13].omim_diseases == set()

    def test_negative_annotation(self):
        add_negative_omim_to_term(self.omim_diseases[0], self.ontology[21])

        assert self.ontology[1].omim_diseases == set()
        assert self.ontology[11].omim_diseases == set()
        assert self.ontology[21].omim_diseases == set()
        assert self.ontology[31].omim_diseases == set()
        assert self.ontology[12].omim_diseases == set()
        assert self.ontology[41].omim_diseases == set()
        assert self.ontology[13].omim_diseases == set()

        assert self.ontology[1].omim_excluded_diseases == set()
        assert self.ontology[11].omim_excluded_diseases == set()
        assert self.ontology[21].omim_excluded_diseases == set([self.omim_diseases[0]])
        assert self.ontology[31].omim_excluded_diseases == set([self.omim_diseases[0]])
        assert self.ontology[12].omim_excluded_diseases == set()
        assert self.ontology[41].omim_excluded_diseases == set([self.omim_diseases[0]])
        assert self.ontology[13].omim_excluded_diseases == set()

    def test_negative_annotation_all(self):
        add_negative_omim_to_term(self.omim_diseases[0], self.ontology[1])

        assert self.ontology[1].omim_diseases == set()
        assert self.ontology[11].omim_diseases == set()
        assert self.ontology[21].omim_diseases == set()
        assert self.ontology[31].omim_diseases == set()
        assert self.ontology[12].omim_diseases == set()
        assert self.ontology[41].omim_diseases == set()
        assert self.ontology[13].omim_diseases == set()

        assert self.ontology[1].omim_excluded_diseases == set([self.omim_diseases[0]])
        assert self.ontology[11].omim_excluded_diseases == set([self.omim_diseases[0]])
        assert self.ontology[21].omim_excluded_diseases == set([self.omim_diseases[0]])
        assert self.ontology[31].omim_excluded_diseases == set([self.omim_diseases[0]])
        assert self.ontology[12].omim_excluded_diseases == set([self.omim_diseases[0]])
        assert self.ontology[41].omim_excluded_diseases == set([self.omim_diseases[0]])
        assert self.ontology[13].omim_excluded_diseases == set([self.omim_diseases[0]])

    def test_annotating_hpo_terms_mutliple_omim_diseases(self):
        add_omim_to_term(self.omim_diseases[0], self.ontology[31])
        add_omim_to_term(self.omim_diseases[1], self.ontology[41])

        assert self.ontology[1].omim_diseases == set(
            [self.omim_diseases[0], self.omim_diseases[1]]
        )
        assert self.ontology[11].omim_diseases == set(
            [self.omim_diseases[0], self.omim_diseases[1]]
        )
        assert self.ontology[21].omim_diseases == set(
            [self.omim_diseases[0], self.omim_diseases[1]]
        )
        assert self.ontology[31].omim_diseases == set(
            [self.omim_diseases[1], self.omim_diseases[0]]
        )
        assert self.ontology[12].omim_diseases == set(
            [self.omim_diseases[1], self.omim_diseases[0]]
        )
        assert self.ontology[41].omim_diseases == set([self.omim_diseases[1]])
        assert self.ontology[13].omim_diseases == set()

    def test_full_annotation(self):
        self.omim_diseases[0].hpo.add(31)
        self.omim_diseases[1].hpo.add(41)
        self.omim_diseases[2].negative_hpo.add(12)
        _add_omim_to_ontology(self.ontology)

        assert self.ontology[1].omim_diseases == set(
            [self.omim_diseases[0], self.omim_diseases[1]]
        )
        assert self.ontology[11].omim_diseases == set(
            [self.omim_diseases[0], self.omim_diseases[1]]
        )
        assert self.ontology[21].omim_diseases == set(
            [self.omim_diseases[0], self.omim_diseases[1]]
        )
        assert self.ontology[31].omim_diseases == set(
            [self.omim_diseases[1], self.omim_diseases[0]]
        )
        assert self.ontology[12].omim_diseases == set(
            [self.omim_diseases[1], self.omim_diseases[0]]
        )
        assert self.ontology[41].omim_diseases == set([self.omim_diseases[1]])
        assert self.ontology[13].omim_diseases == set()

        assert self.omim_diseases[0].hpo == set([31])
        assert self.omim_diseases[1].hpo == set([41])

        assert self.ontology[1].omim_excluded_diseases == set()
        assert self.ontology[11].omim_excluded_diseases == set()
        assert self.ontology[21].omim_excluded_diseases == set()
        assert self.ontology[31].omim_excluded_diseases == set([self.omim_diseases[2]])
        assert self.ontology[12].omim_excluded_diseases == set([self.omim_diseases[2]])
        assert self.ontology[41].omim_excluded_diseases == set([self.omim_diseases[2]])
        assert self.ontology[13].omim_excluded_diseases == set()

        assert self.omim_diseases[0].negative_hpo == set()
        assert self.omim_diseases[1].negative_hpo == set()
        assert self.omim_diseases[2].negative_hpo == set([12])


class TestOmimHpoSet(unittest.TestCase):
    def setUp(self):
        Omim.clear()
        self.ontology = make_ontology()
        self.omim_diseases = make_omim(1)
        self.omim_diseases[0].hpo.add(31)
        self.omim_diseases[0].hpo.add(41)
        _add_omim_to_ontology(self.ontology)

    def tearDown(self):
        Omim.clear()

    def test_hpo_set(self):
        disease = Omim.get(0)
        d_set = disease.hpo_set()
        assert len(d_set) == 2
        assert self.ontology[31] in d_set
        assert self.ontology[41] in d_set
        assert self.ontology[1] not in d_set
