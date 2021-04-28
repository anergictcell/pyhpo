import unittest
from unittest.mock import patch, MagicMock

import pyhpo
from pyhpo.ontology import Ontology
from tests.mockontology import make_terms


class MockPrint:
    def __init__(self):
        self.counter = 0
        self.strings = []

    def __call__(self, string):
        self.counter += 1
        self.strings.append(string)


class MockOntology:
    def __init__(self, id):
        self.index = int(id)


class TestOntologyInit(unittest.TestCase):
    def test_sizes(self):
        a = Ontology(from_obo_file=False)
        assert len(a) == 0
        a._append(MockOntology(1))
        assert len(a) == 1
        a._append(MockOntology(5))
        assert len(a) == 2
        a._append(MockOntology(3))
        assert len(a) == 3

    def test_index(self):
        a = Ontology(from_obo_file=False)
        a._append(MockOntology(3))
        assert a[3].index == 3
        with self.assertRaises(KeyError) as err:
            a[0]
            self.assertEqual(
                'No HPOTerm for index 0',
                str(err.exception)
            )
        with self.assertRaises(KeyError) as err:
            a[2]
            self.assertEqual(
                'No HPOTerm for index 2',
                str(err.exception)
            )

        with self.assertRaises(KeyError) as err:
            a[4]
            self.assertEqual(
                'No HPOTerm for index 4',
                str(err.exception)
            )


class TestBasicOntologyFeatures(unittest.TestCase):
    def setUp(self):
        items = make_terms()
        self.root = items[0]
        self.child_1_1 = items[1]
        self.child_1_2 = items[2]
        self.child_2_1 = items[3]
        self.child_3 = items[4]

        self.terms = Ontology(from_obo_file=False)
        self.terms._append(self.root)
        self.terms._append(self.child_1_1)
        self.terms._append(self.child_1_2)
        self.terms._append(self.child_2_1)
        self.terms._append(self.child_3)

        self.terms._connect_all()

    def test_parents(self):
        assert len(self.child_3.parents) == 2
        self.assertIn(
            self.child_2_1,
            self.child_3.parents
        )
        self.assertIn(
            self.child_1_2,
            self.child_3.parents
        )

        assert len(self.child_2_1.parents) == 1
        self.assertEqual(
            self.child_2_1.parents,
            set([self.child_1_1])
        )

        for p in self.child_2_1.parents:
            self.assertIn(
                self.root,
                p.parents
            )

        assert len(self.child_1_1.parents) == 1
        self.assertIn(
            self.root,
            self.child_1_1.parents
        )

        assert len(self.child_1_2.parents) == 1
        self.assertIn(
            self.root,
            self.child_1_2.parents
        )

        self.assertEqual(
            self.root.parents,
            set()
        )

    def test_children(self):
        assert len(self.root.children) == 2
        self.assertEqual(
            set([self.child_1_1, self.child_1_2]),
            self.root.children
        )

        assert self.child_1_1.children == set([self.child_2_1])

        assert self.child_1_2.children == set([self.child_3])

        assert self.child_2_1.children == set([self.child_3])

        assert self.child_3.children == set()


class TestOntologyTreeTraversal(unittest.TestCase):
    def setUp(self):
        items = make_terms()
        self.root = items[0]
        self.child_1_1 = items[1]
        self.child_1_2 = items[2]
        self.child_2_1 = items[3]
        self.child_3 = items[4]
        self.child_4 = items[5]
        self.child_1_3 = items[6]

        self.terms = Ontology(from_obo_file=False)
        self.terms._append(self.root)
        self.terms._append(self.child_1_1)
        self.terms._append(self.child_1_2)
        self.terms._append(self.child_2_1)
        self.terms._append(self.child_3)
        self.terms._append(self.child_4)
        self.terms._append(self.child_1_3)

        self.terms._connect_all()

    def test_hierarchy(self):

        self.assertEqual(
            self.root.hierarchy,
            ((self.root,),)
        )

        self.assertEqual(
            self.child_1_1.hierarchy,
            ((self.child_1_1, self.root),)
        )

        self.assertEqual(
            self.child_1_2.hierarchy,
            ((self.child_1_2, self.root),)
        )

        self.assertEqual(
            self.child_2_1.hierarchy,
            ((self.child_2_1, self.child_1_1, self.root),)
        )

        self.assertEqual(len(self.child_3.hierarchy), 2)
        self.assertIn(
            (self.child_3, self.child_2_1, self.child_1_1, self.root),
            self.child_3.hierarchy
        )
        self.assertIn(
            (self.child_3, self.child_1_2, self.root),
            self.child_3.hierarchy,
        )

        self.assertEqual(len(self.child_4.hierarchy), 2)
        self.assertIn(
            (
                self.child_4,
                self.child_3,
                self.child_2_1,
                self.child_1_1,
                self.root
            ),
            self.child_4.hierarchy
        )
        self.assertIn(
            (self.child_4, self.child_3, self.child_1_2, self.root),
            self.child_4.hierarchy
        )

    def test_path_to_root_finding(self):

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
        assert self.root.longest_path_to_bottom() == 4
        assert self.child_1_1.longest_path_to_bottom() == 3
        assert self.child_1_2.longest_path_to_bottom() == 2
        assert self.child_2_1.longest_path_to_bottom() == 2
        assert self.child_3.longest_path_to_bottom() == 1
        assert self.child_4.longest_path_to_bottom() == 0
        assert self.child_1_3.longest_path_to_bottom() == 0

    def test_path_to_parent(self):
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

        with self.assertRaises(RuntimeError) as err:
            _ = self.child_4.shortest_path_to_parent(self.child_1_3)
        self.assertEqual(
            str(err.exception),
            'HP:0013 is not a parent of HP:0041'
        )

        with self.assertRaises(RuntimeError) as err:
            _ = self.child_1_2.shortest_path_to_parent(self.child_4)
        self.assertEqual(
            str(err.exception),
            'HP:0041 is not a parent of HP:0012'
        )

    def test_path_to_other(self):

        path = self.child_1_1.path_to_other(self.root)
        assert path == (
            1,
            (self.child_1_1, self.root),
            1,
            0
        )

        path = self.root.path_to_other(self.child_1_1)
        assert path == (
            1,
            (self.root, self.child_1_1),
            0,
            1
        )

        path = self.child_1_1.path_to_other(self.child_1_2)
        assert path == (
            2,
            (self.child_1_1, self.root, self.child_1_2),
            1,
            1
        )

        path = self.child_1_1.path_to_other(self.child_1_3)
        assert path == (
            2,
            (self.child_1_1, self.root, self.child_1_3),
            1,
            1
        )

        path = self.child_2_1.path_to_other(self.child_1_3)
        assert path == (
            3,
            (self.child_2_1, self.child_1_1, self.root, self.child_1_3),
            2,
            1
        )

        path = self.child_4.path_to_other(self.child_1_3)
        assert path == (
            4,
            (
                self.child_4,
                self.child_3,
                self.child_1_2,
                self.root,
                self.child_1_3
            ),
            3,
            1
        )

        path = self.child_1_3.path_to_other(self.child_4)
        assert path == (
            4,
            (
                self.child_1_3,
                self.root,
                self.child_1_2,
                self.child_3,
                self.child_4
            ),
            1,
            3
        )

    def test_child_parent_checking(self):

        assert self.root.parent_of(self.child_1_1)
        assert self.root.parent_of(self.child_1_2)
        assert self.root.parent_of(self.child_2_1)
        assert self.root.parent_of(self.child_3)
        assert self.root.parent_of(self.child_4)
        assert self.root.parent_of(self.child_1_3)

        assert not self.root.child_of(self.child_1_1)
        assert not self.root.child_of(self.child_1_2)
        assert not self.root.child_of(self.child_2_1)
        assert not self.root.child_of(self.child_3)
        assert not self.root.child_of(self.child_4)
        assert not self.root.child_of(self.child_1_3)

        assert not self.child_1_1.parent_of(self.root)
        assert not self.child_1_1.parent_of(self.child_1_2)
        assert self.child_1_1.parent_of(self.child_2_1)
        assert self.child_1_1.parent_of(self.child_3)
        assert self.child_1_1.parent_of(self.child_4)
        assert not self.child_1_1.parent_of(self.child_1_3)

        assert self.child_1_1.child_of(self.root)
        assert not self.child_1_1.child_of(self.child_1_2)
        assert not self.child_1_1.child_of(self.child_2_1)
        assert not self.child_1_1.child_of(self.child_3)
        assert not self.child_1_1.child_of(self.child_4)
        assert not self.child_1_1.child_of(self.child_1_3)

        assert not self.child_1_2.parent_of(self.root)
        assert not self.child_1_2.parent_of(self.child_1_1)
        assert not self.child_1_2.parent_of(self.child_2_1)
        assert self.child_1_2.parent_of(self.child_3)
        assert self.child_1_2.parent_of(self.child_4)
        assert not self.child_1_2.parent_of(self.child_1_3)

        assert self.child_1_2.child_of(self.root)
        assert not self.child_1_2.child_of(self.child_1_1)
        assert not self.child_1_2.child_of(self.child_2_1)
        assert not self.child_1_2.child_of(self.child_3)
        assert not self.child_1_2.child_of(self.child_4)
        assert not self.child_1_2.child_of(self.child_1_3)

        assert not self.child_2_1.parent_of(self.root)
        assert not self.child_2_1.parent_of(self.child_1_1)
        assert not self.child_2_1.parent_of(self.child_1_2)
        assert self.child_2_1.parent_of(self.child_3)
        assert self.child_2_1.parent_of(self.child_4)
        assert not self.child_2_1.parent_of(self.child_1_3)

        assert self.child_2_1.child_of(self.root)
        assert self.child_2_1.child_of(self.child_1_1)
        assert not self.child_2_1.child_of(self.child_1_2)
        assert not self.child_2_1.child_of(self.child_3)
        assert not self.child_2_1.child_of(self.child_4)
        assert not self.child_2_1.child_of(self.child_1_3)

        assert not self.child_3.parent_of(self.root)
        assert not self.child_3.parent_of(self.child_1_1)
        assert not self.child_3.parent_of(self.child_1_2)
        assert not self.child_3.parent_of(self.child_2_1)
        assert self.child_3.parent_of(self.child_4)
        assert not self.child_3.parent_of(self.child_1_3)

        assert self.child_3.child_of(self.root)
        assert self.child_3.child_of(self.child_1_1)
        assert self.child_3.child_of(self.child_1_2)
        assert self.child_3.child_of(self.child_2_1)
        assert not self.child_3.child_of(self.child_4)
        assert not self.child_3.child_of(self.child_1_3)

        err_msg = 'An HPO term cannot be parent/child of itself'
        with self.assertRaises(RuntimeError) as err:
            self.child_3.child_of(self.child_3)
        assert str(err.exception) == err_msg

        with self.assertRaises(RuntimeError) as err:
            self.child_3.parent_of(self.child_3)
        assert str(err.exception) == err_msg

        with self.assertRaises(RuntimeError) as err:
            self.root.child_of(self.root)
        assert str(err.exception) == err_msg

        with self.assertRaises(RuntimeError) as err:
            self.root.parent_of(self.root)
        assert str(err.exception) == err_msg

    def test_parent_listing(self):

        assert self.root.count_parents() == 0
        assert self.child_1_1.count_parents() == 1
        assert self.child_1_2.count_parents() == 1
        assert self.child_2_1.count_parents() == 2
        assert self.child_3.count_parents() == 5
        assert self.child_4.count_parents() == 6
        assert self.child_1_3.count_parents() == 1

        assert self.root.parent_ids() == []
        assert self.child_1_1.parent_ids() == [1]
        assert self.child_1_2.parent_ids() == [1]
        assert self.child_2_1.parent_ids() == [11]
        assert self.child_3.parent_ids() == [21, 12]
        assert self.child_4.parent_ids() == [31]
        assert self.child_1_3.parent_ids() == [1]

    def test_builtins(self):
        assert int(self.root) == 1
        assert int(self.child_1_3) == 13

        assert self.child_1_3 > self.root
        assert self.child_3 > self.root
        assert self.child_3 > self.child_2_1

        assert not self.child_1_3 == self.root
        assert not self.child_3 == self.root
        assert not self.child_3 == self.child_2_1

        assert self.child_1_3 != self.root
        assert self.child_3 != self.root
        assert self.child_3 != self.child_2_1

        assert self.root == self.root
        assert self.child_1_3 == self.child_1_3
        assert self.child_3 == self.child_3

        assert str(self.root) == 'HP:0001 | Test root'
        self.assertEqual(
            repr(self.root),
            "HPOTerm(id='HP:0001', name='Test root', is_a=[])"
        )

    @unittest.skip('Deprecating print_hierarchy')
    def test_hierarchy_printing(self):
        pyhpo.term.print = MockPrint()

        self.child_3.print_hierarchy()
        assert pyhpo.term.print.counter == 6
        assert pyhpo.term.print.strings[0] == '-Test child level 3'
        assert pyhpo.term.print.strings[1].endswith('-Test child level 2-1')
        assert pyhpo.term.print.strings[2].endswith('-Test child level 1-1')
        assert pyhpo.term.print.strings[3].endswith('-Test root')
        assert pyhpo.term.print.strings[4].endswith('-Test child level 1-2')
        assert pyhpo.term.print.strings[5].endswith('-Test root')
        pyhpo.term.print = print


class TestOntologyQueries(unittest.TestCase):
    def setUp(self):
        items = make_terms()
        self.root = items[0]
        self.child_1_1 = items[1]
        self.child_1_2 = items[2]
        self.child_2_1 = items[3]
        self.child_3 = items[4]
        self.child_4 = items[5]
        self.child_1_3 = items[6]

        self.terms = Ontology(from_obo_file=False)
        self.terms._append(self.root)
        self.terms._append(self.child_1_1)
        self.terms._append(self.child_1_2)
        self.terms._append(self.child_2_1)
        self.terms._append(self.child_3)
        self.terms._append(self.child_4)
        self.terms._append(self.child_1_3)
        self.terms._connect_all()

    def test_get_hpo_object(self):
        self.assertEqual(
            self.terms.get_hpo_object('Test child level 1-2'),
            self.child_1_2
        )
        self.assertEqual(
            self.terms.get_hpo_object('HP:00012'),
            self.child_1_2
        )
        self.assertEqual(
            self.terms.get_hpo_object(12),
            self.child_1_2
        )
        with self.assertRaises(RuntimeError) as err:
            self.terms.get_hpo_object([1, 2, 3])
        assert 'Invalid type' in str(err.exception)

        with self.assertRaises(RuntimeError) as err:
            self.terms.get_hpo_object('Some invalid term')
        assert 'No HPO entry with term' in str(err.exception)

    def test_matching(self):
        self.assertEqual(
            self.terms.match(self.root.name),
            self.root
        )
        self.assertEqual(
            self.terms.match(self.child_1_1.name),
            self.child_1_1
        )
        self.assertEqual(
            self.terms.match(self.child_1_2.name),
            self.child_1_2
        )
        self.assertEqual(
            self.terms.match(self.child_1_3.name),
            self.child_1_3
        )
        self.assertEqual(
            self.terms.match(self.child_1_2.name),
            self.child_1_2
        )
        self.assertEqual(
            self.terms.match(self.child_3.name),
            self.child_3
        )
        self.assertEqual(
            self.terms.match(self.child_4.name),
            self.child_4
        )

        with self.assertRaises(RuntimeError) as err:
            self.terms.match('Some invalid term')
        assert 'No HPO entry with name' in str(err.exception)

    @patch('pyhpo.Ontology.get_hpo_object')
    def test_path_unit(self, mock_gho):
        mock_term = MagicMock()
        mock_gho.return_value = mock_term
        self.terms.path('first query', 'second query')

        mock_gho.assert_any_call('first query')
        mock_gho.assert_any_call('second query')
        assert mock_gho.call_count == 2

        mock_term.path_to_other.assert_called_once_with(mock_term)

    def test_path_integration(self):
        path = self.terms.path('Test child level 1-1', 'Test root')
        self.assertEqual(
            path,
            (
                1,
                (self.child_1_1, self.root),
                1,
                0
            )
        )

        path = self.terms.path('Test root', 'Test child level 1-1')
        self.assertEqual(
            path,
            (
                1,
                (self.root, self.child_1_1),
                0,
                1
            )
        )

        path = self.terms.path('Test child level 1-1', 'Test child level 1-2')
        self.assertEqual(
            path,
            (
                2,
                (self.child_1_1, self.root, self.child_1_2),
                1,
                1
            )
        )

    @patch('pyhpo.Ontology.synonym_search')
    def test_search(self, mock_syn_search):
        mock_syn_search.return_value = False

        self.assertEqual(
            list(self.terms.search('something')),
            []
        )
        # All terms will be searched for in synonyms
        self.assertEqual(
            mock_syn_search.call_count,
            7
        )
        mock_syn_search.reset_mock()

        self.assertEqual(
            list(self.terms.search('Test root')),
            [self.root]
        )
        # Root term will not be searched for in synonyms
        self.assertEqual(
            mock_syn_search.call_count,
            6
        )
        mock_syn_search.reset_mock()

        self.assertEqual(
            list(self.terms.search('Test child level 1-1')),
            [self.child_1_1]
        )
        # Matched term will not be searched for in synonyms
        self.assertEqual(
            mock_syn_search.call_count,
            6
        )

    def test_synonym_search(self):
        assert self.terms.synonym_search(self.child_1_2, 'not')
        assert self.terms.synonym_search(self.child_1_2, 'ther na')
        assert self.terms.synonym_search(self.child_1_2, 'another name')
        assert self.terms.synonym_search(self.child_1_2, 'name')
        assert self.terms.synonym_search(self.child_1_2, 'third name')
        assert not self.terms.synonym_search(self.child_1_2, 'xyz')

        assert not self.terms.synonym_search(self.child_1_3, 'not')
        assert not self.terms.synonym_search(self.child_1_3, 'ther na')
        assert not self.terms.synonym_search(self.child_1_3, 'another name')
        assert not self.terms.synonym_search(self.child_1_3, 'name')
        assert not self.terms.synonym_search(self.child_1_3, 'third name')
        assert not self.terms.synonym_search(self.child_1_3, 'xyz')

    def test_synonym_match(self):
        self.child_1_1.synonym.append('Test child level 1-2')

        self.assertEqual(
            self.terms.synonym_match('Test child level 1-2'),
            self.child_1_2
        )
        self.assertEqual(
            self.terms.synonym_match('another name'),
            self.child_1_2
        )
        self.assertEqual(
            self.terms.synonym_match('third name'),
            self.child_1_2
        )

        self.child_1_2.Config.allow_mutation = True
        self.child_1_2.name = 'something else'
        self.assertEqual(
            self.terms.synonym_match('Test child level 1-2'),
            self.child_1_1
        )

    @unittest.skip('TODO')
    def test_common_ancestors(self):
        pass

    @unittest.skip('TODO')
    def test_annotations(self):
        pass

    @unittest.skip('TODO')
    def test_loading_from_file(self):
        pass


if __name__ == "__main__":
    unittest.main()
