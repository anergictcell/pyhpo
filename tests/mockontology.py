from typing import List, Tuple

import pyhpo
from pyhpo.term import HPOTerm
from pyhpo.ontology import Ontology
from pyhpo.annotations import Gene, Omim, Decipher, Orpha

from pyhpo.parser import diseases as ds
from pyhpo.parser.genes import _add_genes_to_ontology

"""
Generates the following Ontology
- HP:0001
    - HP:0011
        - HP:0021
            - HP:0031(*)
    - HP:0012
        - HP:0031(*)
            - HP:0041
    - HP:0013

"""


def make_terms() -> Tuple[HPOTerm, ...]:
    root = HPOTerm(id="HP:0001", name="Test root")

    child_1_1 = HPOTerm(id="HP:0011", name="Test child level 1-1", is_a=[root.id])

    child_1_2 = HPOTerm(
        id="HP:0012",
        name="Test child level 1-2",
        is_a=[root.id],
        synonym=["another name", "third name"],
    )

    child_2_1 = HPOTerm(id="HP:0021", name="Test child level 2-1", is_a=[child_1_1.id])

    child_3 = HPOTerm(
        id="HP:0031", name="Test child level 3", is_a=[child_2_1.id, child_1_2.id]
    )

    child_4 = HPOTerm(id="HP:0041", name="Test child level 4", is_a=[child_3.id])

    child_1_3 = HPOTerm(id="HP:0013", name="Test child level 1-3", is_a=[root.id])

    return (root, child_1_1, child_1_2, child_2_1, child_3, child_4, child_1_3)


def make_ontology() -> pyhpo.ontology.OntologyClass:
    items = make_terms()

    terms = Ontology(from_obo_file=False)
    for item in items:
        terms._append(item)

    terms._connect_all()

    return terms


def make_ontology_with_modifiers() -> pyhpo.ontology.OntologyClass:
    items = make_terms()

    terms = Ontology(from_obo_file=False)
    for item in items:
        terms._append(item)

    moi_root = HPOTerm(id="HP:0000005", name="Mode of inheritance", is_a=[terms[1].id])
    terms._append(moi_root)

    cm_root = HPOTerm(id="HP:0012823", name="Clinical modifier", is_a=[terms[1].id])
    terms._append(cm_root)

    moi_child1 = HPOTerm(id="HP:5000001", name="MOI - C1", is_a=[moi_root.id])
    terms._append(moi_child1)

    moi_child2 = HPOTerm(id="HP:5000002", name="MOI - C1", is_a=[moi_root.id])
    terms._append(moi_child2)

    moi_child3 = HPOTerm(id="HP:5100001", name="MOI - C1", is_a=[moi_child1.id])
    terms._append(moi_child3)

    terms._connect_all()

    return terms


def make_genes(n) -> List[pyhpo.annotations.GeneSingleton]:
    # Ensure to remove all items from Gene object
    Gene.clear()
    return [Gene(hgncid=i, symbol="Gene{}".format(i)) for i in range(n)]


def make_omim(n) -> List[pyhpo.annotations.DiseaseSingleton]:
    Omim.clear()
    return [Omim(diseaseid=i, name="Omim{}".format(i)) for i in range(n)]


def make_decipher(n) -> List[pyhpo.annotations.DiseaseSingleton]:
    Decipher.clear()
    return [Decipher(diseaseid=i, name="Decipher{}".format(i)) for i in range(n)]


def make_orpha(n) -> List[pyhpo.annotations.DiseaseSingleton]:
    Orpha.clear()
    return [Orpha(diseaseid=i, name="Orpha{}".format(i)) for i in range(n)]


def make_ontology_with_annotation() -> pyhpo.ontology.OntologyClass:
    """
    Generates the following Ontology
    - HP:0001
        - HP:0011
            - HP:0021               <- Gene/Disease 0 / Negative Disease 2
                - HP:0031(*)
        - HP:0012                   <- Gene/Disease 1
            - HP:0031(*)
                - HP:0041
        - HP:0013

    """

    Gene.clear()
    Omim.clear()
    Orpha.clear()
    Decipher.clear()

    items = make_terms()

    terms = Ontology(from_obo_file=False)
    for item in items:
        terms._append(item)

    terms._connect_all()

    genes = make_genes(2)
    genes[0].hpo.add(21)
    genes[1].hpo.add(12)

    omim = make_omim(3)
    omim[0].hpo.add(21)
    omim[1].hpo.add(12)
    omim[2].negative_hpo.add(21)

    decipher = make_decipher(3)
    decipher[0].hpo.add(21)
    decipher[1].hpo.add(12)
    decipher[2].negative_hpo.add(21)

    orpha = make_orpha(3)
    orpha[0].hpo.add(21)
    orpha[1].hpo.add(12)
    orpha[2].negative_hpo.add(21)

    ds._add_omim_to_ontology(terms)
    ds._add_decipher_to_ontology(terms)
    ds._add_orpha_to_ontology(terms)
    _add_genes_to_ontology(terms)

    return terms


def tearDown():
    Gene.clear()
    Omim.clear()
    Orpha.clear()
    Decipher.clear()
