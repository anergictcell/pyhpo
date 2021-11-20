import unittest
from unittest.mock import patch, MagicMock

try:
    from pyhpo import stats
except ImportError:
    import sys
    sys.modules['scipy.stats'] = MagicMock()
    sys.modules['scipy.stats'].hypergeom.sf = MagicMock(return_value=0.0000235)  # type: ignore # noqa: E501
    from pyhpo import stats

from pyhpo.stats import HPOEnrichment, EnrichmentModel
from pyhpo.set import HPOSet

from tests.mockontology import make_ontology, make_genes, make_omim


class TestHypergeometricStats(unittest.TestCase):
    def test_hypergeom_test(self):
        self.assertLess(
            stats.hypergeom_test(8, 10, 20, 100),
            0.000024
        )
        self.assertGreater(
            stats.hypergeom_test(8, 10, 20, 100),
            0.000023
        )


class TestHPOEnrichment(unittest.TestCase):
    def setUp(self):
        self.ontology = make_ontology()
        genes = make_genes(4)
        genes[0].hpo.add(self.ontology[1].index)
        genes[0].hpo.add(self.ontology[11].index)
        genes[1].hpo.add(self.ontology[1].index)
        genes[2].hpo.add(self.ontology[11].index)
        genes[3].hpo.add(self.ontology[31].index)
        omim = make_omim(5)
        omim[0].hpo.add(self.ontology[1].index)
        omim[0].hpo.add(self.ontology[11].index)
        omim[1].hpo.add(self.ontology[1].index)
        omim[2].hpo.add(self.ontology[11].index)
        omim[3].hpo.add(self.ontology[31].index)
        omim[4].hpo.add(self.ontology[41].index)
        self.ontology._genes = set(genes)
        self.ontology._omim_diseases = set(omim)

    def test_init(self):
        with patch.object(
            HPOEnrichment,
            '_hpo_count',
            return_value=({}, 15)
        ) as patch_hpo_count:
            _ = HPOEnrichment('gene')
            patch_hpo_count.assert_called_once_with(
                self.ontology.genes
            )
            patch_hpo_count.reset_mock()
            _ = HPOEnrichment('omim')
            patch_hpo_count.assert_called_once_with(
                self.ontology.omim_diseases
            )

    def test_hpo_count(self):
        res = HPOEnrichment._hpo_count(None, self.ontology.genes)
        self.assertEqual(
            res[1],
            5
        )
        self.assertEqual(
            res[0],
            {
                1: 2,
                11: 2,
                31: 1
            }
        )

        res = HPOEnrichment._hpo_count(None, self.ontology.omim_diseases)
        self.assertEqual(
            res[1],
            6
        )
        self.assertEqual(
            res[0],
            {
                1: 2,
                11: 2,
                31: 1,
                41: 1
            }
        )

    def test_single_enrichment(self):
        mocktotal = MagicMock()
        mocktotal.total = 12
        mocktotal.hpos = {'bar': 'foo'}
        with patch.object(stats, 'hypergeom_test', return_value=1212) as mock_hg:
            res = HPOEnrichment._single_enrichment(
                mocktotal,
                'hypergeom',
                'bar',
                11,
                13
            )
            mock_hg.assert_called_once_with(
                11, 13, 'foo', 12
            )
            self.assertEqual(res, 1212)

    def test_single_enrichment_error(self):
        mocktotal = MagicMock()
        mocktotal.hpos = {'bar': 'foo'}
        with self.assertRaises(RuntimeError) as context:
            HPOEnrichment._single_enrichment(
                mocktotal,
                'bar',
                10,
                11,
                12
            )
        self.assertEqual(
            'The HPO term 10 is not present in the reference population',
            str(context.exception)
        )

    def test_single_enrichment_wrong_method(self):
        mocktotal = MagicMock()
        mocktotal.total = 12
        mocktotal.hpos = {'bar': 'foo'}
        with self.assertRaises(NotImplementedError) as err:
            _ = HPOEnrichment._single_enrichment(
                mocktotal,
                'wrongmethod',
                'bar',
                11,
                13
            )
        
        assert str(err.exception) == 'Enrichment method not implemented'

    def test_enrichment(self):
        that = MagicMock()
        that._hpo_count = MagicMock(return_value=[{
            1: 2,
            11: 2,
            31: 1
            }, 66])
        that._single_enrichment = MagicMock(
            side_effect=[22, 11, 33]
        )
        res = HPOEnrichment.enrichment(that, 'foo', 'bar')
        self.assertEqual(
            res,
            [{
                'hpo': self.ontology[11],
                'count': 2,
                'enrichment': 11
            }, {
                'hpo': self.ontology[1],
                'count': 2,
                'enrichment': 22
            }, {
                'hpo': self.ontology[31],
                'count': 1,
                'enrichment': 33
            }]
        )


class TestAnnotationEnrichment(unittest.TestCase):
    def setUp(self):
        self.ontology = make_ontology()
        genes = make_genes(4)
        genes[0].hpo.add(self.ontology[1].index)
        genes[0].hpo.add(self.ontology[11].index)
        genes[1].hpo.add(self.ontology[1].index)
        genes[2].hpo.add(self.ontology[11].index)
        genes[3].hpo.add(self.ontology[31].index)
        omim = make_omim(5)
        omim[0].hpo.add(self.ontology[1].index)
        omim[0].hpo.add(self.ontology[11].index)
        omim[1].hpo.add(self.ontology[1].index)
        omim[2].hpo.add(self.ontology[11].index)
        omim[3].hpo.add(self.ontology[31].index)
        omim[4].hpo.add(self.ontology[41].index)
        self.ontology._genes = set(genes)
        self.ontology._omim_diseases = set(omim)
        self.genes = genes

    def test_init(self):
        with patch.object(
            EnrichmentModel,
            '_population_count',
            return_value=({}, 15)
        ) as patch_count:
            res = EnrichmentModel('gene')
            patch_count.assert_called_once_with(
                HPOSet(self.ontology)
            )
            self.assertEqual(
                res.attribute,
                res.attribute_lookup['gene']
            )

            res = EnrichmentModel('omim')
            self.assertEqual(
                res.attribute,
                res.attribute_lookup['omim']
            )

    def test_population_count(self):
        term1 = MagicMock()
        term1.genes = [1, 2, 3]
        term2 = MagicMock()
        term2.genes = [3, 4]
        that = MagicMock()
        that.attribute = EnrichmentModel.attribute_lookup['gene']
        res = EnrichmentModel._population_count(
            that,
            [term1, term2]
        )
        self.assertEqual(
            res,
            (
                {
                    1: 1,
                    2: 1,
                    3: 2,
                    4: 1
                },
                5
            )
        )

    def test_single_enrichment(self):
        that = MagicMock()
        that.total = 12
        that.base_count = {'bar': 'foo'}
        with patch.object(
            stats,
            'hypergeom_test',
            return_value=1212
        ) as mock_hg:
            res = EnrichmentModel._single_enrichment(
                that,
                'hypergeom',
                'bar',
                11,
                13
            )
            mock_hg.assert_called_once_with(
                11, 13, 'foo', 12
            )
            self.assertEqual(res, 1212)

    def test_single_enrichment_error(self):
        that = MagicMock()
        that.base_count = {'bar': 'foo'}
        with self.assertRaises(RuntimeError) as context:
            EnrichmentModel._single_enrichment(
                that,
                'hypergeom',
                'foo',
                11,
                12
            )
        self.assertEqual(
            'The item foo is not present in the reference population',
            str(context.exception)
        )

    def test_single_enrichment_wrong_method(self):
        that = MagicMock()
        that.total = 12
        that.base_count = {'bar': 'foo'}
        with self.assertRaises(NotImplementedError) as err:
            _ = EnrichmentModel._single_enrichment(
                that,
                'wrongmethod',
                'bar',
                11,
                13
            )
        assert str(err.exception) == 'Enrichment method not implemented'

    def test_enrichment(self):
        that = MagicMock()
        that._population_count = MagicMock(return_value=[{
            self.genes[0]: 2,
            self.genes[1]: 2,
            self.genes[2]: 1
            }, 66])
        that._single_enrichment = MagicMock(
            side_effect=[22, 11, 33]
        )
        res = EnrichmentModel.enrichment(that, 'foo', 'bar')
        self.assertEqual(
            res[0]['enrichment'],
            11
        )
        self.assertEqual(
            res[1]['enrichment'],
            22
        )
        self.assertEqual(
            res[2]['enrichment'],
            33
        )


if __name__ == "__main__":
    unittest.main()
