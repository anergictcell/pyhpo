from unittest import TestCase

from pyhpo.parser.obo import parse_obo_section, terms_from_file
from pyhpo import HPOTerm


class OboParsingTest(TestCase):
    def setUp(self):
        self.a1 = [
            'id: HP:0000001',
            'name: All',
            'comment: Root of all terms in the Human Phenotype Ontology.',
            'xref: UMLS:C0444868',
        ]

        self.a2 = [
            'id: HP:0000002',
            'name: Abnormality of body height',
            'def: "Deviation from the norm of height with respect to that which is expected according to age and gender norms." [HPO:probinson]',
            'synonym: "Abnormality of body height" EXACT layperson []',
            'xref: UMLS:C4025901',
            'is_a: HP:0001507 ! Growth abnormality',
            'created_by: peter',
            'creation_date: 2008-02-27T02:20:00Z'
        ]

        self.a3 = [
            'id: HP:0000003',
            'name: Multicystic kidney dysplasia',
            'alt_id: HP:0004715',
            'def: "Multicystic dysplasia of the kidney is characterized by multiple cysts of varying size in the kidney and the absence of a normal pelvicaliceal system. The condition is associated with ureteral or ureteropelvic atresia, and the affected kidney is nonfunctional." [HPO:curators]',
            'comment: Multicystic kidney dysplasia is the result of abnormal fetal renal development in which the affected kidney is replaced by multiple cysts and has little or no residual function. The vast majority of multicystic kidneys are unilateral. Multicystic kidney can be diagnosed on prenatal ultrasound.',
            'synonym: "Multicystic dysplastic kidney" EXACT []',
            'synonym: "Multicystic kidneys" EXACT []',
            'synonym: "Multicystic renal dysplasia" EXACT []',
            'xref: MSH:D021782',
            'xref: SNOMEDCT_US:204962002',
            'xref: SNOMEDCT_US:82525005',
            'xref: UMLS:C3714581',
            'is_a: HP:0000107 ! Renal cyst'
        ]

    def test_root_term(self):
        a = parse_obo_section(self.a1)
        self.assertEqual(a['id'], 'HP:0000001')
        self.assertEqual(a['name'], 'All')
        self.assertEqual(
            a['comment'],
            'Root of all terms in the Human Phenotype Ontology.'
        )
        self.assertEqual(a['definition'], '')
        self.assertEqual(a['is_obsolete'], False)
        self.assertEqual(a['replaced_by'], '')
        self.assertEqual(a['xref'], ['UMLS:C0444868'])

        term = HPOTerm(**a)
        self.assertEqual(
            term.index,
            1
        )
        self.assertEqual(
            term.id,
            'HP:0000001'
        )
        self.assertEqual(
            term.name,
            'All'
        )
        
    def test_full_load(self):
        for term in terms_from_file('pyhpo/data'):
            # print(term['id'])
            HPOTerm(**term)

# print('=========== A 1 =============')
# t1 = HPOTerm.from_obo_term_section(a1)
# print('=========== A 2 =============')
# t2 = HPOTerm.from_obo_term_section(a2)
# print('=========== A 3 =============')
# t3 = HPOTerm.from_obo_term_section(a3)


"""
    @unittest.skip('Refactored')
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

    @unittest.skip('Refactored')
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

    @unittest.skip('Refactored')
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

    @unittest.skip('Refactored')
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
"""
