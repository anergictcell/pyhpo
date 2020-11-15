import unittest
from unittest.mock import patch, call
import warnings

from pyhpo.set import HPOSet, BasicHPOSet
from pyhpo.term import HPOTerm
from pyhpo.matrix import Matrix
from tests.mockontology import make_terms, make_ontology, make_ontology_with_modifiers


class SetMethods(unittest.TestCase):
    def test_combinations(self):
        ci = HPOSet(['term1', 'term2', 'term3'])
        res = list(ci.combinations())
        assert res == [
            ('term1', 'term2'),
            ('term1', 'term3'),
            ('term2', 'term1'),
            ('term2', 'term3'),
            ('term3', 'term1'),
            ('term3', 'term2')
        ], res

    def test_combinations_one_way(self):
        ci = HPOSet(['term1', 'term2', 'term3'])
        res = list(ci.combinations_one_way())
        assert res == [
            ('term1', 'term2'),
            ('term1', 'term3'),
            ('term2', 'term3')
        ], res


class SetInitTests(unittest.TestCase):
    def setUp(self):
        self.ontology = make_ontology()
        self.ci = HPOSet([
            term for term in self.ontology
        ])

    def test_initialization(self):
        assert len(self.ci) == len(self.ontology)

    def test_set_from_queries(self):
        a = HPOSet.from_queries([
            'Test child level 1-1',
            'Test child level 2-1',
            'Test child level 4'
        ])
        assert len(a) == 3

    def test_child_nodes(self):
        child_nodes = self.ci.child_nodes()

        assert len(child_nodes) == 2, len(child_nodes)

        assert self.ontology[1] not in child_nodes
        assert self.ontology[11] not in child_nodes
        assert self.ontology[12] not in child_nodes
        assert self.ontology[13] in child_nodes
        assert self.ontology[21] not in child_nodes
        assert self.ontology[31] not in child_nodes
        assert self.ontology[41] in child_nodes

    def test_toJSON(self):
        res = self.ci.toJSON()

        self.assertEqual(
            len(res),
            7
        )
        self.assertEqual(
            res[0],
            self.ontology[1].toJSON()
        )

        res_verbose = self.ci.toJSON(verbose=True)

        self.assertEqual(
            len(res_verbose),
            7
        )
        self.assertEqual(
            res_verbose[0],
            self.ontology[1].toJSON(verbose=True)
        )

    def test_serialization(self):
        a = HPOSet.from_queries([
            'Test child level 1-1',
            'Test child level 2-1',
            'Test child level 4'
        ])
        self.assertEqual(
            a.serialize(),
            '11+21+41'
        )

        self.assertEqual(
            HPOSet.from_serialized('11+21+41'),
            a
        )

    def test_remove_modifier(self):
        terms = make_ontology_with_modifiers()

        normal_term_ids = set(
            [1, 11, 12, 21, 31, 41, 13]
        )
        modifier_term_ids = set(
            [5, 12823, 5000001, 5000002, 5100001]
        )

        self.assertEqual(
            len(terms),
            (len(normal_term_ids | modifier_term_ids))
        )

        full_set = HPOSet.from_queries(
            normal_term_ids | modifier_term_ids
        )

        self.assertEqual(
            len(full_set),
            len(normal_term_ids | modifier_term_ids)
        )

        set_2 = full_set.remove_modifier()
        self.assertEqual(
            len(set_2),
            len(normal_term_ids)
        )

        self.assertEqual(
            (normal_term_ids | modifier_term_ids),
            {int(x) for x in full_set}
        )

        self.assertEqual(
            normal_term_ids,
            {int(x) for x in set_2}
        )

    def test_adding_terms(self):
        hposet = HPOSet([
            self.ontology[1],
            self.ontology[11],
            self.ontology[41]
        ])
        self.assertEqual(
            hposet,
            set([
                self.ontology[1],
                self.ontology[11],
                self.ontology[41]
            ])
        )
        self.assertEqual(
            len(hposet),
            len(hposet._list)
        )

        hposet.add(self.ontology[41])
        self.assertEqual(
            hposet,
            set([
                self.ontology[1],
                self.ontology[11],
                self.ontology[41]
            ])
        )
        self.assertEqual(
            len(hposet),
            len(hposet._list)
        )

        hposet.add(self.ontology[31])
        self.assertEqual(
            hposet,
            set([
                self.ontology[1],
                self.ontology[11],
                self.ontology[31],
                self.ontology[41]
            ])
        )
        self.assertEqual(
            len(hposet),
            len(hposet._list)
        )

    def test_updating_terms(self):
        hposet = HPOSet([
            self.ontology[1],
            self.ontology[11],
            self.ontology[41]
        ])
        self.assertEqual(
            hposet,
            set([
                self.ontology[1],
                self.ontology[11],
                self.ontology[41]
            ])
        )
        self.assertEqual(
            len(hposet),
            len(hposet._list)
        )

        hposet.update([
            self.ontology[41],
            self.ontology[31],
        ])
        self.assertEqual(
            hposet,
            set([
                self.ontology[1],
                self.ontology[11],
                self.ontology[31],
                self.ontology[41]
            ])
        )
        self.assertEqual(
            len(hposet),
            len(hposet._list)
        )

    def test_replacing_obsolete(self):
        ci = HPOSet([
            self.ontology[1],
            self.ontology[11],
            self.ontology[12],
            self.ontology[21],
            self.ontology[31]
        ])
        self.assertEqual(
            len(ci),
            5
        )
        ci2 = ci.replace_obsolete()
        self.assertEqual(
            len(ci2),
            5
        )

        self.ontology[12].is_obsolete = True
        self.ontology[12].replaced_by = 'HP:0041'
        ci2 = ci.replace_obsolete()
        self.assertEqual(
            len(ci2),
            5
        )
        self.assertEqual(
            ci2,
            set([
                self.ontology[1],
                self.ontology[11],
                self.ontology[41],
                self.ontology[21],
                self.ontology[31]
            ])
        )

        self.ontology[12].is_obsolete = 'False'
        self.ontology[12].replaced_by = 'HP:0041'
        ci2 = ci.replace_obsolete()
        self.assertEqual(
            len(ci2),
            5
        )
        self.assertEqual(
            ci2,
            set([
                self.ontology[1],
                self.ontology[11],
                self.ontology[12],
                self.ontology[21],
                self.ontology[31]
            ])
        )

    def test_removing_obsolete(self):
        ci = self.ci
        self.assertEqual(
            len(ci),
            len(self.ontology)
        )
        ci2 = ci.replace_obsolete()
        self.assertEqual(
            len(ci2),
            len(self.ontology)
        )

        self.ontology[12].is_obsolete = True
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            ci2 = ci.replace_obsolete()
            self.assertEqual(
                len(ci2),
                len(self.ontology)-1
            )


class BasicHPOSetTests(unittest.TestCase):
    def test_init(self):
        ontology = make_ontology()
        ci = BasicHPOSet([
            term for term in ontology
        ])
        self.assertEqual(
            ci,
            set([ontology[41], ontology[13]])
        )

    def test_remove_modifiers(self):
        ontology = make_ontology_with_modifiers()
        ci = BasicHPOSet([
            term for term in ontology
        ])
        self.assertEqual(
            ci,
            set([ontology[41], ontology[13]])
        )

    def test_remove_duplicate_terms(self):
        ontology = make_ontology()
        ci = BasicHPOSet([
            term for term in ontology
        ] + [ontology[41]])
        self.assertEqual(
            ci,
            set([ontology[41], ontology[13]])
        )


class SetMetricsTests(unittest.TestCase):
    def setUp(self):
        self.ontology = make_ontology()
        self.ci = HPOSet([
            term for term in self.ontology
        ])

    def test_variance(self):
        with patch.object(
            HPOTerm,
            'path_to_other',
            side_effect=[
                (1, None),
                (1, None),
                (1, None),
                (1, None),
                (1, None),
                (1, None),
                (2, None),
                (2, None),
                (2, None),
                (2, None),
                (2, None),
                (3, None),
                (3, None),
                (3, None),
                (3, None),
                (4, None),
                (4, None),
                (4, None),
                (5, None),
                (5, None),
                (6, None)
            ]
        ) as mock_pto:
            res = self.ci.variance()
            assert len(res) == 4, len(res)
            assert 1 < res[0] < 7, res[0]
            assert res[1] == 1
            assert res[2] == 6, res[2]
            assert len(res[3]) == 6+5+4+3+2+1, len(res[3])

            calls = [
                call(self.ci._list[1]),
                call(self.ci._list[2]),
                call(self.ci._list[3]),
                call(self.ci._list[4]),
                call(self.ci._list[5]),
                call(self.ci._list[6]),
                call(self.ci._list[2]),
                call(self.ci._list[3]),
                call(self.ci._list[4]),
                call(self.ci._list[5]),
                call(self.ci._list[6]),
                call(self.ci._list[3]),
                call(self.ci._list[4]),
                call(self.ci._list[5]),
                call(self.ci._list[6]),
                call(self.ci._list[4]),
                call(self.ci._list[5]),
                call(self.ci._list[6]),
                call(self.ci._list[5]),
                call(self.ci._list[6]),
                call(self.ci._list[6])
            ]
            mock_pto.assert_has_calls(calls)

    def test_no_variance(self):
        ci = HPOSet([self.ontology[1]])
        assert ci.variance() == (0, 0, 0, [])

    def test_information_content(self):
        i = 0
        for term in self.ci:
            term.information_content['omim'] = i
            term.information_content['gene'] = i*2
            i += 1
        res = self.ci.information_content()

        assert res['mean'] == 3.0
        assert res['total'] == 21
        assert res['max'] == 6
        assert res['all'] == [0, 1, 2, 3, 4, 5, 6]

        # checking default value
        assert self.ci.information_content() == res

        res = self.ci.information_content('gene')

        assert res['mean'] == 6.0
        assert res['total'] == 42
        assert res['max'] == 12
        assert res['all'] == [0, 2, 4, 6, 8, 10, 12]


class SimilarityTests(unittest.TestCase):
    def setUp(self):
        self.terms = make_terms()

    def test_simsilarity_arg_forwarding(self):
        with patch.object(
            HPOSet,
            '_sim_score',
            return_value=Matrix(1, 1, [1])
        ) as mock_simscore:
            set1 = HPOSet([self.terms[0]])
            set2 = HPOSet([self.terms[1]])

            _ = set1.similarity(set2)
            mock_simscore.assert_called_once_with(
                set1, set2, None, None
            )
            mock_simscore.reset_mock()

            _ = set1.similarity(set2, 'foo')
            mock_simscore.assert_called_once_with(
                set1, set2, 'foo', None
            )
            mock_simscore.reset_mock()

            _ = set1.similarity(set2, kind='foo')
            mock_simscore.assert_called_once_with(
                set1, set2, 'foo', None
            )
            mock_simscore.reset_mock()

            _ = set1.similarity(set2, 'foo', 'bar')
            mock_simscore.assert_called_once_with(
                set1, set2, 'foo', 'bar'
            )
            mock_simscore.reset_mock()

            _ = set1.similarity(set2, kind='foo', method='bar')
            mock_simscore.assert_called_once_with(
                set1, set2, 'foo', 'bar'
            )
            mock_simscore.reset_mock()

            _ = set1.similarity(set2, method='bar')
            mock_simscore.assert_called_once_with(
                set1, set2, None, 'bar'
            )
            mock_simscore.reset_mock()

            _ = set1.similarity(set2, None, 'bar')
            mock_simscore.assert_called_once_with(
                set1, set2, None, 'bar'
            )
            mock_simscore.reset_mock()

    def test_equality_score_call(self):
        with patch.object(
            HPOSet,
            '_sim_score',
            return_value=None
        ) as mock_simscore, patch.object(
            HPOSet,
            '_equality_score',
            return_value=12
        ) as mock_equality_score:
            set1 = HPOSet([self.terms[0]])
            set2 = HPOSet([self.terms[1]])

            res = set1.similarity(set2, method='equal')
            mock_simscore.assert_not_called()
            mock_equality_score.assert_called_once_with(
                set2
            )
            self.assertEqual(res, 12)

    def test_funSimAvg(self):
        with patch.object(
            HPOSet,
            '_sim_score',
            return_value=Matrix(2, 4, [1, 0.5, 2, 4, 2, 3, 1, 1])
        ) as mock_simscore:
            """
            Row maxes: 4, 3 ==> 7 ==> 7/2 = 3.5
            Col maxes: 2, 3, 2, 4 ==> 11 ==> 11/4 = 2.75
            """

            set1 = HPOSet([self.terms[0]])
            set2 = HPOSet([self.terms[1]])

            res = set1.similarity(set2)
            mock_simscore.assert_called_once_with(set1, set2, None, None)
            self.assertEqual(res, 3.125)

    def test_funSimMax(self):
        with patch.object(
            HPOSet,
            '_sim_score',
            return_value=Matrix(2, 4, [1, 0.5, 2, 4, 2, 3, 1, 1])
        ) as mock_simscore:
            """
            Row maxes: 4, 3 ==> 7 ==> 7/2 = 3.5
            Col maxes: 2, 3, 2, 4 ==> 11 ==> 11/4 = 2.75
            """

            set1 = HPOSet([self.terms[0]])
            set2 = HPOSet([self.terms[1]])

            res = set1.similarity(set2, combine='funSimMax')
            mock_simscore.assert_called_once_with(set1, set2, None, None)
            self.assertEqual(res, 3.5)

    def test_funSimBMA(self):
        with patch.object(
            HPOSet,
            '_sim_score',
            return_value=Matrix(2, 4, [1, 0.5, 2, 4, 2, 3, 1, 1])
        ) as mock_simscore:
            """
            Row maxes: 4, 3 ==> 7 ==> 7
            Col maxes: 2, 3, 2, 4 ==> 11 ==> 11
            ==> 18 / 6
            """

            set1 = HPOSet([self.terms[0]])
            set2 = HPOSet([self.terms[1]])

            res = set1.similarity(set2, combine='BMA')
            mock_simscore.assert_called_once_with(set1, set2, None, None)
            self.assertEqual(res, 3)

    def test_invalid_combine_method(self):
        with patch.object(
            HPOSet,
            '_sim_score',
            return_value=Matrix(2, 4, [1, 0.5, 2, 4, 2, 3, 1, 1])
        ) as mock_simscore:
            with self.assertRaises(
                RuntimeError
            ) as context:
                set1 = HPOSet([self.terms[0]])
                set2 = HPOSet([self.terms[1]])

                _ = set1.similarity(set2, combine='invalid')
            mock_simscore.assert_called_once_with(set1, set2, None, None)
        self.assertEqual(
            str(context.exception),
            'Invalid combine method specified'
        )

    def test_empty_sets(self):
        with patch.object(
            HPOSet,
            '_sim_score',
            return_value=Matrix(0, 0, [])
        ) as mock_simscore:
            """
            Row maxes: 4, 3 ==> 7 ==> 7
            Col maxes: 2, 3, 2, 4 ==> 11 ==> 11
            ==> 18 / 6
            """

            set1 = HPOSet([self.terms[0]])
            set2 = HPOSet([self.terms[1]])

            res = set1.similarity(set2, combine='BMA')
            mock_simscore.assert_called_once_with(set1, set2, None, None)
            self.assertEqual(res, 0)


class SimScoreTests(unittest.TestCase):
    def setUp(self):
        self.terms = make_terms()

    def test_empty_sim_score(self):
        with patch.object(
            HPOTerm,
            'similarity_score',
            side_effect=[1, 0.5, 2, 4, 2, 3, 1, 1]
        ) as mock_simscore:
            set1 = HPOSet([])
            set2 = HPOSet(self.terms[2:6])
            scores = HPOSet._sim_score(set1, set2, 'omim')
            self.assertEqual(
                scores._data,
                []
            )
            mock_simscore.assert_not_called()
            mock_simscore.reset_mock()

            set1 = HPOSet(self.terms[0:2])
            set2 = HPOSet([])
            scores = HPOSet._sim_score(set1, set2, 'omim')
            self.assertEqual(
                scores._data,
                []
            )
            mock_simscore.assert_not_called()
            mock_simscore.reset_mock()

            set1 = HPOSet([])
            set2 = HPOSet([])
            scores = HPOSet._sim_score(set1, set2, 'omim')
            self.assertEqual(
                scores._data,
                []
            )
            mock_simscore.assert_not_called()

    def test_sim_score(self):
        with patch.object(
            HPOTerm,
            'similarity_score',
            side_effect=[1, 0.5, 2, 4, 2, 3, 1, 1]
        ) as mock_simscore:
            set1 = HPOSet(self.terms[0:2])
            set2 = HPOSet(self.terms[2:6])
            scores = HPOSet._sim_score(set1, set2)

            calls = [
                call(self.terms[2], None, None),
                call(self.terms[3], None, None),
                call(self.terms[4], None, None),
                call(self.terms[5], None, None)
            ]
            mock_simscore.assert_has_calls(calls, any_order=True)
            self.assertEqual(
                mock_simscore.call_count,
                8
            )
            self.assertEqual(
                list(scores.columns),
                [
                    [1, 2],
                    [0.5, 3],
                    [2, 1],
                    [4, 1]
                ]
            )
            self.assertEqual(
                list(scores.rows),
                [
                    [1, 0.5, 2, 4],
                    [2, 3, 1, 1]
                ]
            )

    def test_single_comparison_sim_score(self):
        with patch.object(
            HPOTerm,
            'similarity_score',
            side_effect=[5, 0.5, 2, 4, 2, 3, 1, 1]
        ) as mock_simscore:
            set1 = HPOSet([self.terms[0]])
            set2 = HPOSet([self.terms[1]])
            scores = HPOSet._sim_score(set1, set2)

            mock_simscore.assert_called_once_with(
                self.terms[1], None, None
            )
            self.assertEqual(
                mock_simscore.call_count,
                1
            )
            self.assertEqual(
                list(scores.columns),
                [[5]]
            )
            self.assertEqual(
                list(scores.rows),
                [[5]]
            )

    def test_simscore_arg_forwarding(self):
        with patch.object(
            HPOTerm,
            'similarity_score',
            return_value=None
        ) as mock_simscore:
            set1 = HPOSet([self.terms[0]])
            set2 = HPOSet([self.terms[1]])

            _ = HPOSet._sim_score(set1, set2)
            mock_simscore.assert_called_once_with(
                self.terms[1], None, None
            )
            mock_simscore.reset_mock()

            _ = HPOSet._sim_score(set1, set2, 'foo')
            mock_simscore.assert_called_once_with(
                self.terms[1], 'foo', None
            )
            mock_simscore.reset_mock()

            _ = HPOSet._sim_score(set1, set2, kind='foo')
            mock_simscore.assert_called_once_with(
                self.terms[1], 'foo', None
            )
            mock_simscore.reset_mock()

            _ = HPOSet._sim_score(set1, set2, 'foo', 'bar')
            mock_simscore.assert_called_once_with(
                self.terms[1], 'foo', 'bar'
            )
            mock_simscore.reset_mock()

            _ = HPOSet._sim_score(set1, set2, kind='foo', method='bar')
            mock_simscore.assert_called_once_with(
                self.terms[1], 'foo', 'bar'
            )
            mock_simscore.reset_mock()

            _ = HPOSet._sim_score(set1, set2, method='bar')
            mock_simscore.assert_called_once_with(
                self.terms[1], None, 'bar'
            )
            mock_simscore.reset_mock()

            _ = HPOSet._sim_score(set1, set2, None, 'bar')
            mock_simscore.assert_called_once_with(
                self.terms[1], None, 'bar'
            )
            mock_simscore.reset_mock()


class EqualityScoreTests(unittest.TestCase):
    def setUp(self):
        self.terms = make_terms()

    def test_empty_sets(self):
        set1 = HPOSet([])
        set2 = HPOSet(self.terms[2:6])
        res = set1._equality_score(HPOSet(self.terms[2:6]))
        self.assertEqual(res, 0)

        res = set1._equality_score(HPOSet([]))
        self.assertEqual(res, 0)

        res = set2._equality_score(HPOSet([]))
        self.assertEqual(res, 0)

        res = set2._equality_score(set2)
        self.assertEqual(res, 1)

        res = set2._equality_score(HPOSet(self.terms[3:7]))
        self.assertEqual(res, 0.75)

        res = set2._equality_score(HPOSet(self.terms[4:8]))
        self.assertEqual(res, 0.5)

        res = set2._equality_score(HPOSet(self.terms[5:8]))
        self.assertEqual(res, 0.25)
