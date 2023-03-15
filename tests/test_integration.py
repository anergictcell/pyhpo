import sys
import unittest

from pyhpo import ontology as ont
from pyhpo.ontology import Ontology
from pyhpo.set import HPOSet
from pyhpo.stats import EnrichmentModel
from pyhpo import annotations as an

# Number of terms in HPO Ontology
# grep "^\[Term\]$" pyhpo/data/hp.obo | wc -l
N_TERMS = 17245

# Number of genes in the annotation dataset
# cut -f4 pyhpo/data/phenotype_to_genes.txt | grep -v "^#" | sort -u | wc -l
N_GENES = 4895

# Number of OMIM diseases in the annotation dataset
# cut -f1,3 pyhpo/data/phenotype.hpoa | grep "^OMIM" | sort -u | cut -f2 | grep -v "NOT" | wc -l  # noqa: E501
N_OMIM = 8297
# Number of excluded OMIM diseases in the annotation dataset
# cut -f1,3 pyhpo/data/phenotype.hpoa | grep "^OMIM" | sort -u | cut -f2 | grep "NOT" | wc -l  # noqa: E501
N_OMIM_EXL = 520

# Number of ORPHA diseases in the annotation dataset
# cut -f1,3 pyhpo/data/phenotype.hpoa | grep "^ORPHA" | sort -u | cut -f2 | grep -v "NOT" | wc -l  # noqa: E501
N_ORPHA = 4262
# Number of excluded ORPHA diseases in the annotation dataset
# cut -f1,3 pyhpo/data/phenotype.hpoa | grep "^ORPHA" | sort -u | cut -f2 | grep "NOT" | wc -l  # noqa: E501
N_ORPHA_EXL = 337

# Number of DECIPHER diseases in the annotation dataset
# cut -f1,3 pyhpo/data/phenotype.hpoa | grep "^DECIPHER" | sort -u | cut -f2 | grep -v "NOT" | wc -l  # noqa: E501
N_DECIPHER = 47
# Number of excluded DECIPHER diseases in the annotation dataset
# cut -f1,3 pyhpo/data/phenotype.hpoa | grep "^DECIPHER" | sort -u | cut -f2 | grep "NOT" | wc -l  # noqa: E501
N_DECIPHER_EXL = 0


@unittest.skipUnless(
    'complete-check' in sys.argv,
    'No integration test required'
)
class IntegrationFullTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.terms = Ontology()
        cls.gene_model = EnrichmentModel('gene')
        cls.omim_model = EnrichmentModel('omim')

    def test_terms_present(self):
        """
        These test will most likely need to be updated
        after every data update
        """
        assert len(self.terms) == N_TERMS, len(self.terms)

    def test_genes_associated(self):
        """
        These test will most likely need to be updated
        after every data update
        """
        assert len(self.terms.genes) == N_GENES, len(self.terms.genes)

    def test_omim_associated(self):
        """
        These test will most likely need to be updated
        after every data update
        """
        self.assertEqual(
            len(self.terms.omim_diseases),
            N_OMIM
        )

    def test_orpha_associated(self):
        """
        These test will most likely need to be updated
        after every data update
        """
        self.assertEqual(
            len(self.terms.orpha_diseases),
            N_ORPHA
        )

    def test_decipher_associated(self):
        """
        These test will most likely need to be updated
        after every data update
        """
        self.assertEqual(
            len(self.terms.decipher_diseases),
            N_DECIPHER
        )

    def test_average_annotation_numbers(self):
        """
        These test will most likely need to be updated
        after every data update
        """
        genes = []
        omim = []
        orpha = []
        decipher = []
        excluded_omim = []
        for term in self.terms:
            genes.append(len(term.genes))
            omim.append(len(term.omim_diseases))
            orpha.append(len(term.orpha_diseases))
            decipher.append(len(term.decipher_diseases))
            excluded_omim.append(len(term.omim_excluded_diseases))

        assert sum(genes)/len(genes) > 36, sum(genes)/len(genes)
        assert sum(omim)/len(omim) > 29, sum(omim)/len(omim)
        assert sum(orpha)/len(orpha) > 24, sum(orpha)/len(orpha)
        assert sum(decipher)/len(decipher) > 0.05, sum(decipher)/len(decipher)
        assert sum(excluded_omim)/len(excluded_omim) > 0.05, \
            sum(excluded_omim)/len(excluded_omim)

    def test_annotation_inheritance(self):
        for term in self.terms:
            lg = len(term.genes)
            lo = len(term.omim_diseases)
            lorpha = len(term.orpha_diseases)
            ld = len(term.decipher_diseases)

            for child in term.children:
                with self.subTest(t=term.id, c=child.id):
                    assert lg >= len(child.genes)
                    assert child.genes.issubset(term.genes)

                    assert lo >= len(child.omim_diseases)
                    assert child.omim_diseases.issubset(term.omim_diseases)

                    assert lorpha >= len(child.orpha_diseases)
                    assert child.orpha_diseases.issubset(term.orpha_diseases)

                    assert ld >= len(child.decipher_diseases)
                    assert child.decipher_diseases.issubset(
                        term.decipher_diseases
                    )

    def test_relationships(self):
        kidney = self.terms.get_hpo_object(123)
        assert kidney.name == 'Nephritis'

        scoliosis = self.terms.get_hpo_object('Scoliosis')
        assert scoliosis.id == 'HP:0002650'

        assert not scoliosis.parent_of(kidney)
        assert not scoliosis.child_of(kidney)

        assert not kidney.parent_of(scoliosis)
        assert not kidney.child_of(scoliosis)

        specific_term = self.terms.get_hpo_object(
            'Thoracic kyphoscoliosis'
        )
        broad_term = self.terms.get_hpo_object(
            'Abnormality of the curvature of the vertebral column'
        )

        assert specific_term.child_of(scoliosis)
        assert specific_term.child_of(broad_term)

        assert broad_term.parent_of(scoliosis)
        assert broad_term.parent_of(specific_term)

    @unittest.skipUnless(
        'pd' in globals() or 'pd' in dir(ont),
        'Pandas library is not installed/loaded'
    )
    def test_pandas_dataframe(self):
        """
        These test will most likely need to be updated
        after every data update
        """
        df = self.terms.to_dataframe()

        assert df.shape == (N_TERMS, 14), df.shape
        assert 4 < df.ic_omim.mean() < 5, df.ic_omim.mean()
        assert 3 < df.ic_orpha.mean() < 4, df.ic_orpha.mean()
        assert 0 < df.ic_decipher.mean() < 1, df.ic_decipher.mean()
        assert 3.5 < df.ic_gene.mean() < 4.0, df.ic_gene.mean()
        assert 7.5 < df.dTop_l.mean() < 8.0, df.dTop_l.mean()
        assert 6 < df.dTop_s.mean() < 7, df.dTop_s.mean()
        assert 0.6 < df.dBottom.mean() < 0.7, df.dBottom.mean()

    def test_set(self):
        full_set = HPOSet.from_queries(
            [int(x) for x in self.terms]
        )

        self.assertEqual(
            len(full_set),
            len(self.terms)
        )

        phenoterms = full_set.remove_modifier()
        self.assertLess(
            len(phenoterms),
            len(full_set)
        )
        self.assertGreater(
            len(phenoterms),
            0
        )

        self.assertIn(
            self.terms[5],
            full_set
        )

        self.assertNotIn(
            self.terms[5],
            phenoterms
        )

    def test_gene_enrichment(self):
        hposet = HPOSet.from_queries('HP:0007401,HP:0010885'.split(','))
        res = self.gene_model.enrichment('hypergeom', hposet)
        self.assertIsInstance(res, list)
        self.assertIn('item', res[0])
        self.assertIn('count', res[0])
        self.assertIn('enrichment', res[0])
        self.assertIsInstance(res[0]['item'], an.GeneSingleton)
        self.assertIsInstance(res[0]['count'], int)
        self.assertIsInstance(res[0]['enrichment'], float)

    def test_omim_enrichment(self):
        hposet = HPOSet.from_queries('HP:0007401,HP:0010885'.split(','))
        res = self.omim_model.enrichment('hypergeom', hposet)
        self.assertIsInstance(res, list)
        self.assertIn('item', res[0])
        self.assertIn('count', res[0])
        self.assertIn('enrichment', res[0])
        self.assertIsInstance(res[0]['item'], an.OmimDisease)
        self.assertIsInstance(res[0]['count'], int)
        self.assertIsInstance(res[0]['enrichment'], float)

    def test_similarity_with_custom_ic(self):
        for term in self.terms:
            term.information_content.set_custom('testing_custom_ic', term.information_content.gene)

        for term in self.terms:
            self.assertEqual(
                term.similarity_score(self.terms[1], kind='gene'),
                term.similarity_score(self.terms[1], kind='testing_custom_ic')
            )
