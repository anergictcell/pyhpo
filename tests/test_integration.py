import sys
import unittest

from pyhpo.ontology import Ontology

# Number of terms in HPO Ontology
N_TERMS = 15332
# Number of genes in the annotation dataset
N_GENES = 4317
# Number of OMIM diseases in the annotation dataset
N_OMIM = 7675
# Number of excluded OMIM diseases in the annotation dataset
N_OMIM_EXL = 638


@unittest.skipUnless(
    'complete-check' in sys.argv,
    'No integration test required'
)
class IntegrationFullTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.terms = Ontology()

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
        assert len(self.terms.omim_diseases) == N_OMIM, len(
            self.terms.omim_diseases
        )

    def test_omim_excluded(self):
        """
        These test will most likely need to be updated
        after every data update
        """
        assert len(self.terms.omim_excluded_diseases) == N_OMIM_EXL, len(
            self.terms.omim_excluded_diseases
        )

    def test_average_annotation_numbers(self):
        """
        These test will most likely need to be updated
        after every data update
        """
        genes = []
        omim = []
        excluded_omim = []
        for term in self.terms:
            genes.append(len(term.genes))
            omim.append(len(term.omim_diseases))
            excluded_omim.append(len(term.omim_excluded_diseases))

        assert sum(genes)/len(genes) > 36, sum(genes)/len(genes)
        assert sum(omim)/len(omim) > 29, sum(omim)/len(omim)
        assert sum(excluded_omim)/len(excluded_omim) > 0.05, \
            sum(excluded_omim)/len(excluded_omim)

    def test_annotation_inheritance(self):
        for term in self.terms:
            lg = len(term.genes)
            lo = len(term.omim_diseases)
            for child in term.children:
                with self.subTest(t=term.id, c=child.id):
                    assert lg >= len(child.genes)
                    assert child.genes.issubset(term.genes)

                    assert lo >= len(child.omim_diseases)
                    assert child.omim_diseases.issubset(term.omim_diseases)

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

    def test_pandas_dataframe(self):
        """
        These test will most likely need to be updated
        after every data update
        """
        df = self.terms.to_dataframe()

        assert df.shape == (N_TERMS, 10), df.shape
        assert 4 < df.ic_omim.mean() < 5, df.ic_omim.mean()
        assert 3.6 < df.ic_gene.mean() < 3.7, df.ic_gene.mean()
        assert 7.5 < df.dTop_l.mean() < 7.6, df.dTop_l.mean()
        assert 6 < df.dTop_s.mean() < 7, df.dTop_s.mean()
        assert 0.61 < df.dBottom.mean() < 0.62, df.dBottom.mean()

    @unittest.skip('This test needs better specification')
    def test_similarity_scores(self):
        i = 0
        for term in self.terms:
            i += 1
            if i > 10:
                continue
            for other in self.terms:
                with self.subTest(t=term.id, c=other.id):
                    assert term.similarity_score(other, method='resnik') >= 0
