import unittest

from pyhpo.matrix import Matrix


class MatrixTest(unittest.TestCase):
    def test_init(self):
        x = Matrix(2, 3)
        self.assertEqual(
            x._data,
            [None] * 6
        )
        self.assertEqual(
            x.n_rows,
            2
        )
        self.assertEqual(
            x.n_cols,
            3
        )

    def test_init_error_checking(self):
        with self.assertRaises(RuntimeError) as context:
            a = Matrix(2, 4, [1, 2, 3])  # noqa: F841
        self.assertEqual(
            'Wrong number of data items in `data`',
            str(context.exception)
        )

    def test_string(self):
        a = Matrix(2, 3, range(6))
        self.assertEqual(
            str(a),
            '   ||  0|  1|  2|\n=================\n0  ||  0|  1|  2|\n1  ||  3|  4|  5|'  # noqa: E501
        )


class MatrixReadingTests(unittest.TestCase):
    def setUp(self):
        """
           ||   0|   1|   2|   3|
        =========================
        0  ||  11|  12|  13|  14|
        1  ||  21|  22|  23|  24|
        2  ||  31|  32|  33|  34|
        """
        self.a = Matrix(
            3,
            4,
            list(range(11, 15)) +
            list(range(21, 25)) +
            list(range(31, 35))
        )
        self.singlecol = Matrix(3, 1, [1, 2, 3])
        self.singlerow = Matrix(1, 3, [1, 2, 3])

    def test_single_field_access(self):
        a = self.a
        self.assertEqual(a[0, 0], 11)
        self.assertEqual(a[2, 1], 32)
        self.assertEqual(a[1, 2], 23)

    def test_lengths(self):
        a = self.a
        self.assertEqual(
            len(list(a.rows)),
            3
        )
        self.assertEqual(
            len(list(a.columns)),
            4
        )

    def test_row_reading(self):
        a = self.a
        self.assertEqual(
            list(a.rows)[0],
            [11, 12, 13, 14]
        )
        self.assertEqual(
            list(a.rows)[1],
            [21, 22, 23, 24]
        )
        self.assertEqual(
            list(a.rows)[2],
            [31, 32, 33, 34]
        )

        b = self.singlecol
        self.assertEqual(
            list(b.rows)[0],
            [1]
        )
        self.assertEqual(
            list(b.rows)[1],
            [2]
        )
        self.assertEqual(
            list(b.rows)[2],
            [3]
        )

        c = self.singlerow
        self.assertEqual(
            list(c.rows),
            [[1, 2, 3]]
        )

    def test_column_reading(self):
        a = self.a
        self.assertEqual(
            list(a.columns)[0],
            [11, 21, 31]
        )
        self.assertEqual(
            list(a.columns)[1],
            [12, 22, 32]
        )
        self.assertEqual(
            list(a.columns)[3],
            [14, 24, 34]
        )

        b = self.singlecol
        self.assertEqual(
            list(b.columns),
            [[1, 2, 3]]
        )

        c = self.singlerow
        self.assertEqual(
            list(c.columns)[0],
            [1]
        )
        self.assertEqual(
            list(c.columns)[1],
            [2]
        )
        self.assertEqual(
            list(c.columns)[2],
            [3]
        )

    def test_errors(self):
        a = self.a

        with self.assertRaises(RuntimeError) as context:
            a[3, 1]
        self.assertEqual(
            'Invalid row number: 3',
            str(context.exception)
        )

        with self.assertRaises(RuntimeError) as context:
            a[1, 7]
        self.assertEqual(
            'Invalid column number: 7',
            str(context.exception)
        )


class MatrixEditingTests(unittest.TestCase):
    def setUp(self):
        """
           ||   0|   1|   2|   3|
        =========================
        0  ||  11|  12|  13|  14|
        1  ||  21|  22|  23|  24|
        2  ||  31|  32|  33|  34|
        """

        # a will be edited
        self.a = Matrix(
            3,
            4,
            list(range(11, 15)) +
            list(range(21, 25)) +
            list(range(31, 35))
        )

        # b will be used as reference
        self.b = Matrix(
            3,
            4,
            list(range(11, 15)) +
            list(range(21, 25)) +
            list(range(31, 35))
        )

    def test_single_field_edits(self):
        a = self.a
        b = self.b
        a[2, 3] = 111
        self.assertEqual(
            a[2, 3],
            111
        )
        self.assertEqual(
            a._data[11],
            111
        )
        self.assertEqual(
            a[2, None],
            [31, 32, 33, 111]
        )
        self.assertEqual(
            a[None, 3],
            [14, 24, 111]
        )
        self.assertEqual(
            list(a.rows),
            [
                b[0, None],
                b[1, None],
                list(range(31, 34)) + [111]
            ]
        )

    def test_row_edits(self):
        a = self.a
        b = self.b
        a[1, None] = [111, 112, 113, 114]
        self.assertEqual(
            list(a.rows),
            [
                b[0, None],
                [111, 112, 113, 114],
                b[2, None]
            ]
        )
        self.assertEqual(
            a[None, 3],
            [14, 114, 34]
        )

    def test_column_edits(self):
        a = self.a
        b = self.b
        a[None, 2] = [111, 112, 113]
        self.assertEqual(
            list(a.columns),
            [
                b[None, 0],
                b[None, 1],
                [111, 112, 113],
                b[None, 3]
            ]
        )
        self.assertEqual(
            a[1, None],
            [21, 22, 112, 24]
        )

    def test_errors(self):
        a = self.a
        with self.assertRaises(ValueError) as context:
            a[None, 2] = [111, 112, 113, 114]
        self.assertEqual(
            'Different length of matrix subset and values',
            str(context.exception)
        )

        with self.assertRaises(ValueError) as context:
            a[None, 2] = [111, 112]
        self.assertEqual(
            'Different length of matrix subset and values',
            str(context.exception)
        )

        with self.assertRaises(ValueError) as context:
            a[2, None] = [111, 112, 113, 114, 115]
        self.assertEqual(
            'Different length of matrix subset and values',
            str(context.exception)
        )

        with self.assertRaises(ValueError) as context:
            a[2, None] = [111, 112, 113]
        self.assertEqual(
            'Different length of matrix subset and values',
            str(context.exception)
        )

        with self.assertRaises(RuntimeError) as context:
            a[None, None]
        self.assertEqual(
            'Invalid arguments for Matrix subset',
            str(context.exception)
        )

        with self.assertRaises(RuntimeError) as context:
            a['foo', None]
        self.assertEqual(
            'Invalid arguments for Matrix subset',
            str(context.exception)
        )

        with self.assertRaises(RuntimeError) as context:
            a[None, 'foo']
        self.assertEqual(
            'Invalid arguments for Matrix subset',
            str(context.exception)
        )

        with self.assertRaises(RuntimeError) as context:
            a['bar', 'foo']
        self.assertEqual(
            'Invalid arguments for Matrix subset',
            str(context.exception)
        )

        with self.assertRaises(RuntimeError) as context:
            a['foo', 2]
        self.assertEqual(
            'Invalid arguments for Matrix subset',
            str(context.exception)
        )

        with self.assertRaises(RuntimeError) as context:
            a[2, 'foo']
        self.assertEqual(
            'Invalid arguments for Matrix subset',
            str(context.exception)
        )
