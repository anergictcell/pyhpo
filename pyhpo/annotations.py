import os
import csv

from pyhpo.term import HPOTerm

FILENAMES = {
    'HPO_ONTOLOGY': 'hp.obo',
    'HPO_GENE': 'phenotype_to_genes.txt',
    'HPO_PHENO': 'phenotype.hpoa'
}


class GeneSingleton:
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
        try:
            self.id = int(columns[2])
        except TypeError:
            self.id = None
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

    def toJSON(self, verbose=False):
        res = {
            'id': self.id,
            'name': self.name,
            'symbol': self.name
        }
        if verbose:
            res['hpo'] = self.hpo

        return res

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


class GeneDict(dict):
    """
    An associative dict of all genes

    Ensures that every gene is a single GeneSingleton instance
    and no duplicate instances are generated during parsing of the
    Gen-Pheno-HPO associations.

    This class is initilized once and then the dict is accessible as
    ``annotations.Gene``.
    """
    def __init__(self):
        pass

    def get(self, identifier):
        try:
            return self[int(identifier)]
        except ValueError:
            for gene in self:
                if gene.name == identifier:
                    return gene
        except KeyError:
            pass
        return None

    def __call__(self, cols):
        gene = GeneSingleton(cols)
        if gene.id is None:
            for x in self:
                if x.name == gene.name:
                    return x
            raise RuntimeError('Invalid Gene entry without ID')
        if gene not in self:
            self[gene] = gene
        return self[gene]


class Disease:
    diseasetype = 'Undefined'
    """
    Representation of a disease

    Attributes
    ----------
    id: int
        id
    name: str
        disease name

    Parameters
    ----------
    columns: list
        [None, id, name]
    """
    def __init__(self, cols):
        self.id = int(cols[1])
        self.name = cols[2]
        self._hpo = set()

    @property
    def hpo(self):
        return self._hpo

    @hpo.setter
    def hpo(self, term):
        self._hpo.add(term)

    def toJSON(self, verbose=False):
        res = {
            'id': self.id,
            'name': self.name
        }
        if verbose:
            res['hpo'] = self.hpo

        return res

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
        return '{}(["", {}, "{}"])'.format(
            self.diseasetype,
            self.id,
            self.name
        )


class OmimDisease(Disease):
    diseasetype = 'Omim'


class OrphaDisease(Disease):
    diseasetype = 'Orpha'


class DecipherDisease(Disease):
    diseasetype = 'Decipher'


class DiseaseDict(dict):
    disease_class = None
    """
    An associative dict of all Omim Diseases

    Ensures that every Omim Disease is a single OmimDisease instance
    and no duplicate instances are generated during parsing of the
    Gen-Pheno-HPO associations.

    This class is initilized once and then the dict is accessible as
    ``annotations.Omim``.
    """
    def __init__(self):
        pass

    def get(self, identifier):
        try:
            return self[int(identifier)]
        except ValueError:
            for disease in self:
                if disease.name == identifier:
                    return disease
        except KeyError:
            pass
        return None

    def __call__(self, cols):
        disease = self.disease_class(cols)
        if disease not in self:
            self[disease] = disease
        return self[disease]


class OmimDict(DiseaseDict):
    disease_class = OmimDisease


class OrphaDict(DiseaseDict):
    disease_class = OrphaDisease


class DecipherDict(DiseaseDict):
    disease_class = DecipherDisease


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
                gene.hpo = idx
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
        negative_orpha_dict = {}
        orpha_dict = {}
        negative_decipher_dict = {}
        decipher_dict = {}

        for row in reader:
            idx = HPOTerm.id_from_string(row['HPO_ID'])
            phenotype_source, phenotype_id = row['DatabaseID'].split(':')
            qualifier = row['Qualifier']

            if phenotype_source == 'OMIM':

                # To keep backwards compatibility, we're
                # passing the OMIM details in the same order
                # as they were present in the old
                # annotation files
                pheno = Omim(
                    [0, phenotype_id, row['DiseaseName']]
                )

                pos_assoc = omim_dict
                neg_assoc = negative_omim_dict

            elif phenotype_source == 'ORPHA':
                pheno = Orpha(
                    [0, phenotype_id, row['DiseaseName']]
                )

                pos_assoc = orpha_dict
                neg_assoc = negative_orpha_dict

            elif phenotype_source == 'DECIPHER':
                pheno = Decipher(
                    [0, phenotype_id, row['DiseaseName']]
                )

                pos_assoc = decipher_dict
                neg_assoc = negative_decipher_dict

            else:
                continue

            if qualifier == 'NOT':
                if idx not in neg_assoc:
                    neg_assoc[idx] = set()
                if pheno not in neg_assoc[idx]:
                    neg_assoc[idx].add(pheno)
            if qualifier == '':
                pheno.hpo = idx
                if idx not in pos_assoc:
                    pos_assoc[idx] = set()
                if pheno not in pos_assoc[idx]:
                    pos_assoc[idx].add(pheno)

    return (
        omim_dict, negative_omim_dict,
        orpha_dict, negative_orpha_dict,
        decipher_dict, negative_decipher_dict
    )


Omim = OmimDict()
Orpha = OrphaDict()
Decipher = DecipherDict()
Gene = GeneDict()
