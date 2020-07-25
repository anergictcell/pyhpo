import unittest
import warnings

from pyhpo.ontology import HPOTerm


TEST_HPO = [
    '[Term]',
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


class StaticMethodsTest(unittest.TestCase):
    def test_id_parsing(self):
        assert HPOTerm.id_from_string('HP:00001') == 1
        assert HPOTerm.id_from_string(
            'HP:0001507 ! Growth abnormality'
        ) == 1507
        assert HPOTerm.id_from_string('HP:0000105') == 105

    def test_id_parsing_newline(self):
        assert HPOTerm.id_from_string('HP:00001\n') == 1
        assert HPOTerm.id_from_string(
            'HP:0001507 ! Growth abnormality\n'
        ) == 1507
        assert HPOTerm.id_from_string('HP:0000105\n') == 105

    def test_id_parsing_r_newline(self):
        assert HPOTerm.id_from_string('HP:00001\r\n') == 1
        assert HPOTerm.id_from_string(
            'HP:0001507 ! Growth abnormality\r\n'
        ) == 1507
        assert HPOTerm.id_from_string('HP:0000105\r\n') == 105

    def test_id_parsing_errors(self):
        with self.assertRaises(ValueError) as context:
            HPOTerm.id_from_string('HP:anotherstring')
        assert 'invalid literal for int()' in str(context.exception)

        with self.assertRaises(IndexError) as context:
            HPOTerm.id_from_string('HP12345')
        assert 'list index out of range' == str(context.exception)

        with self.assertRaises(AttributeError) as context:
            HPOTerm.id_from_string(12)
        self.assertEqual(
            "'int' object has no attribute 'split'",
            str(context.exception)
        )

    def test_synonym_parsing(self):
        assert HPOTerm.parse_synonym(
            '"Abnormality of body height" EXACT layperson []'
        ) == 'Abnormality of body height'
        assert HPOTerm.parse_synonym(
            '"Autosomal dominant type" RELATED [HPO:skoehler]'
        ) == 'Autosomal dominant type'
        assert HPOTerm.parse_synonym(
            '"Scalp hair loss" EXACT layperson [ORCID:0000-0001-5889-4463]'
        ) == 'Scalp hair loss'

    def test_synonym_parsing_newline(self):
        assert HPOTerm.parse_synonym(
            '"Abnormality of body height" EXACT layperson []\n'
        ) == 'Abnormality of body height'
        assert HPOTerm.parse_synonym(
            '"Autosomal dominant type" RELATED [HPO:skoehler]\n'
        ) == 'Autosomal dominant type'
        assert HPOTerm.parse_synonym(
            '"Scalp hair loss" EXACT layperson [ORCID:0000-0001-5889-4463]\n'
        ) == 'Scalp hair loss'

    def test_synonym_parsing_r_newline(self):
        assert HPOTerm.parse_synonym(
            '"Abnormality of body height" EXACT layperson []\r\n'
        ) == 'Abnormality of body height'
        assert HPOTerm.parse_synonym(
            '"Autosomal dominant type" RELATED [HPO:skoehler]\r\n'
        ) == 'Autosomal dominant type'
        assert HPOTerm.parse_synonym(
            '"Scalp hair loss" EXACT layperson [ORCID:0000-0001-5889-4463]\r\n'
        ) == 'Scalp hair loss'

    def test_synonym_parsing_errors(self):
        with self.assertRaises(IndexError) as context:
            HPOTerm.parse_synonym('synonym: Scalp hair loss')
        assert 'list index out of range' == str(context.exception)

        with self.assertRaises(AttributeError) as context:
            HPOTerm.parse_synonym(12)
        self.assertEqual(
            "'int' object has no attribute 'split'",
            str(context.exception)
        )


class TermInit(unittest.TestCase):
    def setUp(self):
        self.term = HPOTerm()

    def test_init(self):
        self.term.add_line('testkey: test value')
        assert self.term.testkey == 'test value'

    def test_id(self):
        self.term.add_line('id: HP:00001')
        assert self.term._id == 'HP:00001'
        assert self.term._index == 1

    def test_id_errors(self):
        self.term.add_line('id: HP:00001')
        with self.assertRaises(RuntimeError) as err:
            self.term.add_line('id: HP:00002')
        assert 'Unable to update existing ID' == str(err.exception)

    def test_empty_line(self):
        a = HPOTerm()
        b = HPOTerm()
        a.add_line('')
        for attrs in a.__dict__:
            assert a.__getattribute__(attrs) == b.__getattribute__(attrs)


class SingleTermAttributes(unittest.TestCase):
    def setUp(self):
        self.term = HPOTerm()
        for line in TEST_HPO:
            self.term.add_line(line)

    def test_term(self):
        term = self.term
        assert term.id == 'HP:0004944'
        assert term._index == 4944
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
        assert term.is_a == [
            'HP:0002617 ! Dilatation',
            'HP:0009145 ! Abnormal cerebral artery morphology'
        ]
        assert term.parent_ids() == [2617, 9145]
        assert term.hierarchy() == ((term,),)
        self.assertEqual(
            term.toJSON().keys(),
            {'int', 'id', 'name'}
        )
        self.assertEqual(
            term.toJSON(verbose=True).keys(),
            {'int', 'id', 'name', 'def', 'comment', 'synonym', 'xref', 'is_a'}
        )
        self.assertEqual(
            term.toJSON()['id'],
            term.id
        )
        self.assertEqual(
            term.toJSON()['int'],
            term._index
        )
        self.assertEqual(
            term.toJSON()['name'],
            term.name
        )
        self.assertEqual(
            term.toJSON(verbose=True)['def'],
            term.definition
        )
        self.assertEqual(
            term.toJSON(verbose=True)['comment'],
            term.comment
        )
        self.assertEqual(
            term.toJSON(verbose=True)['synonym'],
            term._synonym
        )
        self.assertEqual(
            term.toJSON(verbose=True)['xref'],
            term._xref
        )
        self.assertEqual(
            term.toJSON(verbose=True)['is_a'],
            term._is_a
        )


class TermAnnotations(unittest.TestCase):
    def setUp(self):
        self.term = HPOTerm()
        for line in TEST_HPO:
            self.term.add_line(line)

    def test_empty_genes(self):
        assert self.term._annotations['genes'] == [set(), False]

        _ = self.term.genes
        assert self.term._annotations['genes'] == [set(), True]

    def test_gene_setting(self):
        self.term.genes = set([1, 2])
        assert len(self.term.genes) == 2, self.term.genes

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")

            self.term.genes = set([3])
            assert len(self.term.genes) == 3

            # Item already present, set will not be updated
            self.term.genes = set([1])
            assert len(self.term.genes) == 3

            with self.assertRaises(RuntimeError) as err:
                self.term.genes = 14
                assert 'Genes must be specified as set' in str(err.exception)

            with self.assertRaises(RuntimeError) as err:
                self.term.genes = 'string'
                assert 'Genes must be specified as set' in str(err.exception)

            with self.assertRaises(RuntimeError) as err:
                self.term.genes = [5, 6, 7]
                assert 'Genes must be specified as set' in str(err.exception)

    def test_genes_and_cache(self):
        # Private cache value must be None initially
        assert not self.term._annotations['genes'][1]

        self.term.genes = set(['Gene1', 'Gene2'])

        # Private cache value should remain None until
        # it needs to be checked
        assert not self.term._annotations['genes'][1]

        assert self.term.genes == set(['Gene1', 'Gene2'])

        # Once ``genes`` has been accessed, private cache must be updated
        assert self.term._annotations['genes'][1]
        assert self.term._annotations['genes'][0] == set(['Gene1', 'Gene2'])

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.term.genes = set(['Gene3'])

        assert self.term._annotations['genes'][1]
        assert self.term.genes == set(['Gene1', 'Gene2', 'Gene3'])
        assert self.term._annotations['genes'][0] == set(['Gene1', 'Gene2', 'Gene3'])

    def test_gene_parent_update(self):
        term2 = HPOTerm()
        term2.add_line('id: HP:000001')
        term2.add_line('name: General parent term')
        term2.children = self.term
        self.term.parents = term2

        # Both terms should not have a cache-flag yet
        assert not self.term._annotations['genes'][1]
        assert not term2._annotations['genes'][1]

        # Adding genes to one term should not affect the caches
        self.term.genes = set(['Gene1', 'Gene2'])
        assert not self.term._annotations['genes'][1]
        assert not term2._annotations['genes'][1]

        # Retrieving genes from term should
        # built the cache on term
        # have no effect on term2 cache
        assert self.term.genes == set(['Gene1', 'Gene2'])
        assert self.term._annotations['genes'][1]
        assert not term2._annotations['genes'][1]

        # Retrieving genes from term2
        # (should be identical to child term1)
        # shoud set cache-flag on term2
        assert term2.genes == set(['Gene1', 'Gene2'])
        assert term2._annotations['genes'][1]
        assert term2._annotations['genes'][0] == set(['Gene1', 'Gene2'])

        # Adding a new gene to term1
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            self.term.genes = set(['Gene3'])

        assert self.term._annotations['genes'][1]
        assert self.term._annotations['genes'][0] == set(['Gene1', 'Gene2', 'Gene3'])

        assert term2._annotations['genes'][1]
        assert term2._annotations['genes'][0] == set(['Gene1', 'Gene2', 'Gene3'])

        assert self.term.genes == set(['Gene1', 'Gene2', 'Gene3'])
        assert term2.genes == set(['Gene1', 'Gene2', 'Gene3'])
