import unittest

from mockontology import make_terms


class informationContentTest(unittest.TestCase):
    def setUp(self):
        self.terms = make_terms()
        self.root = self.terms[0]

    def test_defaults(self):
        self.assertEqual(self.root.information_content['omim'] , 0.0)
        self.assertEqual(self.root.information_content['gene'] , 0.0)
        self.assertEqual(self.root.information_content['orpha'] , 0.0)
        self.assertEqual(self.root.information_content['decipher'] , 0.0)

        with self.assertRaises(AttributeError):
            self.root.information_content['foobar']

    def test_setters(self):
        self.root.information_content.omim = 1.0
        self.root.information_content.gene = 2.1
        self.root.information_content.orpha = 3.2
        self.root.information_content.decipher = 4.3

        self.assertEqual(self.root.information_content['omim'] , 1.0)
        self.assertEqual(self.root.information_content['gene'] , 2.1)
        self.assertEqual(self.root.information_content['orpha'] , 3.2)
        self.assertEqual(self.root.information_content['decipher'] , 4.3)

        self.assertEqual(self.root.information_content['omim'] , self.root.information_content.omim)
        self.assertEqual(self.root.information_content['gene'] , self.root.information_content.gene)
        self.assertEqual(
            self.root.information_content['orpha'],
            self.root.information_content.orpha
        )
        self.assertEqual(
            self.root.information_content['decipher'],
            self.root.information_content.decipher
        )

        self.assertEqual(self.terms[1].information_content['omim'] , 0.0)
        self.assertEqual(self.terms[1].information_content['gene'] , 0.0)
        self.assertEqual(self.terms[1].information_content['orpha'] , 0.0)
        self.assertEqual(self.terms[1].information_content['decipher'] , 0.0)

    def test_custom(self):
        self.root.information_content.set_custom('foobar', 5.4)
        self.terms[1].information_content.set_custom('foobar', 6.6)

        self.assertEqual(self.root.information_content['foobar'] , 5.4)
        self.assertEqual(self.terms[1].information_content['foobar'] , 6.6)

        self.assertEqual(self.root.information_content['omim'] , 0.0)
        self.assertEqual(self.root.information_content['gene'] , 0.0)
        self.assertEqual(self.root.information_content['orpha'] , 0.0)
        self.assertEqual(self.root.information_content['decipher'] , 0.0)
