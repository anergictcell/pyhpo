import os
import unittest

from pyhpo.parser.obo import parse_obo_section, terms_from_file, Converter
from pyhpo.parser.generics import remove_outcommented_rows
from pyhpo import HPOTerm


class OboParsingTest(unittest.TestCase):
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
            (
                'def: "Deviation from the norm of height with respect to that which ' +
                'is expected according to age and gender norms." [HPO:probinson]'
            ),
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
            (
                'def: "Multicystic dysplasia of the kidney is characterized by multiple ' +
                'cysts of varying size in the kidney and the absence of a normal pelvicaliceal ' +
                'system. The condition is associated with ureteral or ureteropelvic atresia, ' +
                'and the affected kidney is nonfunctional." [HPO:curators]'
            ),
            (
                'comment: Multicystic kidney dysplasia is the result of abnormal fetal renal ' +
                'development in which the affected kidney is replaced by multiple cysts and ' +
                'has little or no residual function. The vast majority of multicystic kidneys ' +
                'are unilateral. Multicystic kidney can be diagnosed on prenatal ultrasound.'
            ),
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
        data_dir = os.path.join(
            os.path.dirname(__file__),
            '../pyhpo/data'
        )
        for term in terms_from_file(data_dir):
            # just make sure it does not crash
            HPOTerm(**term)


class TestBasic(unittest.TestCase):
    def test_skipping_outcommented_rows(self):
        rows = [
            '#Skip',
            'Show',
            '#Ignore',
            'Show2'
        ]
        res = list(remove_outcommented_rows(rows))
        assert res == ['Show', 'Show2']

        res = list(remove_outcommented_rows(rows, ignorechar='#S'))
        assert res == ['Show', '#Ignore', 'Show2']

    def test_synonym_parsing(self):
        assert Converter.parse_synonym(
            ['"Abnormality of body height" EXACT layperson []'],
            'synonym',
            []
        ) == ['Abnormality of body height']

        assert Converter.parse_synonym(
            ['"Autosomal dominant type" RELATED [HPO:skoehler]'],
            'synonym',
            []
        ) == ['Autosomal dominant type']
        assert Converter.parse_synonym(
            ['"Scalp hair loss" EXACT layperson [ORCID:0000-0001-5889-4463]'],
            'synonym',
            []
        ) == ['Scalp hair loss']

    def test_synonym_parsing_newline(self):
        assert Converter.parse_synonym(
            ['"Abnormality of body height" EXACT layperson []\n'],
            'synonym',
            []
        ) == ['Abnormality of body height']
        assert Converter.parse_synonym(
            ['"Autosomal dominant type" RELATED [HPO:skoehler]\n'],
            'synonym',
            []
        ) == ['Autosomal dominant type']
        assert Converter.parse_synonym(
            ['"Scalp hair loss" EXACT layperson [ORCID:0000-0001-5889-4463]\n'],
            'synonym',
            []
        ) == ['Scalp hair loss']

    def test_synonym_parsing_r_newline(self):
        assert Converter.parse_synonym(
            ['"Abnormality of body height" EXACT layperson []\r\n'],
            'synonym',
            []
        ) == ['Abnormality of body height']
        assert Converter.parse_synonym(
            ['"Autosomal dominant type" RELATED [HPO:skoehler]\r\n'],
            'synonym',
            []
        ) == ['Autosomal dominant type']
        assert Converter.parse_synonym(
            ['"Scalp hair loss" EXACT layperson [ORCID:0000-0001-5889-4463]\r\n'],
            'synonym',
            []
        ) == ['Scalp hair loss']

    def test_synonym_parsing_errors(self):
        with self.assertRaises(IndexError) as context:
            Converter.parse_synonym(
                ['synonym: Scalp hair loss'],
                'synonym',
                []
            )
        assert 'list index out of range' == str(context.exception)

        with self.assertRaises(AttributeError) as context:
            Converter.parse_synonym([12], 'synonym', [])
        self.assertEqual(
            "'int' object has no attribute 'split'",
            str(context.exception)
        )


if __name__ == "__main__":
    unittest.main()
