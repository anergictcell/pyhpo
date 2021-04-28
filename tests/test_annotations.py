import unittest

from pyhpo.annotations import Gene, Omim


class OmimTests(unittest.TestCase):
    def setUp(self):
        Omim.clear()

    def tearDown(self):
        Omim.clear()

    def test_omim_disease_building(self):
        a = Omim(diseaseid=1, name='Gaucher type I')
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
        d1a = Omim(diseaseid=1, name='Gaucher')
        # ID present, will be used
        d1b = Omim(diseaseid=1, name='Fabry')
        # No name present, ID will be used as well
        d1c = Omim(diseaseid=1, name=None)

        # New ID, new Name => New Disease
        d2a = Omim(diseaseid=2, name='Fabry')
        # ID present, Matching by ID
        d2b = Omim(diseaseid=2, name='Gaucher')
        # ID present, Matching by ID
        d2c = Omim(diseaseid=2, name=None)

        # New ID but existing name => New disease
        d3a = Omim(diseaseid=3, name='Gaucher')

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
            subindex_length(Omim),
            (0, 0)
        )
        _ = Omim(diseaseid=1, name='Gaucher')
        self.assertEqual(
            subindex_length(Omim),
            (1, 1)
        )
        _ = Omim(diseaseid=2, name='Fabry')
        self.assertEqual(
            subindex_length(Omim),
            (2, 2)
        )
        Omim.clear()
        self.assertEqual(
            subindex_length(Omim),
            (0, 0)
        )

    def test_hpo_association(self):
        pass

    def test_get_omim(self):
        d1 = Omim(diseaseid=1, name='Gaucher')
        d2 = Omim(diseaseid=2, name='Fabry')

        self.assertEqual(Omim.get(1), d1)
        self.assertEqual(Omim.get(2), d2)
        self.assertEqual(Omim.get('1'), d1)

        self.assertRaises(
            ValueError,
            lambda: Omim.get('Fabry')
        )
        self.assertRaises(
            KeyError,
            lambda: Omim.get(12)
        )


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

    def test_hpo_association(self):
        pass

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


@unittest.skip('TODO')
class GeneLoading(unittest.TestCase):
    def test_load_from_file(self):
        pass


@unittest.skip('TODO')
class PhenoLoading(unittest.TestCase):
    def test_comment_skipping(self):
        pass

    def test_identify_omim(self):
        pass

    def test_identify_negative_omim(self):
        pass
