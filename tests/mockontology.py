from pyhpo.term import HPOTerm
from pyhpo.ontology import Ontology
from pyhpo.annotations import Gene, Omim, GeneDict, OmimDict


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


def make_terms():
    root = HPOTerm()
    root.id = 'HP:0001'
    root.name = 'Test root'

    child_1_1 = HPOTerm()
    child_1_1.id = 'HP:0011'
    child_1_1.name = 'Test child level 1-1'
    child_1_1.is_a = root.id

    child_1_2 = HPOTerm()
    child_1_2.id = 'HP:0012'
    child_1_2.name = 'Test child level 1-2'
    child_1_2.is_a = root.id
    child_1_2.synonym = '"another name"'
    child_1_2.synonym = '"third name"'

    child_2_1 = HPOTerm()
    child_2_1.id = 'HP:0021'
    child_2_1.name = 'Test child level 2-1'
    child_2_1.is_a = child_1_1.id

    child_3 = HPOTerm()
    child_3.id = 'HP:0031'
    child_3.name = 'Test child level 3'
    child_3.is_a = child_2_1.id
    child_3.is_a = child_1_2.id

    child_4 = HPOTerm()
    child_4.id = 'HP:0041'
    child_4.name = 'Test child level 4'
    child_4.is_a = child_3.id

    child_1_3 = HPOTerm()
    child_1_3.id = 'HP:0013'
    child_1_3.name = 'Test child level 1-3'
    child_1_3.is_a = root.id

    return (
        root,
        child_1_1,
        child_1_2,
        child_2_1,
        child_3,
        child_4,
        child_1_3
    )


def make_ontology():
    items = make_terms()

    terms = Ontology(filename=None)
    for item in items:
        terms._append(item)

    terms._connect_all()

    return terms


def make_ontology_with_modifiers():
    items = make_terms()

    terms = Ontology(filename=None)
    for item in items:
        terms._append(item)

    moi_root = HPOTerm()
    moi_root.id = 'HP:0000005'
    moi_root.name = 'Mode of inheritance'
    moi_root.is_a = terms[1].id
    terms._append(moi_root)

    cm_root = HPOTerm()
    cm_root.id = 'HP:0012823'
    cm_root.name = 'Clinical modifier'
    cm_root.is_a = terms[1].id
    terms._append(cm_root)

    moi_child1 = HPOTerm()
    moi_child1.id = 'HP:5000001'
    moi_child1.name = 'MOI - C1'
    moi_child1.is_a = moi_root.id
    terms._append(moi_child1)

    moi_child2 = HPOTerm()
    moi_child2.id = 'HP:5000002'
    moi_child2.name = 'MOI - C1'
    moi_child2.is_a = moi_root.id
    terms._append(moi_child2)

    moi_child3 = HPOTerm()
    moi_child3.id = 'HP:5100001'
    moi_child3.name = 'MOI - C1'
    moi_child3.is_a = moi_child1.id
    terms._append(moi_child3)

    terms._connect_all()

    return terms


def make_genes(n):
    # Ensure to remove all items from Gene object
    Gene.clear()
    return [
        Gene([None, None, i, 'Gene{}'.format(i)])
        for i in range(n)
    ]


def make_omim(n):
    Omim.clear()
    return [
        Omim([None, i, 'Omim{}'.format(i)])
        for i in range(n)
    ]
