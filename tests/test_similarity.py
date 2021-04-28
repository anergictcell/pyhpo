print('Skipping the tests of the similarity method')
# TODO: Test that only the actual methods have been called
# and no wrong dependencies are used etc
"""
    @unittest.skip('..')
    def test_resnik(self):
        with patch.object(
            HPOTerm,
            'common_ancestors',
            return_value=[self.t1, self.t2, self.t3]
        ) as patch_ca:
            self.assertEqual(
                self.term._resnik_similarity_score('foo', 'omim'),
                3
            )
            patch_ca.assert_called_once_with('foo')
            patch_ca.reset_mock()
            self.assertEqual(
                self.term._resnik_similarity_score('bar', 'gene'),
                33
            )
            patch_ca.assert_called_once_with('bar')

    @unittest.skip('..')
    def test_lin(self):
        with patch.object(
            HPOTerm,
            '_resnik_similarity_score',
            return_value=12
        ) as patch_ca:
            self.assertEqual(
                self.t1._lin_similarity_score(self.t2, 'omim'),
                24/4
            )
            patch_ca.assert_called_once_with(self.t2, 'omim')

            patch_ca.reset_mock()
            self.assertEqual(
                self.t1._lin_similarity_score(self.t2, 'gene'),
                24/44
            )
            patch_ca.assert_called_once_with(self.t2, 'gene')

            self.t1.information_content['zero'] = 0
            self.t2.information_content['zero'] = 0
            patch_ca.reset_mock()
            self.assertEqual(
                self.t1._lin_similarity_score(self.t2, 'zero'),
                0
            )
            patch_ca.assert_called_once_with(self.t2, 'zero')

    @unittest.skip('..')
    def test_jc(self):
        with patch.object(
            HPOTerm,
            '_resnik_similarity_score',
            return_value=12
        ) as patch_ca:
            self.assertEqual(
                self.t1._jc_similarity_score(self.t2, 'omim'),
                -1/(25 - 1 - 3)
            )
            patch_ca.assert_called_once_with(self.t2, 'omim')

            patch_ca.reset_mock()
            self.assertEqual(
                self.t1._jc_similarity_score(self.t2, 'gene'),
                -1/(25 - 11 - 33)
            )
            patch_ca.assert_called_once_with(self.t2, 'gene')

            patch_ca.reset_mock()
            self.assertEqual(
                self.t1._jc_similarity_score(self.t1, 'gene'),
                1
            )
            patch_ca.assert_not_called()

    @unittest.skip('..')
    def test_jc2(self):
        with patch.object(
            HPOTerm,
            '_resnik_similarity_score',
            return_value=12
        ) as patch_ca:
            self.assertEqual(
                self.t1._jc_similarity_score_2(self.t2, 'omim'),
                1 - (1 + 3 - 24)
            )
            patch_ca.assert_called_once_with(self.t2, 'omim')

            patch_ca.reset_mock()
            self.assertEqual(
                self.t1._jc_similarity_score_2(self.t2, 'gene'),
                1 - (11 + 33 - 24)
            )
            patch_ca.assert_called_once_with(self.t2, 'gene')

            patch_ca.reset_mock()
            self.assertEqual(
                self.t1._jc_similarity_score_2(self.t1, 'gene'),
                1
            )
            patch_ca.assert_not_called()

    @unittest.skip('..')
    def test_rel(self):
        with patch.object(
            HPOTerm,
            '_resnik_similarity_score',
            side_effect=[12, 0.0001]
        ) as patch_resnik, patch.object(
            HPOTerm,
            '_lin_similarity_score',
            return_value=22
        ) as patch_lin:
            self.assertGreater(
                self.t1._rel_similarity_score(self.t2, 'omim'),
                20
            )
            patch_resnik.assert_called_once_with(self.t2, 'omim')
            patch_lin.assert_called_once_with(self.t2, 'omim')
            patch_resnik.reset_mock()

            self.assertLess(
                self.t1._rel_similarity_score(self.t2, 'omim'),
                0.01
            )
            patch_resnik.assert_called_once_with(self.t2, 'omim')

    @unittest.skip('..')
    def test_ic(self):
        with patch.object(
            HPOTerm,
            '_resnik_similarity_score',
            side_effect=[12, 0.0001]
        ) as patch_resnik, patch.object(
            HPOTerm,
            '_lin_similarity_score',
            return_value=22
        ) as patch_lin:
            self.assertGreater(
                self.t1._ic_similarity_score(self.t2, 'omim'),
                20
            )
            patch_resnik.assert_called_once_with(self.t2, 'omim')
            patch_lin.assert_called_once_with(self.t2, 'omim')
            patch_resnik.reset_mock()

            self.assertLess(
                self.t1._ic_similarity_score(self.t2, 'omim'),
                0.01
            )
            patch_resnik.assert_called_once_with(self.t2, 'omim')

    @unittest.skip('..')
    def test_graphic(self):
        with patch.object(
            HPOTerm,
            'common_ancestors',
            return_value=set([self.t2])
        ) as patch_ca:

            self.t1._all_parents = set([self.t1, self.t2])
            self.t2._all_parents = set([self.t2, self.t3])

            self.assertEqual(
                self.t1._graph_ic_similarity_score(self.t2, 'omim'),
                3 / 6
            )
            patch_ca.assert_called_once_with(self.t2)

            patch_ca.reset_mock()
            self.assertEqual(
                self.t1._graph_ic_similarity_score(self.t2, 'gene'),
                33 / 66
            )
            patch_ca.assert_called_once_with(self.t2)

            patch_ca.reset_mock()
            self.t1.information_content['zero'] = 0
            self.t2.information_content['zero'] = 0
            self.t3.information_content['zero'] = 0
            self.assertEqual(
                self.t1._graph_ic_similarity_score(self.t2, 'zero'),
                0
            )
            patch_ca.assert_called_once_with(self.t2)

    @unittest.skip('..')
    def test_dist(self):
        with patch.object(
            HPOTerm,
            'path_to_other',
            side_effect=[[0, None], [1, None], [3, None]]
        ) as patch_pto:

            self.assertEqual(
                self.t1._dist_similarity_score(self.t2),
                1
            )

            self.assertEqual(
                self.t1._dist_similarity_score(self.t2),
                0.5
            )

            self.assertEqual(
                self.t1._dist_similarity_score(self.t2),
                0.25
            )

            patch_pto.assert_has_calls([
                call(self.t2),
                call(self.t2),
                call(self.t2)
            ])

"""