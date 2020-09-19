try:
    from scipy.stats import hypergeom
except ImportError:
    raise ImportError(
        'The pyhpo.stats module requires that you install scipy.',
        '\n\n#######################################################'
        '\n\n#   ==> Please install scipy via `pip install scipy`  #'
        '\n\n#######################################################\n\n'
    )

from pyhpo.ontology import Ontology
from pyhpo import annotations


def hypergeom_test(positive_samples, samples, positive_total, total):
    return hypergeom.sf(
        positive_samples-1,  # likelyhood of more than X, #see https://blog.alexlenail.me/understanding-and-implementing-the-hypergeometric-test-in-python-a7db688a7458  # noqa: 501
        total,
        positive_total,
        samples
    )


class HPOEnrichment():
    def __init__(self, category):
        category_lookup = {
            'gene': Ontology.genes,
            'omim': Ontology.omim_diseases
        }
        self.hpos, self.total = self.hpo_count(category_lookup[category])

    def hpo_count(self, annotation_sets):
        hpos = {}
        for item in annotation_sets:
            for term in item.hpo:
                if term not in hpos:
                    hpos[term] = 0
                hpos[term] += 1
        return (hpos, sum(hpos.values()))

    def single_enrichment(self, method, hpo_id, positives, samples):
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

    def enrichment(self, method, annotation_sets):
        list_counts, list_total = self.hpo_count(annotation_sets)
        res = [{
            'hpo': Ontology[hpo],
            'count': count,
            'enrichment': self.single_enrichment(
                method,
                hpo,
                count,
                list_total
            )} for hpo, count in list_counts.items()
        ]

        return res


class EnrichmentModel():
    attribute_lookup = {
        'gene': lambda x: x.genes,
        'omim': lambda x: x.omim_diseases,
        'orpha': lambda x: x.orpha_diseases,
        'decipher': lambda x: x.decipher_diseases
    }
    base_lookup = {
        'gene': lambda x: annotations.Gene([None, None, x, None]),
        'omim': lambda x: annotations.Omim([None, x, None]),
        'orpha': lambda x: annotations.Orpha([None, x, None]),
        'decipher': lambda x: annotations.Decipher([None, x, None])
    }

    def __init__(self, category):
        self.attribute = self.attribute_lookup[category]
        self.base = self.base_lookup[category]
        self.base_count, self.total = self.population_count(Ontology)

    def population_count(self, hopset):
        population = {}
        for term in hopset:
            for item in self.attribute(term):
                if item not in population:
                    population[item] = 0
                population[item] += 1
        return population, sum(population.values())

    def single_enrichment(self, method, item_id, positives, samples):
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

    def enrichment(self, method, hposet):
        list_counts, list_total = self.population_count(hposet)
        res = [{
            'item': item,
            'count': count,
            'enrichment': self.single_enrichment(
                method,
                item.id,
                count,
                list_total
            )} for item, count in list_counts.items()
        ]
        return sorted(res, key=lambda x: x['enrichment'])
