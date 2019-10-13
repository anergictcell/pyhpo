from pyhpo.term import HPOTerm
from pyhpo.ontology import Ontology


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
