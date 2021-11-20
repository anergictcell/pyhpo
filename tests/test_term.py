import unittest
from unittest.mock import patch

from pyhpo.ontology import HPOTerm
from pyhpo.parser.generics import id_from_string
from pyhpo.parser.obo import parse_obo_section
from pyhpo.parser.genes import add_gene_to_term


TEST_HPO = [
    'id: HP:0004944',
    'name: Dilatation of the cerebral artery',
    'alt_id: HP:0002618',
    'alt_id: HP:0006816',
    'def: "The presence of a localized dilatation or ballooning of a cerebral artery." [HPO:probinson]',  # noqa: E501
    'comment: Aneurysm is considered a severe form of dilatation.',
    'synonym: "Brain aneurysm" BROAD layperson [ORCID:0000-0001-6908-9849]',
    'synonym: "Cerebral aneurysm" NARROW []',
    'synonym: "Cerebral artery aneurysm" NARROW []',
    'synonym: "Intracranial aneurysm" BROAD []',
    'xref: MSH:D002532',
    'xref: SNOMEDCT_US:128608001',
    'xref: UMLS:C0751003',
    'xref: UMLS:C1290398',
    'is_a: HP:0002617 ! Dilatation',
    'is_a: HP:0009145 ! Abnormal cerebral artery morphology'
    ]


class TestStaticMethods(unittest.TestCase):
    def test_id_parsing(self):
        assert id_from_string('HP:00001') == 1
        assert id_from_string(
            'HP:0001507 ! Growth abnormality'
        ) == 1507
        assert id_from_string('HP:0000105') == 105

    def test_id_parsing_newline(self):
        assert id_from_string('HP:00001\n') == 1
        assert id_from_string(
            'HP:0001507 ! Growth abnormality\n'
        ) == 1507
        assert id_from_string('HP:0000105\n') == 105

    def test_id_parsing_r_newline(self):
        assert id_from_string('HP:00001\r\n') == 1
        assert id_from_string(
            'HP:0001507 ! Growth abnormality\r\n'
        ) == 1507
        assert id_from_string('HP:0000105\r\n') == 105

    def test_id_parsing_errors(self):
        with self.assertRaises(ValueError) as context:
            id_from_string('HP:anotherstring')
        assert 'invalid literal for int()' in str(context.exception)

        with self.assertRaises(IndexError) as context:
            id_from_string('HP12345')
        assert 'list index out of range' == str(context.exception)

        with self.assertRaises(AttributeError) as context:
            id_from_string(12)
        self.assertEqual(
            "'int' object has no attribute 'split'",
            str(context.exception)
        )


class TestTermInit(unittest.TestCase):
    def setUp(self):
        self.term = HPOTerm(**parse_obo_section(TEST_HPO))

    def test_init(self):
        self.assertIsNotNone(self.term._hash)
        self.assertEqual(
            self.term._hash,
            hash(self.term)
        )
        self.assertEqual(
            hash(self.term),
            hash((self.term.index, self.term.name))
        )

    def test_id(self):
        self.assertEqual(
            hash(self.term.index),
            4944
        )


class TestSingleTermAttributes(unittest.TestCase):
    def setUp(self):
        self.term = HPOTerm(**parse_obo_section(TEST_HPO))

    def test_term(self):
        term = self.term
        assert term.id == 'HP:0004944'
        assert term.index == 4944
        assert term.name == 'Dilatation of the cerebral artery'
        assert term.alt_id == ['HP:0002618', 'HP:0006816']
        self.assertEqual(
            term.definition,
            '"The presence of a localized dilatation or ballooning of a cerebral artery." [HPO:probinson]'  # noqa: E501
        )
        self.assertEqual(
            term.comment,
            'Aneurysm is considered a severe form of dilatation.'
        )
        assert term.synonym == [
            'Brain aneurysm',
            'Cerebral aneurysm',
            'Cerebral artery aneurysm',
            'Intracranial aneurysm'
        ]
        assert term.xref == [
            'MSH:D002532',
            'SNOMEDCT_US:128608001',
            'UMLS:C0751003',
            'UMLS:C1290398'
        ]
        assert term._is_a == [
            'HP:0002617 ! Dilatation',
            'HP:0009145 ! Abnormal cerebral artery morphology'
        ]
        self.assertEqual(
            term.parent_ids(),
            [2617, 9145]
        )
        self.assertEqual(
            term.hierarchy,
            ((term,),)
        )
        self.assertEqual(
            term.toJSON().keys(),
            {'int', 'id', 'name'}
        )
        self.assertEqual(
            term.toJSON(verbose=True).keys(),
            {
                'int',
                'id',
                'name',
                'definition',
                'comment',
                'synonym',
                'xref',
                'is_a',
                'ic'
            }
        )
        self.assertEqual(
            term.toJSON()['id'],
            term.id
        )
        self.assertEqual(
            term.toJSON()['int'],
            term.index
        )
        self.assertEqual(
            term.toJSON()['name'],
            term.name
        )
        self.assertEqual(
            term.toJSON(verbose=True)['definition'],
            term.definition
        )
        self.assertEqual(
            term.toJSON(verbose=True)['comment'],
            term.comment
        )
        self.assertEqual(
            term.toJSON(verbose=True)['synonym'],
            term.synonym
        )
        self.assertEqual(
            term.toJSON(verbose=True)['xref'],
            term.xref
        )
        self.assertEqual(
            term.toJSON(verbose=True)['is_a'],
            term._is_a
        )


class TestTermAnnotations(unittest.TestCase):
    def setUp(self):
        self.term = HPOTerm(**parse_obo_section(TEST_HPO))

    def test_empty_genes(self):
        self.assertEqual(
            self.term.genes,
            set()
        )

    def test_enter_genes(self):
        add_gene_to_term('Gene1', self.term)
        self.assertEqual(
            self.term.genes,
            set(['Gene1'])
        )

        add_gene_to_term('Gene2', self.term)
        self.assertIn(
            'Gene1',
            self.term.genes
        )
        self.assertIn(
            'Gene2',
            self.term.genes
        )
        self.assertEqual(
            len(self.term.genes),
            2
        )

    def test_gene_parent_update(self):
        term2 = HPOTerm(
            id='HP:000001', 
            name='General parent term'
        )
        self.term.parents.add(term2)

        # Both terms should not have a cache-flag yet
        self.assertEqual(self.term.genes, set())
        self.assertEqual(term2.genes, set())

        # Adding genes to child should update parent
        add_gene_to_term('Gene1', self.term)
        self.assertIn('Gene1', self.term.genes)
        self.assertIn('Gene1', term2.genes)

        # Adding genes to parent should not update child
        add_gene_to_term('Gene2', term2)
        self.assertNotIn('Gene2', self.term.genes)
        self.assertIn('Gene2', term2.genes)

        self.assertEqual(
            self.term.genes,
            set(['Gene1'])
        )
        self.assertEqual(
            term2.genes,
            set(['Gene1', 'Gene2'])
        )


class TestTermSimilarities(unittest.TestCase):
    def setUp(self):
        self.term = HPOTerm(**parse_obo_section(TEST_HPO))

        self.t1 = HPOTerm(id='HP:001', name='HP1')
        self.t1.Config.allow_mutation = True
        self.t1.information_content = {'omim': 1, 'gene': 11}
        self.t2 = HPOTerm(id='HP:002', name='HP2')
        self.t2.Config.allow_mutation = True
        self.t2.information_content = {'omim': 3, 'gene': 33}
        self.t3 = HPOTerm(id='HP:003', name='HP3')
        self.t3.Config.allow_mutation = True
        self.t3.information_content = {'omim': 2, 'gene': 22}

    @patch('pyhpo.term.SimScore')
    def test_similarity_call(self, mock_simscore):
        self.term.similarity_score('mockterm')
        mock_simscore.assert_called_once_with(
            self.term, 'mockterm', None, None
        )

    @patch('pyhpo.term.SimScore')
    def test_similarity_method_call(self, mock_simscore):

        self.term.similarity_score('mockterm', method='foo')
        mock_simscore.assert_called_once_with(
            self.term, 'mockterm', None, 'foo'
        )

        mock_simscore.reset_mock()
        self.term.similarity_score('mockterm', None, 'foo')
        mock_simscore.assert_called_once_with(
            self.term, 'mockterm', None, 'foo'
        )

        mock_simscore.reset_mock()
        self.term.similarity_score('mockterm', '', 'foo')
        mock_simscore.assert_called_once_with(
            self.term, 'mockterm', '', 'foo'
        )

    @patch('pyhpo.term.SimScore')
    def test_similarity_kind_call(self, mock_simscore):

        self.term.similarity_score('mockterm', kind='foo')
        mock_simscore.assert_called_once_with(
            self.term, 'mockterm', 'foo', None
        )

        mock_simscore.reset_mock()
        self.term.similarity_score('mockterm', 'foo', None)
        mock_simscore.assert_called_once_with(
            self.term, 'mockterm', 'foo', None
        )

        mock_simscore.reset_mock()
        self.term.similarity_score('mockterm', 'foo', '')
        mock_simscore.assert_called_once_with(
            self.term, 'mockterm', 'foo', ''
        )

    @patch('pyhpo.term.SimScore')
    def test_similarity_kind_method_call(self, mock_simscore):

        self.term.similarity_score('mockterm', kind='foo', method='bar')
        mock_simscore.assert_called_once_with(
            self.term, 'mockterm', 'foo', 'bar'
        )

        mock_simscore.reset_mock()
        self.term.similarity_score('mockterm', method='bar', kind='foo')
        mock_simscore.assert_called_once_with(
            self.term, 'mockterm', 'foo', 'bar'
        )

        mock_simscore.reset_mock()
        self.term.similarity_score('mockterm', 'foo', 'bar')
        mock_simscore.assert_called_once_with(
            self.term, 'mockterm', 'foo', 'bar'
        )
