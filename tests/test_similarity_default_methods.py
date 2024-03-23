import unittest
from unittest.mock import MagicMock

import pyhpo.similarity.defaults as d
import pyhpo.similarity.base as base

from tests.mockontology import make_terms


class TestSimilarity_independent(unittest.TestCase):
    def setUp(self):
        self.simscore = base._Similarity()

    def test_resnik(self):
        self.simscore.register("resnik", d.Resnik)
        terms = make_terms()
        t1 = MagicMock()
        t1.common_ancestors = MagicMock(return_value=terms[0:3])
        terms[0].information_content.omim = 0.5
        terms[1].information_content.omim = 0.7
        terms[2].information_content.omim = 0.6
        res = self.simscore(t1, {}, method="resnik")
        assert res == 0.7

    def test_graphic(self):
        self.simscore.register("graphic", d.GraphIC)
        terms = make_terms()
        t1 = MagicMock()
        t1.common_ancestors = MagicMock(return_value=terms[2:4])
        t1.all_parents = set(terms[0:4])

        t2 = MagicMock()
        t2.all_parents = set(terms[3:5])

        terms[0].information_content.omim = 0.5
        terms[1].information_content.omim = 0.7
        terms[2].information_content.omim = 0.6
        terms[3].information_content.omim = 0.2
        terms[4].information_content.omim = 0.1

        # common: 0.6 + 0.2 => 0.8
        # union: (0.5 + 0.7 + 0.6 + 0.2) + 0.1 => 2.1
        res = self.simscore(t1, t2, method="graphic")
        assert int(res * 10_000) == 3809, res

    def test_graphic_zero(self):
        self.simscore.register("graphic", d.GraphIC)
        t1 = MagicMock()
        t1.common_ancestors = MagicMock(return_value=[])
        t1.all_parents = set([])

        t2 = MagicMock()
        t2.all_parents = set([])

        res = self.simscore(t1, t2, method="graphic")
        assert res == 0.0, res

    def test_graphic_equal(self):
        self.simscore.register("graphic", d.GraphIC)

        term = "foo"
        res = self.simscore(term, term, method="graphic")
        assert res == 1.0, res

    def test_distance(self):
        self.simscore.register("dist", d.Distance)
        t1 = MagicMock()
        t1.path_to_other = MagicMock(return_value=[2, ("foo", "bar"), 1, 1])

        # 1 / (2 + 1)
        res = self.simscore(t1, {}, method="dist")
        assert int(res * 10_000) == 3333, res

    def test_distance_zero(self):
        self.simscore.register("dist", d.Distance)
        t1 = MagicMock()
        t1.path_to_other = MagicMock(return_value=[])

        res = self.simscore(t1, {}, method="dist")
        assert res == 0.0, res


class TestSimlarity_resnik_dependency(unittest.TestCase):
    def setUp(self):
        self.simscore = base._Similarity()
        mock_resnik = MagicMock(return_value=0.9)
        mock_resnik.dependencies = []
        self.simscore.dispatch["resnik"] = mock_resnik

    def test_lin(self):
        self.simscore.register("lin", d.Lin)
        terms = make_terms()
        terms[0].information_content.omim = 0.5
        terms[1].information_content.omim = 0.7

        # 1.8 / (0.5+0.7) = 1.5
        res = self.simscore(terms[0], terms[1], method="lin")
        assert res == 1.5, res

    def test_lin_zero(self):
        self.simscore.register("lin", d.Lin)
        terms = make_terms()
        terms[0].information_content.omim = 0
        terms[1].information_content.omim = 0

        res = self.simscore(terms[0], terms[1], method="lin")
        assert res == 0.0, res

    def test_jc(self):
        # Resnik retuns 0.9
        self.simscore.register("jc", d.JC)
        terms = make_terms()
        terms[0].information_content.omim = 1.6
        terms[1].information_content.omim = 1.2
        # 1 / 1.6 + 1.2 - 2 x 0.9 + 1
        # 1 / 2.8 - 1.8 + 1
        # 1 / 2
        res = self.simscore(terms[0], terms[1], method="jc")
        assert int(res * 10) == 5, res

        terms[0].information_content.omim = 0
        terms[1].information_content.omim = 1.2
        res = self.simscore(terms[0], terms[1], method="jc")
        assert res == 0.0, res

        terms[0].information_content.omim = 1.8
        terms[1].information_content.omim = 0
        res = self.simscore(terms[0], terms[1], method="jc")
        assert res == 0.0, res

    def test_jc_identical(self):
        self.simscore.register("jc", d.JC)

        term = "foo"
        res = self.simscore(term, term, method="jc")
        assert res == 1


class TestSimilarity_resnik_lin_dependencies(unittest.TestCase):
    def setUp(self):
        self.simscore = base._Similarity()

        mock_resnik = MagicMock(return_value=0.9)
        mock_resnik.dependencies = []
        self.simscore.dispatch["resnik"] = mock_resnik

        mock_lin = MagicMock(return_value=1.5)
        mock_lin.dependencies = []
        self.simscore.dispatch["lin"] = mock_lin

    def test_relevance(self):
        self.simscore.register("rel", d.Relevance)

        # 1.5 * (1 - e**(0.9*-1))
        res = self.simscore({}, {}, method="rel")
        assert int(res * 10_000) == 8901, res

    def test_ic(self):
        self.simscore.register("ic", d.InformationCoefficient)

        # 1.5 * (1 - (1 / (1 + 0.9) ) )
        res = self.simscore({}, {}, method="ic")
        assert int(res * 10_000) == 7105, res


if __name__ == "__main__":
    unittest.main()
