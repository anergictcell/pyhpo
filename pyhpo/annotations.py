import os
import csv
from typing import Any, ClassVar, Dict, Iterator, List
from typing import Optional, Set, Tuple, Union


from pyhpo import HPOTerm

FILENAMES = {
    'HPO_ONTOLOGY': 'hp.obo',
    'HPO_GENE': 'phenotype_to_genes.txt',
    'HPO_PHENO': 'phenotype.hpoa'
}


class Annotation:
    @property
    def hpo(self) -> Set[int]:
        ...

    @hpo.setter
    def hpo(self, term: int) -> None:
        ...


class GeneSingleton:
    """
    This class represents a single gene.

    .. note::

        ``GeneSingleton`` should never be initiated directly,
        but only via :class:`.GeneDict`
        to ensure that every gene is only created once.

    Attributes
    ----------
    id: int
        HGNC gene ID

    name: str
        HGNC gene synbol

    symbol: str
        HGNC gene symbol (alias of :attr:`.GeneSingleton.name`)

    hpo: set of :class:`pyhpo.term.HPOTerm`
        all HPOTerms associated to the gene

    Parameters
    ----------
    idx: int
        HGNC gene ID
    name: str
        HGNC gene synbol
    """
    def __init__(self, idx: Union[int, None], name: str) -> None:
        self.id = idx
        self.name: str = name
        self._hpo: Set[int] = set()
        self._hash = hash((
            self.id,
            self.name
        ))

    @property
    def symbol(self) -> str:
        return self.name

    @property
    def hpo(self) -> Set[int]:
        return self._hpo

    @hpo.setter
    def hpo(self, term: int) -> None:
        self._hpo.add(term)

    def toJSON(self, verbose: bool = False) -> Dict:
        """
        JSON (dict) representation of ``Gene``

        Parameters
        ----------
        verbose: bool, default: ``False``
            Return all associated HPOTerms

        Returns
        -------
        dict
            A dict with the following keys

            * **id** - The HGNC ID
            * **name** - The gene symbol
            * **symbol** - The gene symbol (same as ``name``)
            * **hpo** - (If ``verbose == True``):
              set of :class:`pyhpo.term.HPOTerm`
        """
        res = {
            'id': self.id,
            'name': self.name,
            'symbol': self.name
        }
        if verbose:
            res['hpo'] = self.hpo  # type: ignore[assignment]

        return res

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, int):
            return self.id == other

        if isinstance(other, str):
            return self.name == other

        try:
            return bool(
                (self.id and self.id == other.id) or
                (self.name and self.name == other.name)
            )
        except AttributeError:
            return False

    def __hash__(self) -> int:
        return self._hash

    def __str__(self) -> str:
        return self.name

    def __repr__(self) -> str:
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

    This class is initilized once and genes are created by calling
    the instance of GeneDict to ensure that the same gene exists only once.

    For example ::

        Gene = GeneDict()
        gba = Gene(symbol='GBA')
        ezh2 = Gene(symbol='EZH2')
        gba_2 = Gene(symbol='GBA')

        gba is ezh2
        >> False
        gba is gba_2
        >> True

    Parameters
    ----------
    cols: list, default: ``None``
        Only used for backwards compatibility reasons.
        Should have the following entries

        * None
        * None
        * HGNC-ID
        * Gene symbol

    hgncid: int
        The HGNC ID
    symbol: str
        The gene symbol (alternative to name)

    Returns
    -------
    :class:`.GeneSingleton`
    """
    def __init__(self) -> None:
        self._indicies: Dict[int, GeneSingleton] = {}
        self._names: Dict[str, GeneSingleton] = {}

    def __call__(
        self,
        cols: List = None,
        hgncid: Optional[int] = None,
        symbol: Optional[str] = None
    ) -> GeneSingleton:
        if not any([cols, hgncid, symbol]):
            raise TypeError('GeneDict requires at least one argument')

        # for backwards compatibility
        # we need to create and use this weird list
        if cols is None:
            cols = [
                None,
                None,
                hgncid,
                symbol
            ]
        name = cols[3]
        try:
            idx: int = int(cols[2])
        except TypeError:
            idx = None  # type: ignore[assignment] # desired behaviour

        try:
            return self._names[name]
        except KeyError:
            pass
        try:
            return self._indicies[idx]
        except KeyError:
            pass

        gene = GeneSingleton(idx, name)

        self[gene] = gene
        self._indicies[idx] = gene
        self._names[name] = gene

        return gene

    def clear(self) -> None:
        self._indicies.clear()
        self._names.clear()
        dict.clear(self)

    def get(
        self,
        query: Union[int, str],
        default: Any = None
    ) -> GeneSingleton:
        """
        Allows client to query for a gene by both ID and symbol.
        This method is useful for client that do not want to add new
        genes

        Parameters
        ----------
        query: int or str
            The (most likely user supplied) query.
            Can be either the HGNC-ID or the gene symbol

        Returns
        -------
        GeneSingleton
            If a gene is found, it is returned. Otherwise an Error is raised
        """
        try:
            idx: int = int(query)
            return self._indicies[idx]
        except (ValueError, KeyError):
            idx = None  # type: ignore[assignment]  # desired

        try:
            return self._names[str(query)]
        except KeyError:
            raise KeyError('No gene found for query')


class DiseaseSingleton:
    """
    This class represents a single disease.

    .. note::

        ``DiseaseSingleton`` should never be initiated directly,
        but only via the appropriate disease dictionary, e.g.
        :class:`.OmimDict` (:class:`.DiseaseDict`)
        to ensure that every disease is only created once.

    Attributes
    ----------
    id: int
        Disease ID

    name: str
        disease name

    hpo: set of :class:`pyhpo.term.HPOTerm`
        all HPOTerms associated to the disease

    Parameters
    ----------
    idx: int
        Disease ID
    name: str
        Disease name
    """
    diseasetype = 'Undefined'

    def __init__(self, idx: int, name: str) -> None:
        self.id: int = idx
        self.name: str = name
        self._hpo: Set[int] = set()
        self._hash = hash((
            self.id,
            self.diseasetype
        ))

    @property
    def hpo(self) -> Set[int]:
        return self._hpo

    @hpo.setter
    def hpo(self, term: int) -> None:
        self._hpo.add(term)

    def toJSON(self, verbose: bool = False) -> Dict:
        """
        JSON (dict) representation of ``Disease``

        Parameters
        ----------
        verbose: bool, default: ``False``
            Return all associated HPOTerms

        Returns
        -------
        dict
            A dict with the following keys

            * **id** - The Disease ID
            * **name** - The disease name
            * **hpo** - (If ``verbose == True``):
              set of :class:`pyhpo.term.HPOTerm`
        """
        res = {
            'id': self.id,
            'name': self.name
        }
        if verbose:
            res['hpo'] = self.hpo

        return res

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, int):
            return self.id == other

        if isinstance(other, str):
            return self.name == other

        try:
            return bool(
                (self.id and self.id == other.id) or
                (self.name and self.name == other.name)
            )
        except AttributeError:
            return False

    def __hash__(self) -> int:
        return self._hash

    def __str__(self) -> str:
        return str(self.name)

    def __repr__(self) -> str:
        return '{}(["", {}, "{}"])'.format(
            self.diseasetype,
            self.id,
            self.name
        )


class OmimDisease(DiseaseSingleton):
    diseasetype = 'Omim'


class OrphaDisease(DiseaseSingleton):
    diseasetype = 'Orpha'


class DecipherDisease(DiseaseSingleton):
    diseasetype = 'Decipher'


class DiseaseDict(dict):
    """
    An associative dict of all Omim Diseases

    Ensures that every Omim Disease is a single OmimDisease instance
    and no duplicate instances are generated during parsing of the
    Gen-Pheno-HPO associations.

    This class is initilized once and diseases are created by calling
    the instance of ``DiseaseDict`` to ensure that the same disease
    exists only once.

    For example ::

        Disease = OmimDict()
        gaucher = Disease(diseaseid=1)
        fabry = Disease(diseaseid=2)
        gaucher_2 = Disease(diseaseid=1)

        gaucher is fabry
        >> False
        gaucher is gaucher_2
        >> True


    Parameters
    ----------
    cols: list, default: ``None``
        Only used for backwards compatibility reasons.
        Should have the following entries

        * None
        * Disease ID
        * Disease Name

    diseaseid: int
        The Disease ID
    name: str
        The disease name

    Returns
    -------
    :class:`.DiseaseSingleton`
    """
    disease_class: ClassVar = None

    def __init__(self) -> None:
        self._indicies: Dict[int, DiseaseSingleton] = {}

    def __call__(
        self,
        cols: List = None,
        diseaseid: int = None,
        name: str = None
    ) -> DiseaseSingleton:
        assert self.disease_class

        if not any([cols, diseaseid, name]):
            raise TypeError('DiseaseDict requires at least one argument')

        # for backwards compatibility
        # we need to create and use this weird list
        if cols is None:
            cols = [
                None,
                diseaseid,
                name
            ]
        name = cols[2]
        try:
            idx: int = int(cols[1])
        except TypeError:
            idx = None  # type: ignore[assignment]

        try:
            return self._indicies[idx]
        except KeyError:
            pass

        disease = self.disease_class(idx, name)

        self[disease] = disease
        self._indicies[idx] = disease

        return disease

    def clear(self) -> None:
        self._indicies.clear()
        dict.clear(self)

    def get(
        self,
        query: Union[int, str],
        default: Any = None
    ) -> DiseaseSingleton:
        """
        Allows client to query for a disease by ID.
        This method is useful for client that do not want to add new
        diseases

        Parameters
        ----------
        query: int
            The (most likely user supplied) query for Disease ID.

        Returns
        -------
        DiseaseSingleton
            If a disease is found, it is returned. Otherwise an Error is raised
        """
        try:
            idx = int(query)
            return self._indicies[idx]
        except ValueError:
            raise ValueError('Invalid Disease ID supplied')
        except KeyError:
            raise KeyError('No disease found for query')


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
    def __init__(
        self,
        filename: Optional[str] = None,
        path: str = './'
    ) -> None:
        if filename is None:
            filename = os.path.join(path, FILENAMES['HPO_GENE'])
        self.load_from_file(filename)

    def load_from_file(self, filename: str) -> None:
        with open(filename) as fh:
            for line in fh:
                if line.startswith('#'):
                    continue
                cols = line.strip().split('\t')
                idx = HPOTerm.id_from_string(cols[0])
                if idx not in self:
                    self[idx] = set()
                gene = Gene(cols)
                gene.hpo = idx  # type: ignore[assignment]
                if gene not in self[idx]:
                    self[idx].add(gene)


def remove_outcommented_rows(
    fh: Iterator[str],
    ignorechar: str = '#'
) -> Iterator[str]:
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
        else:
            if row.startswith('#DatabaseID'):
                # The header row in phenotype.hpoa file starts with a # as well
                yield row[1:]


def parse_pheno_file(
    filename: Optional[str] = None,
    path: str = './',
    delimiter: str = '\t'
) -> Tuple[Any, ...]:
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

        negative_omim_dict: dict = {}
        omim_dict: dict = {}
        negative_orpha_dict: dict = {}
        orpha_dict: dict = {}
        negative_decipher_dict: dict = {}
        decipher_dict: dict = {}

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
                pheno.hpo = idx  # type: ignore[assignment]
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
