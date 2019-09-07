import unittest
from pyhpo.ontology import Ontology


class MockOntology:
    def __init__(self, id=1):
        self._index = int(id)


class OntologySizeTests(unittest.TestCase):
    def test_sizes(self):
        a = Ontology(filename=None)
        assert len(a) == 0
        a._append(MockOntology())
        assert len(a) == 1
        a._append(MockOntology(5))
        assert len(a) == 2
        a._append(MockOntology(3))
        assert len(a) == 3
