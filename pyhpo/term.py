from operator import or_
from functools import reduce, lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple

from pydantic import BaseModel, Field
from backports.cached_property import cached_property

from pyhpo.config import MODIFIER_IDS
from pyhpo.similarity import SimScore
from pyhpo.annotations import GeneSingleton
from pyhpo.annotations import OmimDisease, DecipherDisease, OrphaDisease
from pyhpo.parser.generics import id_from_string


class InformationContent(BaseModel):
    """
    InformationContent contains automatically calculated IC based on
    direct/indirect associations with genes, omim, orpha and decipher.
    IC instances are created automatically and accessed through
    :class:`pyhpo.term.HPOTerm` instances.

    Users can also register and calculate custom IC scores via
    :func:`pyhpo.term.InformationContent.set_custom`.
    """
    gene: float = 0.0  # Gene based IC
    omim: float = 0.0  # OMIM based IC
    orpha: float = 0.0  # OrphaNet based IC
    decipher: float = 0.0  # Decipher based IC
    custom: Dict[str, float] = Field(default_factory=dict)

    def __getitem__(self, key: str) -> float:
        """
        The IC is frequently accessed dynamically. e.g. in PyhPOAPI the
        kind of IC is specified in the query (omim / gene)
        Due to this, a dynamic access method is provided

        .. code-block:: python

            ic_kind = 'omim'
            term.information.content[ic_kind]

        """
        try:
            return float(self.__getattribute__(key))
        except AttributeError as err:
            if key in self.custom:
                return self.custom[key]
            else:
                raise AttributeError from err

    def set_custom(self, key: str, value: float) -> None:
        """
        Set the IC of a custom score

        Parameters
        ----------
        key: str
            The name of the information-content metric
        value: float
            The actual information content


        **Example:** ::

            for term in Ontology:
                # For some reason, you want to base the information content
                # on the depths of the Term in the ontology
                term.setcustom('depth',  term.shortest_path_to_root())

            # and now calculate similarity of two sets
            my_similarity = term_set_1.similarity(term_set_2, kind='depth')

        """
        self.custom[key] = value


class HPOTerm(BaseModel):
    """
    An HPOTerm instance can be build solely by itself,
    without knowledge of the actual Ontology. This is not recommended
    because it would miss all ontology features, such as parents, children,
    associated genes and diseaases etc.

    An HPOTerm instance should always be derived from the :class:`pyhpo.Ontology`
    """

    ###
    # Always present and mandatory
    ###

    id: str
    """
    The HPO identifier, e.g. ``HP:0000118``
    """

    name: str
    """
    The name of the HPO term, e.g. ``Abnormal axial skeleton morphology``
    """

    ###
    # Mandatory, calculated during initialization
    ###

    index: int
    """
    The integer representation of the HPO identifier
    """

    _hash: int

    ###
    # Mandatory for HPOTerm, but not always present in input
    ###

    comment: str = ''
    """
    The comment from the OBO source file
    """

    definition: str = ''
    """
    The definition from the OBO source file
    """

    _is_a: List[str] = []
    synonym: List[str] = []
    """
    A list of synonymous names for the term
    """

    xref: List[str] = []
    alt_id: List[str] = []

    ###
    # Special logic for some obsolete terms
    ###

    is_obsolete: bool = False
    replaced_by: Optional[str] = None
    consider: List[str] = []

    ###
    # Computed once all HPO Terms are present in the Ontology
    ###

    parents: Set['HPOTerm'] = set()
    """
    A set of all direct parent terms
    """

    children: Set['HPOTerm'] = set()
    """
    A set of all direct child terms
    """

    genes: Set[GeneSingleton] = set()
    """
    A set of all associated genes. Associated genes are inversely inherited from
    child terms as well
    """

    omim_diseases: Set[OmimDisease] = set()
    """
    A set of all associated Omim diseases. Associated diseases are inversely inherited from
    child terms as well
    """

    omim_excluded_diseases: Set[OmimDisease] = set()
    """
    A set of all explicitly non-associated Omim diseases. Non-associated diseases are inherited from
    parent terms as well
    """

    orpha_diseases: Set[OrphaDisease] = set()
    """
    A set of all associated Orpha diseases. Associated diseases are inversely inherited from
    child terms as well
    """

    orpha_excluded_diseases: Set[OrphaDisease] = set()
    """
    A set of all explicitly non-associated Orpha diseases. Non-associated diseases are inherited from
    parent terms as well
    """

    decipher_diseases: Set[DecipherDisease] = set()
    """
    A set of all associated Decipher diseases. Associated diseases are inversely inherited from
    child terms as well
    """

    decipher_excluded_diseases: Set[DecipherDisease] = set()
    """
    A set of all explicitly non-associated Decipher diseases. Non-associated diseases are inherited from
    parent terms as well
    """

    information_content: InformationContent = InformationContent()
    """
    The :class:`.InformationContent` of the HPO term.
    Multiple kinds of IC are automatically calculated,
    others can be manually calculated.
    """

    def __init__(self, **kwargs) -> None:  # type: ignore
        kwargs['index'] = id_from_string(kwargs['id'])
        super().__init__(**kwargs)
        self._hash = hash((
            self.index,
            self.name
        ))
        self._is_a = kwargs.get('is_a', [])

    @cached_property
    def all_parents(self) -> Set['HPOTerm']:
        hierarchy_set = reduce(
                or_,
                [set(path) for path in self.hierarchy]
            )
        hierarchy_set.remove(self)
        return hierarchy_set

    @cached_property
    def hierarchy(self) -> Tuple[Tuple['HPOTerm', ...], ...]:
        """
        Calculates all paths from current term to Root term
        and returns each path as a Tuple of HPOTerms

        .. note::

            This function is expensive. To ensure better performance, the
            result is cached and all subsequent calls utilize the cache. Don't
            call ``hierarchy`` before the Ontology is fully built with all
            items.

        Returns
        -------
        tuple of tuple of :class:`.HPOTerm` s
            Tuple of paths. Each path is another tuple made up of HPOTerms
        """
        if not self.parents:
            return ((self,),)

        paths: List[Tuple['HPOTerm', ...]] = []
        for parent in self.parents:
            for path in parent.hierarchy:
                paths.append((self,) + path)

        return tuple(paths)

    @cached_property
    def is_modifier(self) -> bool:
        return int(self) in MODIFIER_IDS or bool(
            MODIFIER_IDS & {int(x) for x in self.all_parents}
        )

    def parent_ids(self) -> List[int]:
        return [
            id_from_string(item) for item in self._is_a
        ]

    def parent_of(self, other: 'HPOTerm') -> bool:
        """
        Checks if ``self`` is a direct or indirect parent of ``other``.

        Parameters
        ----------
        other: :class:`.HPOTerm`
            HPOTerm to check for lineage dependency

        Returns
        -------
        bool
            Is the HPOTerm a direct or indirect parent of another HPOTerms
        """
        return other.child_of(self)

    def child_of(self, other: 'HPOTerm') -> bool:
        """
        Checks if ``self`` is a direct or indirect child of ``other``.

        Parameters
        ----------
        other: :class:`.HPOTerm`
            HPOTerm to check for lineage dependency

        Returns
        -------
        bool
            Is the HPOTerm a direct or indirect child of another HPOTerms
        """
        if self == other:
            raise RuntimeError('An HPO term cannot be parent/child of itself')

        return other in self.all_parents

    def common_ancestors(self, other: 'HPOTerm') -> Set['HPOTerm']:
        """
        Identifies all common ancestors
        of two HPO terms

        Parameters
        ----------
        other: :class:`.HPOTerm`
            Target HPO term for path finding

        Returns
        -------
        set
            Set of common ancestor HPOTerms
        """

        # Return the intersection of all ancestors of self and other.
        # Consider the following edge cases:
        # - self is in other.all_parents
        # - other is in self.all_parents
        # To account for these edge cases,
        # we first add self to self.all_parents
        # and other to other.all_parents
        self_ancestors: Set['HPOTerm'] = (
            self.all_parents | set([self])
        )
        other_ancestors: Set['HPOTerm'] = (
            other.all_parents | set([other])
        )
        return self_ancestors & other_ancestors

    def longest_path_to_root(self) -> int:
        """
        Calculates the longest path to root

        Returns
        -------
        int
            Maximum number of nodes until the root HPOTerm
        """
        return max([
            len(h)-1 for h in self.hierarchy
        ])

    def shortest_path_to_root(self) -> int:
        """
        Calculates the shortest path to root

        Returns
        -------
        int
            Minimum number of nodes until the root HPOTerm
        """
        return min([
            len(h)-1 for h in self.hierarchy
        ])

    def shortest_path_to_parent(
        self,
        other: 'HPOTerm'
    ) -> Tuple[int, Tuple['HPOTerm', ...]]:
        """
        Calculates the shortest path to another HPO Term

        Parameters
        ----------
        other: HPOTerm
            parent HPOTerm instance

        Returns
        -------
        int
            Minimum number of nodes until the specified HPOTerm

            (float('inf') if ``other`` is not a parent.)
        tuple
            Tuple of all HPOTerm instances on the path

            (``None`` if ``other`` is not a parent)
        """
        if other not in self.all_parents and self != other:
            raise RuntimeError(
                f'{other.id} is not a parent of {self.id}'
            )
        return_tuples: List[Tuple[int, Tuple['HPOTerm', ...]]] = []
        for path in self.hierarchy:
            try:
                i = path.index(other)
                return_tuples.append((i, path[:i+1]))
            except ValueError:
                pass

        try:
            return sorted(
                return_tuples,
                key=lambda x: x[0]
            )[0]
        except IndexError as err:
            raise RuntimeError(
                f'Unable to determine path to parent term {other.name}'
            ) from err

    def longest_path_to_bottom(self, level: int = 0) -> int:
        """
        Calculates how far the most distant child is apart

        Parameters
        ----------
        level: int
            Offset level to indicate for calculation
            Default: 0

        Returns
        -------
        int:
            Number of steps to most distant child

        """
        if len(self.children):
            return max([
                child.longest_path_to_bottom(level + 1)
                for child in self.children
            ])
        else:
            return level

    def path_to_other(
        self,
        other: 'HPOTerm'
    ) -> Tuple[int, Tuple['HPOTerm', ...], int, int]:
        """
        Identifies the shortest connection between
        two HPO terms

        Parameters
        ----------
        other: HPOTerm
            Target HPO term for path finding

        Returns
        -------
        int
            Length of path
        tuple
            Tuple of HPOTerms in the path
        int
            Number of steps from term-1 to the common parent
        int
            Number of steps from term-2 to the common parent

        """
        common = self.common_ancestors(other)

        paths = []
        for term in common:
            path1 = self.shortest_path_to_parent(term)
            path2 = other.shortest_path_to_parent(term)

            total_path = path1[1] + tuple(reversed(path2[1]))[1:]
            paths.append((
                int(path1[0] + path2[0]),
                total_path,
                int(path1[0]),
                int(path2[0])
            ))
        return sorted(paths, key=lambda x: x[0])[0]

    def count_parents(self) -> int:
        """
        Calculates total number of ancestral HPO Terms

        Returns
        -------
        int
            The number of all ancestral HPO Terms
        """
        return sum([
            parent.count_parents() + 1
            for parent in self.parents
        ])

    def similarity_score(
        self,
        other: 'HPOTerm',
        kind: Optional[str] = None,
        method: Optional[str] = None
    ) -> float:
        """
        Calculate the similarity between this and another HPO-Term
        It uses :class:`pyhpo.similarity.base._Similarity` underneath

        Parameters
        ----------
        other: `HPOTerm`
            Other HPO term to compare similarity to

        kind: str, default ``''``
            Which kind of information content should be calculated.
            Default option is defined in `pyhpo.similarity.base._Similarity`

            Available options:

            * **omim**
            * **orpha**
            * **decipher**
            * **gene**

        method: string, default ``''``
            The method to use to calculate the similarity.
            Default option is defined in `pyhpo.similarity.base._Similarity`

            Available options:

            * **resnik** - Resnik P, Proceedings of the 14th IJCAI, (1995)
            * **lin** - Lin D, Proceedings of the 15th ICML, (1998)
            * **jc** - Jiang J, Conrath D, ROCLING X, (1997)
              Implementation according to R source code
            * **jc2** - Jiang J, Conrath D, ROCLING X, (1997)
              Implementation according to paper from R ``hposim`` library
              Deng Y, et. al., PLoS One, (2015)
            * **rel** - Relevance measure - Schlicker A, et.al.,
              BMC Bioinformatics, (2006)
            * **ic** - Information coefficient - Li B, et. al., arXiv, (2010)
            * **graphic** - Graph based Information coefficient -
              Deng Y, et. al., PLoS One, (2015)
            * **dist** - Distance between terms
            * Additional methods can be registered separately (
              see :class::`pyhpo.similarity.base._Similarity`)

        Raises
        ------
        RuntimeError
            The specified ``method`` does not exist
        NotImplementedError
            This error can only occur with custom Similarity-Score
            methods that do not have a ``similarity`` method defined.
        AttributeError
            The information content for ``kind`` does not exist
        """
        return SimScore(self, other, kind, method)

    @lru_cache(maxsize=128)
    def cached_similarity_score(
        self,
        other: 'HPOTerm',
        kind: str = '',
        method: str = ''
    ) -> float:
        """
        This is a LRU-chached alias of
        :func:`pyhpo.term.HPOTerm.similarity_score`
        """
        return self.similarity_score(other, kind, method)

    def toJSON(
        self,
        verbose: bool = False
    ) -> dict:
        """
        Creates a JSON-like object of the HPOTerm

        Parameters
        ----------
        verbose: bool, default ``False``
            Include extra properties

        Returns
        -------
        dict
            A dictionary with the main properties of the HPOTerm


        **Example:** ::

            >>> terms[2].toJSON()
            {
                'name': 'Abnormality of body height',
                'id': 'HP:0000002',
                'int': 2
            }

            >>> terms[2].toJSON(verbose=True)
            {
                'name': 'Abnormality of body height',
                'synonym': ['Abnormality of body height'],
                'comment': None,
                'def': '"Deviation from the norm of height with respect [...]',
                'xref': ['UMLS:C4025901'],
                'is_a': ['HP:0001507 ! Growth abnormality'],
                'id': 'HP:0000002',
                'int': 2
            }

        """
        res = {
            'int': int(self),
            'id': self.id,
            'name': self.name
        }

        if verbose:
            res['definition'] = self.definition
            res['comment'] = self.comment
            res['synonym'] = self.synonym
            res['xref'] = self.xref
            res['is_a'] = self._is_a
            res['ic'] = self.information_content.model_dump()

        return res

    def to_obo(self) -> str:
        raise NotImplementedError('Method is missing')

    def __hash__(self) -> int:
        """
        The hash is precalcuated during initialization
        """
        return self._hash

    def __int__(self) -> int:
        return self.index

    def __eq__(self, t2: Any) -> bool:
        return hash(self) == hash(t2) and isinstance(t2, HPOTerm)

    def __lt__(self, other: Any) -> bool:
        return int(self) < int(other)

    def __str__(self) -> str:
        return '{} | {}'.format(self.id, self.name)

    def __repr__(self) -> str:
        return (
            f"HPOTerm(id='{self.id}', name='{self.name}', "
            f"is_a={self._is_a})"
        )

    class Config:
        arbitrary_types_allowed = True
        ignored_types = (cached_property, )
