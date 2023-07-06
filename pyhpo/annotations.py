from typing import Any, ClassVar, Dict, Set, Union

from pydantic import BaseModel


class Annotation(BaseModel):
    id: int
    name: str
    hpo: Set[int] = set()
    _hash: int
    _json_keys = set(['id', 'name'])

    def __init__(self, **kwargs: Union[int, str]) -> None:
        super().__init__(**kwargs)
        self._hash = hash((self.id, self.name))

    def toJSON(self, verbose: bool = False) -> dict:
        """
        Backwards compatibility method
        BaseModel include ``.json`` method

        Parameters
        ----------
        verbose: bool, default: ``False``
            Return all associated HPOTerms

        Returns
        -------
        dict
            A dict with the following keys
            (additional keys might be present, depending on the class)

            * **id** - The HGNC ID
            * **name** - The gene symbol
            * **hpo** - (If ``verbose == True``):
              set of :class:`pyhpo.term.HPOTerm`
        """
        res = {}
        for key in self._json_keys:
            res[key] = self.__getattribute__(key)
        if verbose:
            res['hpo'] = self.hpo
        return res

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, int):
            return self.id == other

        if isinstance(other, str):
            return self.name == other

        return hash(self) == hash(other)

    def __hash__(self) -> int:
        return self._hash

    def __str__(self) -> str:
        return self.name


class GeneSingleton(Annotation):
    """
    An instance of ``GeneSingleton`` represents a single gene.

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
    id: int
        HGNC gene ID
    name: str
        HGNC gene synbol
    """
    _json_keys = set(['id', 'name', 'symbol'])

    @property
    def symbol(self) -> str:
        return self.name


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
        hgncid: int,
        symbol: str
    ) -> GeneSingleton:

        try:
            return self._names[symbol]
        except KeyError:
            pass
        try:
            return self._indicies[hgncid]
        except KeyError:
            pass

        gene = GeneSingleton(id=hgncid, name=symbol)  # type: ignore

        self[gene] = gene
        self._indicies[hgncid] = gene
        self._names[symbol] = gene

        return gene

    def clear(self) -> None:
        """
        Removes all Genes to start with blank state.

        There are almot zero use-cases to ever call this method in
        client-side code. If you use code, that modifies the ``GeneDict``
        class a lot, you might use this. Under normal circumstences,
        this should not be needed.

        Currently, the primary use case is to clean up the state for
        unittests.
        """
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


class DiseaseSingleton(Annotation):
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
    negative_hpo: set of :class:`pyhpo.term.HPOTerm`
        HPOTerms not associated to the disease

    Parameters
    ----------
    id: int
        Disease ID
    name: str
        Disease name
    """
    diseasetype: str = 'Undefined'
    negative_hpo: Set[int] = set()


class OmimDisease(DiseaseSingleton):
    diseasetype: str = 'Omim'


class OrphaDisease(DiseaseSingleton):
    diseasetype: str = 'Orpha'


class DecipherDisease(DiseaseSingleton):
    diseasetype: str = 'Decipher'


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
        diseaseid: int,
        name: str
    ) -> DiseaseSingleton:

        assert self.disease_class
        try:
            return self._indicies[diseaseid]
        except KeyError:
            pass

        disease: DiseaseSingleton = self.disease_class(id=diseaseid, name=name)

        self[disease] = disease
        self._indicies[diseaseid] = disease

        return disease

    def clear(self) -> None:
        """
        Removes all Diseases to start with blank state.

        There are almot zero use-cases to ever call this method in
        client-side code. If you use code, that modifies the ``DiseaseDict``
        class a lot, you might use this. Under normal circumstences,
        this should not be needed.

        Currently, the primary use case is to clean up the state for
        unittests.
        """
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


Omim = OmimDict()
Orpha = OrphaDict()
Decipher = DecipherDict()
Gene = GeneDict()
