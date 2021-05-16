import unittest

from pyhpo.annotations import Orpha
from pyhpo.parser.diseases import all_orpha_diseases, add_orpha_to_term, add_negative_orpha_to_term
from pyhpo.parser.diseases import _add_orpha_to_ontology

from tests.mockontology import make_ontology, make_orpha


class OrphaTests(unittest.TestCase):
    def setUp(self):
        Orpha.clear()

    def tearDown(self):
        Orpha.clear()

    def test_orpha_disease_building(self):
        a = Orpha(diseaseid=1, name='Gaucher type I')
        self.assertEqual(
            a.name,
            'Gaucher type I'
        )
        self.assertEqual(
            a.id,
            1
        )
        self.assertEqual(
            a.hpo,
            set()
        )

    def test_singleton_handling(self):
        d1a = Orpha(diseaseid=1, name='Gaucher')
        # ID present, will be used
        d1b = Orpha(diseaseid=1, name='Fabry')
        # No name present, ID will be used as well
        d1c = Orpha(diseaseid=1, name=None)

        # New ID, new Name => New Disease
        d2a = Orpha(diseaseid=2, name='Fabry')
        # ID present, Matching by ID
        d2b = Orpha(diseaseid=2, name='Gaucher')
        # ID present, Matching by ID
        d2c = Orpha(diseaseid=2, name=None)

        # New ID but existing name => New disease
        d3a = Orpha(diseaseid=3, name='Gaucher')

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

        self.assertEqual(
            subindex_length(Orpha),
            (0, 0)
        )
        _ = Orpha(diseaseid=1, name='Gaucher')
        self.assertEqual(
            subindex_length(Orpha),
            (1, 1)
        )
        _ = Orpha(diseaseid=2, name='Fabry')
        self.assertEqual(
            subindex_length(Orpha),
            (2, 2)
        )
        Orpha.clear()
        self.assertEqual(
            subindex_length(Orpha),
            (0, 0)
        )

    def test_get_orpha(self):
        d1 = Orpha(diseaseid=1, name='Gaucher')
        d2 = Orpha(diseaseid=2, name='Fabry')

        self.assertEqual(Orpha.get(1), d1)
        self.assertEqual(Orpha.get(2), d2)
        self.assertEqual(Orpha.get('1'), d1)

        self.assertRaises(
            ValueError,
            lambda: Orpha.get('Fabry')
        )
        self.assertRaises(
            KeyError,
            lambda: Orpha.get(12)
        )

    def test_json(self):
        g = Orpha(diseaseid=1, name='Foo')

        self.assertEqual(
            g.toJSON(),
            {'id': 1, 'name': 'Foo'}
        )

        self.assertEqual(
            g.toJSON(verbose=True),
            {'id': 1, 'name': 'Foo', 'hpo': set()}
        )

    def test_equality(self):
        g = Orpha(diseaseid=1, name='Foo')
        self.assertEqual(g, 1)
        self.assertEqual(g, 'Foo')

    def test_string_representation(self):
        d = Orpha(diseaseid=1, name='Foo')
        self.assertEqual(str(d), 'Foo')


class TestOrphaAnnotationParsing(unittest.TestCase):
    def setUp(self):
        Orpha.clear()
        self.ontology = make_ontology()
        self.orpha_diseases = make_orpha(5)

    def tearDown(self):
        Orpha.clear()

    def test_gene_global_singleton(self):
        assert len(all_orpha_diseases()) == 5

    def test_annotating_hpo_terms(self):
        assert self.ontology[1].orpha_diseases == set()
        assert self.ontology[11].orpha_diseases == set()
        assert self.ontology[21].orpha_diseases == set()
        assert self.ontology[31].orpha_diseases == set()
        assert self.ontology[12].orpha_diseases == set()
        assert self.ontology[41].orpha_diseases == set()
        assert self.ontology[13].orpha_diseases == set()

        add_orpha_to_term(self.orpha_diseases[0], self.ontology[21])
        
        assert self.ontology[1].orpha_diseases == set([self.orpha_diseases[0]])
        assert self.ontology[11].orpha_diseases == set([self.orpha_diseases[0]])
        assert self.ontology[21].orpha_diseases == set([self.orpha_diseases[0]])
        assert self.ontology[31].orpha_diseases == set()
        assert self.ontology[12].orpha_diseases == set()
        assert self.ontology[41].orpha_diseases == set()
        assert self.ontology[13].orpha_diseases == set()

        assert self.ontology[1].orpha_excluded_diseases == set()
        assert self.ontology[11].orpha_excluded_diseases == set()
        assert self.ontology[21].orpha_excluded_diseases == set()
        assert self.ontology[31].orpha_excluded_diseases == set()
        assert self.ontology[12].orpha_excluded_diseases == set()
        assert self.ontology[41].orpha_excluded_diseases == set()
        assert self.ontology[13].orpha_excluded_diseases == set()

    def test_annotating_hpo_terms_multiple_parents(self):
        add_orpha_to_term(self.orpha_diseases[0], self.ontology[31])
        
        assert self.ontology[1].orpha_diseases == set([self.orpha_diseases[0]])
        assert self.ontology[11].orpha_diseases == set([self.orpha_diseases[0]])
        assert self.ontology[21].orpha_diseases == set([self.orpha_diseases[0]])
        assert self.ontology[31].orpha_diseases == set([self.orpha_diseases[0]])
        assert self.ontology[12].orpha_diseases == set([self.orpha_diseases[0]])
        assert self.ontology[41].orpha_diseases == set()
        assert self.ontology[13].orpha_diseases == set()

    def test_negative_annotation(self):
        add_negative_orpha_to_term(self.orpha_diseases[0], self.ontology[21])
        
        assert self.ontology[1].orpha_diseases == set()
        assert self.ontology[11].orpha_diseases == set()
        assert self.ontology[21].orpha_diseases == set()
        assert self.ontology[31].orpha_diseases == set()
        assert self.ontology[12].orpha_diseases == set()
        assert self.ontology[41].orpha_diseases == set()
        assert self.ontology[13].orpha_diseases == set()

        assert self.ontology[1].orpha_excluded_diseases == set()
        assert self.ontology[11].orpha_excluded_diseases == set()
        assert self.ontology[21].orpha_excluded_diseases == set([
            self.orpha_diseases[0]
        ])
        assert self.ontology[31].orpha_excluded_diseases == set([
            self.orpha_diseases[0]
        ])
        assert self.ontology[12].orpha_excluded_diseases == set()
        assert self.ontology[41].orpha_excluded_diseases == set([
            self.orpha_diseases[0]
        ])
        assert self.ontology[13].orpha_excluded_diseases == set()

    def test_negative_annotation_all(self):
        add_negative_orpha_to_term(self.orpha_diseases[0], self.ontology[1])
        
        assert self.ontology[1].orpha_diseases == set()
        assert self.ontology[11].orpha_diseases == set()
        assert self.ontology[21].orpha_diseases == set()
        assert self.ontology[31].orpha_diseases == set()
        assert self.ontology[12].orpha_diseases == set()
        assert self.ontology[41].orpha_diseases == set()
        assert self.ontology[13].orpha_diseases == set()

        assert self.ontology[1].orpha_excluded_diseases == set([
            self.orpha_diseases[0]
        ])
        assert self.ontology[11].orpha_excluded_diseases == set([
            self.orpha_diseases[0]
        ])
        assert self.ontology[21].orpha_excluded_diseases == set([
            self.orpha_diseases[0]
        ])
        assert self.ontology[31].orpha_excluded_diseases == set([
            self.orpha_diseases[0]
        ])
        assert self.ontology[12].orpha_excluded_diseases == set([
            self.orpha_diseases[0]
        ])
        assert self.ontology[41].orpha_excluded_diseases == set([
            self.orpha_diseases[0]
        ])
        assert self.ontology[13].orpha_excluded_diseases == set([
            self.orpha_diseases[0]
        ])

    def test_annotating_hpo_terms_mutliple_orpha_diseases(self):
        add_orpha_to_term(self.orpha_diseases[0], self.ontology[31])
        add_orpha_to_term(self.orpha_diseases[1], self.ontology[41])
        
        assert self.ontology[1].orpha_diseases == set([
            self.orpha_diseases[0],
            self.orpha_diseases[1]
        ])
        assert self.ontology[11].orpha_diseases == set([
            self.orpha_diseases[0],
            self.orpha_diseases[1]
        ])
        assert self.ontology[21].orpha_diseases == set([
            self.orpha_diseases[0],
            self.orpha_diseases[1]
        ])
        assert self.ontology[31].orpha_diseases == set([
            self.orpha_diseases[1],
            self.orpha_diseases[0]
        ])
        assert self.ontology[12].orpha_diseases == set([
            self.orpha_diseases[1],
            self.orpha_diseases[0]
        ])
        assert self.ontology[41].orpha_diseases == set([
            self.orpha_diseases[1]
        ])
        assert self.ontology[13].orpha_diseases == set()

    def test_full_annotation(self):
        self.orpha_diseases[0].hpo.add(31)
        self.orpha_diseases[1].hpo.add(41)
        self.orpha_diseases[2].negative_hpo.add(12)
        _add_orpha_to_ontology(self.ontology)

        assert self.ontology[1].orpha_diseases == set([
            self.orpha_diseases[0],
            self.orpha_diseases[1]
        ])
        assert self.ontology[11].orpha_diseases == set([
            self.orpha_diseases[0],
            self.orpha_diseases[1]
        ])
        assert self.ontology[21].orpha_diseases == set([
            self.orpha_diseases[0],
            self.orpha_diseases[1]
        ])
        assert self.ontology[31].orpha_diseases == set([
            self.orpha_diseases[1],
            self.orpha_diseases[0]
        ])
        assert self.ontology[12].orpha_diseases == set([
            self.orpha_diseases[1],
            self.orpha_diseases[0]
        ])
        assert self.ontology[41].orpha_diseases == set([
            self.orpha_diseases[1]
        ])
        assert self.ontology[13].orpha_diseases == set()

        assert self.orpha_diseases[0].hpo == set([31])
        assert self.orpha_diseases[1].hpo == set([41])

        assert self.ontology[1].orpha_excluded_diseases == set()
        assert self.ontology[11].orpha_excluded_diseases == set()
        assert self.ontology[21].orpha_excluded_diseases == set()
        assert self.ontology[31].orpha_excluded_diseases == set([
            self.orpha_diseases[2]
        ])
        assert self.ontology[12].orpha_excluded_diseases == set([
            self.orpha_diseases[2]
        ])
        assert self.ontology[41].orpha_excluded_diseases == set([
            self.orpha_diseases[2]
        ])
        assert self.ontology[13].orpha_excluded_diseases == set()

        assert self.orpha_diseases[0].negative_hpo == set()
        assert self.orpha_diseases[1].negative_hpo == set()
        assert self.orpha_diseases[2].negative_hpo == set([12])
