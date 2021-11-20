from typing import Callable, Dict, List, Union, Tuple

try:
    from scipy.stats import hypergeom  # type: ignore[import]
except ImportError:
    print(
        'The pyhpo.stats module requires that you install scipy.',
        '\n\n#######################################################'
        '\n\n#   ==> Please install scipy via `pip install scipy`  #'
        '\n\n#######################################################\n\n'
    )
    raise ImportError()

import pyhpo
from pyhpo import Ontology
from pyhpo import HPOSet


def hypergeom_test(
    positive_samples: int,
    samples: int,
    positive_total: int,
    total: int
) -> float:
    """
    Wrapper function to call the scipy hypergeometric stats function

    Parameters
    ----------
        positive_samples: int
            Number of successes in the sample set (correctly drawn marbles)
        samples: int
            Total number of samples (number of drawn marbles)
        positive_total: int
            Number of positives in the reference set
            (number of positive marbles in the bag)
        total: int
            Total size of reference set
            (number of marbles in the bag)

    Returns
    -------
    float
        The hypergeometic enrichment score

    """
    return float(hypergeom.sf(
        positive_samples-1,  # likelyhood of more than X, #see https://blog.alexlenail.me/understanding-and-implementing-the-hypergeometric-test-in-python-a7db688a7458  # noqa: 501
        total,
        positive_total,
        samples
    ))


class HPOEnrichment():
    """
    Calculates the enrichment of HPO Terms in an Annotation set.

    You can use this class for the following example use cases:

    * You have a list of genes and want to see if some HPO terms are
      enriched in that group. (e.g. RNAseq differential gene expression)
    * You have a list of OMIM diseases and want to see if they have
      some underlying HPO symptom.

    Parameters
    ----------
    category: str
        String to declare if enrichment is done for genes or for OMIM diseases

        Options are:

        * **gene**
        * **omim**

    """
    def __init__(self, category: str) -> None:
        category_lookup = {
            'gene': Ontology.genes,
            'omim': Ontology.omim_diseases
        }
        self.hpos, self.total = self._hpo_count(
            category_lookup[category]  # type: ignore[arg-type]
        )

    def enrichment(
        self,
        method: str,
        annotation_sets: List['pyhpo.Annotation']
    ) -> List[dict]:
        """
        Calculates the enrichment of HPO terms in the provided annotation set

        Parameters
        ----------
        method: str
            The statistical test for enrichment

            * **hypergeom** Hypergeometric distribution test

        annotation_sets: list of ``annoation``
            Every ``annotation`` item in the list must have an attribute
            ``hpos``, being a list of HPO-Term indicies

        Returns
        -------
        list of dict
            The enrichment of every HPO term in the ``annotation_sets`` list,
            sorted by descending enrichment. Every dict has the following keys:

            * **hpo**: :class:`.HPOTerm`
            * **count**: Number of appearances in the sets
            * **enrichment**: Enrichment score

        """
        list_counts, list_total = self._hpo_count(annotation_sets)
        res = [{
            'hpo': Ontology[hpo],
            'count': count,
            'enrichment': self._single_enrichment(
                method,
                hpo,
                count,
                list_total
            )} for hpo, count in list_counts.items()
        ]

        return sorted(res, key=lambda x: x['enrichment'])

    def _hpo_count(
        self,
        annotation_sets: List['pyhpo.Annotation']
    ) -> Tuple[dict, int]:
        """
        Counts the number of occurrenes of every HPO term
        in the ``annotation_sets``

        Parameters
        ----------
            annotation_set: list of ``annoation``
                Every ``annotation`` item in the list must have an attribute
                ``hpos``, returning an iterable of :class:`.HPOTerm`

        Returns
        -------
        tuple with following items:
            * Dict with
                * key: :class:`.HPOTerm`
                * value: int <Number of occurences>
            * Total number of HPO terms in set
        """
        hpos = {}
        for item in annotation_sets:
            for term in item.hpo:
                if term not in hpos:
                    hpos[term] = 0
                hpos[term] += 1
        return (hpos, sum(hpos.values()))

    def _single_enrichment(
        self,
        method: str,
        hpo_id: Union[int, 'pyhpo.HPOTerm'],
        positives: int,
        samples: int
    ) -> float:
        """
        Calculates the enrichment of a single HPO term compared to
        the reference set

        Parameters
        ----------
            method: str
                The statistical test for enrichment

                * **hypergeom** Hypergeometric distribution test

            hpo_id: int or :class:`.HPOTerm`
                ID of the HPO Term
            positives: int
                Number of successes in the sample set (correctly drawn marbles)
            samples: int
                Total number of samples (number of drawn marbles)

        Returns
        -------
        float
            The enrichment score
        """
        try:
            positive_total = self.hpos[hpo_id]
        except KeyError:
            raise RuntimeError(
                'The HPO term {} is not present in the '
                'reference population'.format(hpo_id)
            )
        if method == 'hypergeom':
            return hypergeom_test(
                positives,
                samples,
                positive_total,
                self.total
            )
        else:
            raise NotImplementedError('Enrichment method not implemented')


class EnrichmentModel():
    """
    Calculates the enrichment of annotations in an :class:`.HPOSet`.

    You can use this class for the following example use cases:

    * You have a set of HPOTerms and want to find the
      most likely causative gene
    * You have a set of HPOTerms and want to find the underlying disease

    Parameters
    ----------
    category: str
        String to declare if enrichment is done for genes or for OMIM diseases

        Options are:

        * **gene**
        * **omim**
        * **orpha**
        * **decipher**

    """
    attribute_lookup: Dict[str, Callable] = {
        'gene': lambda x: x.genes,
        'omim': lambda x: x.omim_diseases,
        'orpha': lambda x: x.orpha_diseases,
        'decipher': lambda x: x.decipher_diseases
    }

    def __init__(self, category: str) -> None:
        self.attribute = self.attribute_lookup[category]
        self.base_count, self.total = self._population_count(HPOSet(Ontology))

    def enrichment(
        self,
        method: str,
        hposet: HPOSet
    ) -> List[dict]:
        """
        Calculates the enrichment of annotations in the provided HPOSet

        Parameters
        ----------
        method: str
            The statistical test for enrichment

            * **hypergeom** Hypergeometric distribution test

        hposet: :class:`.HPOSet`

        Returns
        -------
        list of dict
            The enrichment of every annotation item sorted by
            descending enrichment. Every dict has the following keys:

            * **item**: Gene or OMIM or Decipher annotation item
            * **count**: Number of appearances in the sets
            * **enrichment**: Enrichment score

        """
        list_counts, list_total = self._population_count(hposet)
        res = [{
            'item': item,
            'count': count,
            'enrichment': self._single_enrichment(
                method,
                item,
                count,
                list_total
            )} for item, count in list_counts.items()
        ]
        return sorted(res, key=lambda x: x['enrichment'])

    def _population_count(self, hopset: HPOSet) -> Tuple[dict, int]:
        """
        Counts the number of occurrenes of every annotation item
        in the HPOSet

        Parameters
        ----------
            hposet: :class:`.HPOSet`

        Returns
        -------
        tuple with following items:
            * Dict with
                * key: Annotation Item
                * value: int <Number of occurences>
            * Total number of annotations in set
        """
        population = {}
        for term in hopset:
            for item in self.attribute(term):
                if item not in population:
                    population[item] = 0
                population[item] += 1
        return population, sum(population.values())

    def _single_enrichment(
        self,
        method: str,
        item_id: int,
        positives: int,
        samples: int
    ) -> float:
        """
        Calculates the enrichment of annotations in an HPO set

        Parameters
        ----------
            method: str
                The statistical test for enrichment

                * **hypergeom** Hypergeometric distribution test

            item_id: int
                ID of the Annotation
            positives: int
                Number of successes in the sample set (correctly drawn marbles)
            samples: int
                Total number of samples (number of drawn marbles)

        Returns
        -------
        float
            The enrichment score
        """
        try:
            positive_total = self.base_count[item_id]
        except KeyError:
            raise RuntimeError(
                'The item {} is not present in the '
                'reference population'.format(item_id)
            )
        if method == 'hypergeom':
            return hypergeom_test(
                positives,
                samples,
                positive_total,
                self.total
            )
        else:
            raise NotImplementedError('Enrichment method not implemented')
