import unittest
from unittest.mock import MagicMock

from pyhpo.similarity import base


class Test_Simscore_registers(unittest.TestCase):
    def setUp(self):
        self.simscore = base._Similarity()

    def test_defaults(self):
        assert self.simscore.kind == 'omim'
        assert self.simscore.method == 'graphic'

    def test_invalid_method(self):
        with self.assertRaises(RuntimeError) as err:
            self.simscore(term1={}, term2={}, method='foobar')
        assert str(err.exception) == (
            'Unknown method foobar to calculate similarity'
        )

    def test_default_fallback(self):
        mock_graphic = MagicMock(return_value=12)
        self.simscore.register('graphic', MagicMock(return_value=mock_graphic))
        res = self.simscore({}, {})
        assert res == 12
        mock_graphic.assert_called_once_with({}, {}, 'omim', [])


if __name__ == "__main__":
    unittest.main()
