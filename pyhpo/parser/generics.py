"""
Generic functions required for handling HPOTerms
They used to be part of HPOTerm, but refactored out to
have a leander HPOTerm class
"""
from typing import Iterator


def id_from_string(hpo_string: str) -> int:
    """
    Formats the HPO-type Term-ID into an integer id

    Parameters
    ----------
    hpo_string:
        HPO term ID.

        (e.g.: HP:000001)

    Returns
    -------
    int
        Integer representation of provided HPO ID

        (e.g.: 1)

    """
    idx = hpo_string.split('!')[0].strip()
    return int(idx.split(':')[1].strip())


def remove_outcommented_rows(
    fh: Iterator[str],
    ignorechar: str = '#'
) -> Iterator[str]:
    """
    Removes all rows from a filereader object that start
    with a comment character

    Parameters
    ----------
    fh:
        any object which supports the iterator protocol and
        returns a string each time its __next__() method is
        called — file objects and list objects are both suitable

    ignorechar:
        All lines starting with this character(s) will be ignored

    Yields
    ------
    row: str
        One row of the ``fh`` iterator
    """
    len_check = len(ignorechar)
    for row in fh:
        if row[0:len_check] != ignorechar:
            yield row
