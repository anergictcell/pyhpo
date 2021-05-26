import unittest

from pyhpo.annotations import Gene
from pyhpo.parser.genes import all_genes, add_gene_to_term
from pyhpo.parser.genes import _add_genes_to_ontology

from tests.mockontology import make_ontology, make_genes


class GeneTests(unittest.TestCase):
    def setUp(self):
        Gene.clear()

    def tearDown(self):
        Gene.clear()

    def test_gene_building(self):
        a = Gene(hgncid=1, symbol='EZH2')
        self.assertEqual(
            a.name,
            'EZH2'
        )
        self.assertEqual(
            a.id,
            1
        )
        self.assertEqual(
            a.symbol,
            'EZH2'
        )
        self.assertEqual(
            a.hpo,
            set()
        )

    def test_singleton_handling(self):
        a = Gene(hgncid=1, symbol='EZH2')
        # When no name is given, ID is used for comparison
        b = Gene(hgncid=1, symbol=None)
        # EZH1 does not exist, but ID is used for comparison
        c = Gene(hgncid=1, symbol='EZH1')
        # EZH2 exists, is used for comparison
        d = Gene(hgncid=2, symbol='EZH2')
        # EZH2 exists, is used for comparison
        e = Gene(hgncid=None, symbol='EZH2')

        # EZH1 does not exist. ID does not exist => New Gene
        f = Gene(hgncid=2, symbol='EZH1')
        # ID is used for comparison
        g = Gene(hgncid=2, symbol='EZH2')
        # EZH1 is used for comparison
        h = Gene(hgncid=1, symbol='EZH1')
        # EZH1 is used for comparison
        i = Gene(hgncid=None, symbol='EZH1')

        self.assertIs(a, b)
        self.assertIs(a, c)
        self.assertIs(a, d)
        self.assertIs(a, e)
        self.assertIsNot(a, f)
        self.assertIs(a, g)
        self.assertIsNot(a, h)
        self.assertIs(f, h)
        self.assertIs(f, i)

        self.assertEqual(a, b)
        self.assertEqual(a, c)
        self.assertEqual(a, d)
        self.assertEqual(a, e)
        self.assertEqual(a, g)
        self.assertEqual(b, c)
        self.assertEqual(b, d)
        self.assertEqual(b, e)
        self.assertEqual(b, g)
        self.assertEqual(c, d)
        self.assertEqual(c, e)
        self.assertEqual(c, g)
        self.assertEqual(d, e)
        self.assertEqual(d, g)
        self.assertEqual(e, g)
        self.assertNotEqual(a, f)
        self.assertNotEqual(a, h)
        self.assertNotEqual(a, i)
        self.assertNotEqual(b, f)
        self.assertNotEqual(b, h)
        self.assertNotEqual(b, i)
        self.assertNotEqual(c, f)
        self.assertNotEqual(c, h)
        self.assertNotEqual(c, i)
        self.assertNotEqual(d, f)
        self.assertNotEqual(d, h)
        self.assertNotEqual(d, i)
        self.assertNotEqual(e, f)
        self.assertNotEqual(e, h)
        self.assertNotEqual(e, i)

        self.assertEqual(f, h)
        self.assertEqual(f, i)
        self.assertEqual(h, i)

        self.assertEqual(
            len(Gene.keys()),
            2
        )
        self.assertEqual(
            len(Gene.values()),
            2
        )
        self.assertEqual(
            len(set(Gene.values())),
            2
        )

    def test_indexing(self):
        def subindex_length(x):
            return (
                len(x.keys()),
                len(x._indicies.keys()),
                len(x._names.keys())
            )

        self.assertEqual(
            subindex_length(Gene),
            (0, 0, 0)
        )
        _ = Gene(hgncid=1, symbol='EZH1')
        self.assertEqual(
            subindex_length(Gene),
            (1, 1, 1)
        )
        _ = Gene(hgncid=2, symbol='EZH2')
        self.assertEqual(
            subindex_length(Gene),
            (2, 2, 2)
        )
        Gene.clear()
        self.assertEqual(
            subindex_length(Gene),
            (0, 0, 0)
        )

    def test_get_gene(self):
        g1 = Gene(hgncid=1, symbol='EZH1')
        g2 = Gene(hgncid=2, symbol='EZH2')

        self.assertEqual(Gene.get(1), g1)
        self.assertEqual(Gene.get(2), g2)
        self.assertEqual(Gene.get('1'), g1)
        self.assertEqual(Gene.get('EZH1'), g1)
        self.assertEqual(Gene.get('EZH2'), g2)

        self.assertRaises(
            KeyError,
            lambda: Gene.get('GBA')
        )
        self.assertRaises(
            KeyError,
            lambda: Gene.get(12)
        )


class TestAnnotationBase(unittest.TestCase):
    def setUp(self):
        Gene.clear()

    def tearDown(self):
        Gene.clear()

    def test_json(self):
        g = Gene(hgncid=1, symbol='Foo')

        self.assertEqual(
            g.toJSON(),
            {'id': 1, 'name': 'Foo', 'symbol': 'Foo'}
        )

        self.assertEqual(
            g.toJSON(verbose=True),
            {'id': 1, 'name': 'Foo', 'symbol': 'Foo', 'hpo': set()}
        )

    def test_equality(self):
        g = Gene(hgncid=1, symbol='Foo')
        self.assertEqual(g, 1)
        self.assertEqual(g, 'Foo')

    def test_string_representation(self):
        g = Gene(hgncid=1, symbol='Foo')
        self.assertEqual(str(g), 'Foo')


class TestGeneAnnotationParsing(unittest.TestCase):
    def setUp(self):
        self.ontology = make_ontology()
        self.genes = make_genes(5)

    def tearDown(self):
        Gene.clear()

    def test_gene_global_singleton(self):
        assert len(all_genes()) == 5

    def test_annotating_hpo_terms(self):
        assert self.ontology[1].genes == set()
        assert self.ontology[11].genes == set()
        assert self.ontology[21].genes == set()
        assert self.ontology[31].genes == set()
        assert self.ontology[12].genes == set()
        assert self.ontology[41].genes == set()
        assert self.ontology[13].genes == set()

        add_gene_to_term(self.genes[0], self.ontology[21])
        
        assert self.ontology[1].genes == set([self.genes[0]])
        assert self.ontology[11].genes == set([self.genes[0]])
        assert self.ontology[21].genes == set([self.genes[0]])
        assert self.ontology[31].genes == set()
        assert self.ontology[12].genes == set()
        assert self.ontology[41].genes == set()
        assert self.ontology[13].genes == set()

    def test_annotating_hpo_terms_multiple_parents(self):
        add_gene_to_term(self.genes[0], self.ontology[31])
        
        assert self.ontology[1].genes == set([self.genes[0]])
        assert self.ontology[11].genes == set([self.genes[0]])
        assert self.ontology[21].genes == set([self.genes[0]])
        assert self.ontology[31].genes == set([self.genes[0]])
        assert self.ontology[12].genes == set([self.genes[0]])
        assert self.ontology[41].genes == set()
        assert self.ontology[13].genes == set()

    def test_annotating_hpo_terms_mutliple_genes(self):
        add_gene_to_term(self.genes[0], self.ontology[31])
        add_gene_to_term(self.genes[1], self.ontology[41])
        
        assert self.ontology[1].genes == set([self.genes[0], self.genes[1]])
        assert self.ontology[11].genes == set([self.genes[0], self.genes[1]])
        assert self.ontology[21].genes == set([self.genes[0], self.genes[1]])
        assert self.ontology[31].genes == set([self.genes[1], self.genes[0]])
        assert self.ontology[12].genes == set([self.genes[1], self.genes[0]])
        assert self.ontology[41].genes == set([self.genes[1]])
        assert self.ontology[13].genes == set()

    def test_full_annotation(self):
        self.genes[0].hpo.add(31)
        self.genes[1].hpo.add(41)
        _add_genes_to_ontology(self.ontology)

        assert self.ontology[1].genes == set([self.genes[0], self.genes[1]])
        assert self.ontology[11].genes == set([self.genes[0], self.genes[1]])
        assert self.ontology[21].genes == set([self.genes[0], self.genes[1]])
        assert self.ontology[31].genes == set([self.genes[1], self.genes[0]])
        assert self.ontology[12].genes == set([self.genes[1], self.genes[0]])
        assert self.ontology[41].genes == set([self.genes[1]])
        assert self.ontology[13].genes == set()

        assert self.genes[0].hpo == set([31])
        assert self.genes[1].hpo == set([41])


@unittest.skip('TODO')
class PhenoLoading(unittest.TestCase):
    def test_comment_skipping(self):
        pass

    def test_identify_omim(self):
        pass

    def test_identify_negative_omim(self):
        pass


if __name__ == "__main__":
    unittest.main()
