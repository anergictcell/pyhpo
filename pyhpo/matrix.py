from typing import Iterable, Any, Optional, List, Union, Tuple


class Matrix:
    """
    # noqa: E501

    Poor man's implementation of a DataFrame/Matrix

    This is used to calculate similarities between HPO sets
    and is surprisingly much faster than using pandas DataFrames

    .. note::

        Pandas::

            ===== COMPARING SETS ======
            23806489 function calls (23770661 primitive calls) in 19.705 seconds

            ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            ....
            9900    0.267    0.000   19.106    0.002 set.py:318(similarity)
            9900    1.124    0.000   14.330    0.001 set.py:477(_sim_score)
            ....

        Matrix::

            ===== COMPARING SETS ======
            12870433 function calls in 6.642 seconds

            ncalls  tottime  percall  cumtime  percall filename:lineno(function)
            ....
            9900    0.048    0.000    6.424    0.001 set.py:316(similarity)
            9900    0.928    0.000    5.112    0.001 set.py:432(_sim_score)
            ....

    .. warning::

        This `Matrix` should not be used as a public interface.
        It's only used internally for calculations.

    Parameters
    ----------
    rows: int
        The number of rows in the Matrix
    cols: int
        The number of columns in the Matrix
    data: list of values, default ``None``
        A list with values to fill the Matrix.

    Attributes
    ----------
    n_rows: int
        The number of rows in the Matrix

    n_cols: int
        The number of columns in the Matrix

    rows: iterator
        Iterator over all rows

        **Example:** ::

            print(matrix)

            >>    ||   0|   1|   2|   3|
            >> =========================
            >> 0  ||  11|  12|  13|  14|
            >> 1  ||  21|  22|  23|  24|
            >> 2  ||  31|  32|  33|  34|

            for row in matrix.rows:
                print(row)

            >> [11, 12, 13, 14]
            >> [21, 22, 23, 24]
            >> [31, 32, 33, 34]

    columns: iterator
        Iterator over all columns

        **Example:** ::

            print(matrix)

            >>    ||   0|   1|   2|   3|
            >> =========================
            >> 0  ||  11|  12|  13|  14|
            >> 1  ||  21|  22|  23|  24|
            >> 2  ||  31|  32|  33|  34|

            for col in matrix.columns:
                print(col)

            >> [11, 21, 31]
            >> [12, 22, 32]
            >> [13, 23, 33]
            >> [14, 24, 34]

    """
    def __init__(
        self,
        rows: int,
        cols: int,
        data: Optional[List[Any]] = None
    ):
        self.n_rows = rows
        self.n_cols = cols
        self._data: List[Any]
        if data is None:
            self._data = [None] * rows * cols
        elif len(data) == rows * cols:
            self._data = data
        else:
            raise RuntimeError('Wrong number of data items in `data`')

    def __getitem__(self, key: Tuple[Optional[int], Optional[int]]) -> Any:
        idx = self._get_key_indicies(key)
        return self._data[idx]

    def __setitem__(
        self,
        key: Tuple[Optional[int], Optional[int]],
        val: Any
    ) -> None:
        idx = self._get_key_indicies(key)

        if isinstance(idx, int) or len(self._data[idx]) == len(val):
            self._data[idx] = val
        else:
            raise ValueError('Different length of matrix subset and values')

    def _get_key_indicies(
        self,
        key: Tuple[Optional[int], Optional[int]]
    ) -> Union[int, slice]:
        row = key[0]
        col = key[1]

        if row is None and isinstance(col, int):
            # Return one column
            return slice(
                col,
                self.n_rows * (self.n_cols) + col,
                self.n_cols
            )

        if col is None and isinstance(row, int):
            # Return one row
            return slice(
                row * self.n_cols,
                row * self.n_cols + self.n_cols,
                1
            )

        if isinstance(row, int) and isinstance(col, int):
            if row > self.n_rows - 1:
                raise RuntimeError('Invalid row number: {}'.format(row))
            if col > self.n_cols - 1:
                raise RuntimeError('Invalid column number: {}'.format(col))
            return row * self.n_cols + col

        raise RuntimeError('Invalid arguments for Matrix subset')

    @property
    def rows(self) -> Iterable[Any]:
        for x in range(self.n_rows):
            yield self[x, None]

    @property
    def columns(self) -> Iterable[Any]:
        for x in range(self.n_cols):
            yield self[None, x]

    def __str__(self) -> str:
        maxlength = max(
            [len(str(self.n_cols))] +
            [len(str(x)) for x in self._data]
        ) + 2
        idxlength = len(str(self.n_rows)) + 2

        s = ''

        s += '{}||'.format(''.rjust(idxlength))
        s += ''.join([
            '{}|'.format(str(x).rjust(maxlength))
            for x in range(self.n_cols)
        ])
        s += '\n' + '=' * len(s)

        for idx, item in enumerate(self._data):
            if idx % self.n_cols == 0:
                s += '\n{}||'.format(
                    str(int(idx/self.n_cols)).ljust(idxlength)
                )
            s += '{}|'.format(str(item).rjust(maxlength))

        return s
