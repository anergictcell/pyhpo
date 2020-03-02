import os
import csv

from pyhpo.term import HPOTerm

FILENAMES = {
    'HPO_ONTOLOGY': 'hp.obo',
    'HPO_GENE': 'phenotype_to_genes.txt',
    'HPO_PHENO': 'phenotype.hpoa'
}


class Gene:
    """
    Representation of a Gene

    Attributes
    ----------
    id: int
        HGNC id
    name: str
        HGNC gene synbol
    symbol: str
        HGNC gene symbol (alias of ``name``)

    Parameters
    ----------
    columns: list
        [None, None, id, name]
    """
    def __init__(self, columns):
        self.id = int(columns[2])
        self.name = columns[3]
        self._hpo = set()

    @property
    def symbol(self):
        return self.name

    @property
    def hpo(self):
        return self._hpo

    @hpo.setter
    def hpo(self, term):
        self._hpo.add(term)

    def __eq__(self, other):
        if isinstance(other, int):
            return self.id == other

        if isinstance(other, str):
            return self.id == other or self.name == other

        try:
            return self.id == other.id
        except AttributeError:
            return False

        return False

    def __hash__(self):
        return self.id

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Gene(["", "", {}, "{}"])'.format(
            self.id,
            self.name
        )


class Omim:
    """
    Representation of an OMIM disease

    Attributes
    ----------
    id: int
        OMIM id
    name: str
        OMIM disease name

    Parameters
    ----------
    columns: list
        [None, id, name]
    """
    def __init__(self, cols):
        self.id = int(cols[1])
        self.name = cols[2]
        self._hpo = set

    @property
    def hpo(self):
        return self._hpo

    @hpo.setter
    def hpo(self, term):
        self._hpo.add(term)

    def __eq__(self, other):
        if isinstance(other, int):
            return self.id == other

        if isinstance(other, str):
            return self.id == other or self.name == other

        try:
            return self.id == other.id
        except AttributeError:
            return False

        return False

    def __hash__(self):
        return self.id

    def __str__(self):
        return self.name

    def __repr__(self):
        return 'Omim(["", {}, "{}"])'.format(
            self.id,
            self.name
        )


class HPO_Gene(dict):
    """
    Associative ``dict`` to link an HPO term to a :class:`.Gene`

    Parameters
    ----------
    filename: str
        Filename of HPO-Gene association file.
        Defaults to filename from HPO
    path: str
        Path to data files.
        Defaults to './'
    """
    def __init__(self, filename=None, path='./'):
        if filename is None:
            filename = os.path.join(path, FILENAMES['HPO_GENE'])
        self.load_from_file(filename)

    def load_from_file(self, filename):
        with open(filename) as fh:
            for line in fh:
                if line.startswith('#'):
                    continue
                cols = line.strip().split('\t')
                idx = HPOTerm.id_from_string(cols[0])
                if idx not in self:
                    self[idx] = set()
                gene = Gene(cols)
                if gene not in self[idx]:
                    self[idx].add(gene)


def remove_outcommented_rows(fh, ignorechar='#'):
    """
    Removes all rows from a filereader object that start
    with a comment character

    Parameters
    ----------
    fh: iterator
        any object which supports the iterator protocol and
        returns a string each time its __next__() method is
        called — file objects and list objects are both suitable

    ignorechar: str, defaults: ``#``
        All lines starting with this character will be ignored

    Yields
    ------
    row: str
        One row of the ``fh`` iterator
    """
    for row in fh:
        if row[0:len(ignorechar)] != ignorechar:
            yield row


def parse_pheno_file(filename=None, path='./', delimiter='\t'):
    """
    Parses OMIM-HPO assoation file and generates a positive
    and negative annotation dictionary

    Parameters
    ----------
    filename: str
        Filename of HPO-Gene association file.
        Defaults to filename from HPO
    path: str
        Path to data files.
        Defaults to './'

    Returns
    -------
    omim_dict: dict
        Dictionary containing all HPO-OMIM associations.
        HPO-ID is the key
    negative_omim_dict: dict
        Dictionary containing all negative HPO-OMIM associations.
        HPO-ID is the key
    """
    if filename is None:
        filename = os.path.join(path, FILENAMES['HPO_PHENO'])

    with open(filename) as fh:
        reader = csv.DictReader(
            remove_outcommented_rows(fh),
            delimiter=delimiter
        )

        negative_omim_dict = {}
        omim_dict = {}

        for row in reader:
            idx = HPOTerm.id_from_string(row['HPO_ID'])
            if row['DatabaseID'][0:4] == 'OMIM':

                # To keep backwards compatibility, we're
                # passing the OMIM details in the same order
                # as they were present in the old
                # annotation files
                omim_id = row['DatabaseID'].split(':')[1]
                omim = Omim(
                    [0, omim_id, row['DiseaseName']]
                )

                if row['Qualifier'] == 'NOT':
                    if idx not in negative_omim_dict:
                        negative_omim_dict[idx] = set()
                    if omim not in negative_omim_dict[idx]:
                        negative_omim_dict[idx].add(omim)
                if row['Qualifier'] == '':
                    if idx not in omim_dict:
                        omim_dict[idx] = set()
                    if omim not in omim_dict[idx]:
                        omim_dict[idx].add(omim)

    return (omim_dict, negative_omim_dict)
