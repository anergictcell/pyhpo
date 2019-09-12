import unittest
from pyhpo.ontology import Ontology
from pyhpo.term import HPOTerm


class MockOntology:
    def __init__(self, id):
        self._index = int(id)


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


class OntologyInitTests(unittest.TestCase):
    def test_sizes(self):
        a = Ontology(filename=None)
        assert len(a) == 0
        a._append(MockOntology(1))
        assert len(a) == 1
        a._append(MockOntology(5))
        assert len(a) == 2
        a._append(MockOntology(3))
        assert len(a) == 3

    def test_index(self):
        a = Ontology(filename=None)
        a._append(MockOntology(3))
        assert a[3]._index == 3
        assert a[0] is None
        assert a[2] is None
        assert a[4] is None


class BasicOntologyFeatures(unittest.TestCase):
    def setUp(self):
        items = make_terms()
        self.root = items[0]
        self.child_1_1 = items[1]
        self.child_1_2 = items[2]
        self.child_2_1 = items[3]
        self.child_3 = items[4]

        self.terms = Ontology(filename=None)
        self.terms._append(self.root)
        self.terms._append(self.child_1_1)
        self.terms._append(self.child_1_2)
        self.terms._append(self.child_2_1)
        self.terms._append(self.child_3)

    def test_parents(self):
        self.terms._connect_all()

        assert len(self.child_3.parents) == 2
        assert self.child_3.parents[0] == self.child_2_1
        assert self.child_3.parents[1] == self.child_1_2

        assert len(self.child_2_1.parents) == 1
        assert self.child_2_1.parents[0] == self.child_1_1
        assert self.child_2_1.parents[0].parents[0] == self.root

        assert len(self.child_1_1.parents) == 1
        assert self.child_1_1.parents[0] == self.root

        assert len(self.child_1_2.parents) == 1
        assert self.child_1_2.parents[0] == self.root

        assert self.root.parents == []

    def test_children(self):
        self.terms._connect_all()
        assert len(self.root.children) == 2
        assert self.root.children[0] == self.child_1_1
        assert self.root.children[1] == self.child_1_2

        assert self.child_1_1.children == [self.child_2_1]

        assert self.child_1_2.children == [self.child_3]

        assert self.child_2_1.children == [self.child_3]

        assert self.child_3.children == []


class OntologyTreeTraversal(unittest.TestCase):
    def setUp(self):
        items = make_terms()
        self.root = items[0]
        self.child_1_1 = items[1]
        self.child_1_2 = items[2]
        self.child_2_1 = items[3]
        self.child_3 = items[4]
        self.child_4 = items[5]
        self.child_1_3 = items[6]

        self.terms = Ontology(filename=None)
        self.terms._append(self.root)
        self.terms._append(self.child_1_1)
        self.terms._append(self.child_1_2)
        self.terms._append(self.child_2_1)
        self.terms._append(self.child_3)
        self.terms._append(self.child_4)
        self.terms._append(self.child_1_3)

    def test_hierarchy(self):
        self.terms._connect_all()

        assert self.root.hierarchy() == (
            (self.root,),
        )

        assert self.child_1_1.hierarchy() == (
            (self.child_1_1, self.root),
        )

        assert self.child_1_2.hierarchy() == (
            (self.child_1_2, self.root),
        )

        assert self.child_2_1.hierarchy() == (
            (self.child_2_1, self.child_1_1, self.root),
        )

        assert self.child_3.hierarchy() == (
            (self.child_3, self.child_2_1, self.child_1_1, self.root),
            (self.child_3, self.child_1_2, self.root)
        )

        assert self.child_4.hierarchy() == (
            (self.child_4, self.child_3, self.child_2_1, self.child_1_1, self.root),
            (self.child_4, self.child_3, self.child_1_2, self.root)
        )

    def test_path_to_root_finding(self):
        self.terms._connect_all()

        assert self.root.longest_path_to_root() == 0
        assert self.root.shortest_path_to_root() == 0

        assert self.child_1_1.longest_path_to_root() == 1
        assert self.child_1_1.shortest_path_to_root() == 1

        assert self.child_1_2.longest_path_to_root() == 1
        assert self.child_1_2.shortest_path_to_root() == 1

        assert self.child_2_1.longest_path_to_root() == 2
        assert self.child_2_1.shortest_path_to_root() == 2

        assert self.child_3.longest_path_to_root() == 3
        assert self.child_3.shortest_path_to_root() == 2

        assert self.child_4.longest_path_to_root() == 4
        assert self.child_4.shortest_path_to_root() == 3

        assert self.child_1_3.longest_path_to_root() == 1
        assert self.child_1_3.shortest_path_to_root() == 1

    def test_path_to_bottom_finding(self):
        self.terms._connect_all()
        assert self.root.longest_path_to_bottom() == 4
        assert self.child_1_1.longest_path_to_bottom() == 3
        assert self.child_1_2.longest_path_to_bottom() == 2
        assert self.child_2_1.longest_path_to_bottom() == 2
        assert self.child_3.longest_path_to_bottom() == 1
        assert self.child_4.longest_path_to_bottom() == 0
        assert self.child_1_3.longest_path_to_bottom() == 0

    def test_path_to_parent(self):
        self.terms._connect_all()
        assert self.child_1_1.shortest_path_to_parent(self.root) == (
            1,
            (self.child_1_1, self.root)
        )

        assert self.child_1_2.shortest_path_to_parent(self.root) == (
            1,
            (self.child_1_2, self.root)
        )

        assert self.child_2_1.shortest_path_to_parent(self.root) == (
            2,
            (self.child_2_1, self.child_1_1, self.root)
        )

        assert self.child_3.shortest_path_to_parent(self.root) == (
            2,
            (self.child_3, self.child_1_2, self.root)
        )

        assert self.child_4.shortest_path_to_parent(self.root) == (
            3,
            (self.child_4, self.child_3, self.child_1_2, self.root)
        )

        assert self.child_4.shortest_path_to_parent(self.child_3) == (
            1,
            (self.child_4, self.child_3)
        )

        assert self.child_4.shortest_path_to_parent(self.child_2_1) == (
            2,
            (self.child_4, self.child_3, self.child_2_1)
        )

        assert self.child_4.shortest_path_to_parent(self.child_1_1) == (
            3,
            (self.child_4, self.child_3, self.child_2_1, self.child_1_1)
        )

        assert self.child_4.shortest_path_to_parent(self.child_1_2) == (
            2,
            (self.child_4, self.child_3, self.child_1_2)
        )

        assert self.child_4.shortest_path_to_parent(self.child_1_3) == (
            float('inf'),
            None
        )

        assert self.child_1_2.shortest_path_to_parent(self.child_4) == (
            float('inf'),
            None
        )

    def test_path_to_other(self):
        # path_to_other
        pass

    def test_child_parent_checking(self):
        # is_parent
        # is_child_of
        pass

    def test_parent_listing(self):
        # count_parents
        # parent_ids
        pass

    def test_builtins(self):
        # >
        # ==
        # str()
        # repr()
        pass
