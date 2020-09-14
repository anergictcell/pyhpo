# PYTHONPATH=./ python tests/benchmarking.py
import cProfile

from pyhpo.ontology import Ontology
from pyhpo.set import HPOSet, BasicHPOSet


def diseases2sets(diseases):
    return [(
        d.name,
        HPOSet.from_queries(d.hpo).child_nodes().remove_modifier()
    ) for d in diseases]


def diseases2basicsets(diseases):
    return [(
        d.name,
        BasicHPOSet.from_queries(d.hpo)
    ) for d in diseases]


def build_ontology():
    _ = Ontology()


def compare_set(diseases):
    for x in list(diseases)[0:100]:
        set1 = HPOSet.from_queries(x.hpo)
        for y in list(diseases)[1:100]:
            set2 = HPOSet.from_queries(y.hpo)
            _ = set1.similarity(set2)
    return None


print('===== LOADING ONTOLOGY ======')
cProfile.run('build_ontology()')

print('===== BUILDING DISEASE SETS ======')
#cProfile.run('diseases2sets(Ontology.omim_diseases)')

print('===== BUILDING DISEASE BasicSETS ======')
#cProfile.run('diseases2basicsets(Ontology.omim_diseases)')

print('===== COMPARING SETS ======')
cProfile.run('compare_set(Ontology.omim_diseases)')
