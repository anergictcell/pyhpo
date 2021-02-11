import warnings
import math
from typing import List, Set, Tuple, Optional, Union, Dict, Any

import pyhpo


TRUTH = ('true', 't', 'yes', 'y', '1')


class HPOAnnotation:
    """
    Guarantees proper type annotations and backwards compatibility of
    :func:`pyhpo.term.HPOTerm._annotations
    Even though it's a class, it provides mappings of dict, such
    ``__getitem__``, ``setitem__`` etc.
    Those methods will be removed eventually and should not be used.
    After all, it's a private method anyway
    """
    def __init__(self) -> None:
        self.items: Set[Any] = set()
        self.cached: bool = False

    def __getitem__(self, key: int) -> Union[Set[Any], bool]:
        """
        Backwards compatibility of ``dict`` features
        """
        key = int(key)
        if key == 0:
            return self.items
        elif key == 1:
            return self.cached
        else:
            raise KeyError(f'Invalid key for HPO Term annotation {key}')

    def __setitem__(self, key: int, value: Any) -> None:
        """
        Backwards compatibility of ``dict`` features
        """
        key = int(key)
        if key == 0:
            self.items = value
        elif key == 1:
            self.cached = value
        else:
            raise KeyError(f'Invalid key for HPO Term annotation {key}')

    def __str__(self) -> str:
        return f'items={self.items} | cached={self.cached}'

    def __eq__(self, other: Any) -> bool:
        """
        Backwards compatibility of ``dict`` features
        """
        return bool([self.items, self.cached] == other)


class HPOAnnotationCollection:
    def __init__(self) -> None:
        self.genes: HPOAnnotation = HPOAnnotation()
        self.omim_diseases: HPOAnnotation = HPOAnnotation()
        self.orpha_diseases: HPOAnnotation = HPOAnnotation()
        self.decipher_diseases: HPOAnnotation = HPOAnnotation()
        self.omim_excluded_diseases: HPOAnnotation = HPOAnnotation()
        self.orpha_excluded_diseases: HPOAnnotation = HPOAnnotation()
        self.decipher_excluded_diseases: HPOAnnotation = HPOAnnotation()

    def __getitem__(self, key: str) -> HPOAnnotation:
        try:
            return self.__getattribute__(key)
        except AttributeError:
            raise KeyError(f'Invalid key {key}')

    def __setitem__(self, key: str, value: Any) -> None:
        if key in self.__dict__:
            self.__setattr__(key, value)
        else:
            raise KeyError(f'Invalid key {key}')

    def __eq__(self, other: Any) -> bool:
        return all([
            self[x] == other[x] for x in (
                'genes',
                'omim_diseases',
                'orpha_diseases',
                'decipher_diseases',
                'omim_excluded_diseases',
                'orpha_excluded_diseases',
                'decipher_excluded_diseases'
            )
        ])


class HPOTerm():
    """
    Represents an HPO Term
    with all metadata

    .. note::

        An HPOTerm is initialized as an empty object.
        Attributes are added line by line from an OBO file

    Attributes
    ----------
    all_parents: set of :class:`.HPOTerm`
        Set of direct and indirect parent HPOTerms

        .. note::

            This property is read-only

    children: list of :class:`.HPOTerm`
        List of direct children HPOTerms

    comment: str
        Comments from HPO Team

        **Example:** ::

            Multicystic kidney dysplasia is the result of
            abnormal fetal renal development in which the affected kidney
            is replaced by multiple cysts and has little or no residual
            function. The vast majority of multicystic kidneys are unilateral.
            Multicystic kidney can be diagnosed on prenatal ultrasound.

    definition: str
        HPO Term Definition

        **Example:** ::

            "Multicystic dysplasia of the kidney is characterized by
            multiple cysts of varying size in the kidney and the absence of a
            normal pelvicaliceal system. The condition is associated with
            ureteral or ureteropelvic atresia, and the affected kidney is
            nonfunctional." [HPO:curators]

        .. warning::

           The string contains double-quote enclosed sections

    genes: set of :class:`pyhpo.annotations.Gene`
        All genes associated with the term or its children

        .. note::

            The set is recursively calcualted the first time it is requested
            by retrieving all children genes as well. The updated set is then
            cached.

            It is not possibe to remove genes from the set. Any updates will
            only allow addition of new genes.

        .. warning::

            Updating the associated gene set causes a recalculation of the
            cache and the caches of all parents, so this is a quite expensive
            operation and should be avoided.

    id: str
        HPO Term ID

        **Example:** ::

            'HP:0000003'

    information_content: dict
        The information content of the HPO term for:

        * **gene**: float
        * **omim**: float
        * **orpha**: float
        * **decipher**: float

        **Example:** ::

            {
                'gene': 0.24,
                'omim': 0.84,
                'orpha': 0.43,
                'decipher': 0.12
            }

    name: str
        HPO Term name

        **Example:** ::

            'Abnormality of body height'

    omim_diseases: set of :class:`pyhpo.annotations.Omim`
        All OMIM diseases associated with the term or its children

        .. note::

            The set is recursively calcualted the first time it is requested
            by retrieving all children OMIM diseases as well. The updated set
            is then cached.

            It is not possibe to remove OMIM diseases from the set. Any updates
            will only allow addition of new omim-diseases.

        .. warning::

            Updating the associated OMIM disease set causes a recalculation
            of the cache and the caches of all parents, so this is a quite
            expensive operation and should be avoided.

    omim_excluded_diseases: set of :class:`pyhpo.annotations.Omim`
        All OMIM diseases that are excluded from the term

        .. note::

            Since excluded diseased do not follow the general model
            of ontology inheritance, the associated annotations
            are not inherited from or passed on to parents or children

    orpha_diseases: set of :class:`pyhpo.annotations.Orpha`
        All Orphanet diseases associated with the term or its children

        .. note::

            The set is recursively calcualted the first time it is requested
            by retrieving all children Orphanet diseases as well. The updated
            set is then cached.

            It is not possibe to remove Orphanet diseases from the set.
            Any updates will only allow addition of new orphanet-diseases.

        .. warning::

            Updating the associated Orphanet disease set causes a recalculation
            of the cache and the caches of all parents, so this is a quite
            expensive operation and should be avoided.

    decipher_diseases: set of :class:`pyhpo.annotations.Decipher`
        All Decipher diseases associated with the term or its children

        .. note::

            The set is recursively calcualted the first time it is requested
            by retrieving all children Decipher diseases as well.
            The updated set is then cached.

            It is not possibe to remove Decipher diseases from the set.
            Any updates will only allow addition of new decipher-diseases.

        .. warning::

            Updating the associated Decipher disease set causes a recalculation
            of the cache and the caches of all parents, so this is a quite
            expensive operation and should be avoided.

    parents: list of :class:`.HPOTerm`
        List of direct parent :class:`.HPOTerms`

    synonym: list of str
        List of synonymous names

        **Example:** ::

            ['Multicystic dysplastic kidney', 'Multicystic kidneys',
            'Multicystic renal dysplasia']

    xref: list
        List of xref attributes

    is_a: list of str
        List of parent HPO terms

        **Example:** ::

            ['HP:0000107 ! Renal cyst']

    is_obsolete: bool
        Indicates if the HPO term is obsolete and should not be used anymore.

        .. note::

            Check the ``replaced_by`` attribute which HPO term to use instead.

    replaced_by: str (``HPOTerm.id``)
        Specifies which HPO term to use instead if self is obsolete.

        **Example:** ::

            'HP:0008665'

        .. warning::

            It is not guaranteed that this attribute is present -
            even for obsolete terms.

    is_modifier: bool
        Indicates whether the HPO is a child of a mooifier term. (read only)
        Modifier terms are specified in ``HPOTerm._modifier_ids``

        * ``Mode of inheritance`` - ``'HP:0000005'``
        * ``Clinical modifier`` - ``'HP:0012823'``
        * ``Frequency`` - ``'HP:0040279'``
        * ``Clinical course`` - ``'HP:0031797'``
        * ``Blood group`` - ``'HP:0032223'``
        * ``Past medical history`` - ``'HP:0032443'``

    _index: int
        Integer representation of ID

        **Example:** ::

            3
    """

    # IDs of root modifier terms
    _modifier_ids = {5, 12823, 40279, 31797, 32223, 32443}

    def __init__(self) -> None:
        self.name: str = ''
        self.definition: str = ''
        self.comment: str = ''
        self._id: str = ''
        self._index: int = 0
        self._hash: Optional[int] = None

        self._alt_id: List[str] = []
        self._alt_index: List[int] = []
        self._synonym: List[str] = []
        self._xref: List[str] = []
        self._is_a: List[str] = []
        self._is_obsolete: bool = False
        self._parents: List['HPOTerm'] = []
        self._all_parents: Optional[Set['HPOTerm']] = None
        self._children: List['HPOTerm'] = []
        self._hierarchy: Optional[Tuple[Tuple['HPOTerm', ...], ...]] = None

        # External annotations
        self._annotations = HPOAnnotationCollection()

        self.information_content = {
            'omim': 0.0,
            'gene': 0.0
        }

    def add_line(self, line: str) -> None:
        """
        Adds one line of information to ``self``.

        Use this function for parsing ``obo`` files line by line

        Parameters
        ----------
        line: str
            One line of an HPO obo file belonging to this HPO term
        """
        if line == '':
            return
        key, *values = line.split(': ')
        value = ': '.join(values).strip()
        if key == 'def':
            key = 'definition'
        self.__setattr__(key, value)

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        if self._id and self._id != value:
            raise RuntimeError('Unable to update existing ID')
        self._id = value
        self._index = HPOTerm.id_from_string(value)

    @property
    def alt_id(self) -> List[str]:
        return self._alt_id

    @alt_id.setter
    def alt_id(self, value: str) -> None:
        self._alt_id.append(value)
        self._alt_index.append(HPOTerm.id_from_string(value))

    @property
    def synonym(self) -> List[str]:
        return self._synonym

    @synonym.setter
    def synonym(self, value: str) -> None:
        self._synonym.append(HPOTerm.parse_synonym(value))

    @property
    def xref(self) -> List[str]:
        return self._xref

    @xref.setter
    def xref(self, value: str) -> None:
        self._xref.append(value)

    @property
    def is_a(self) -> List[str]:
        return self._is_a

    @is_a.setter
    def is_a(self, value: str) -> None:
        self._is_a.append(value)

    @property
    def is_obsolete(self) -> bool:
        return self._is_obsolete

    @is_obsolete.setter
    def is_obsolete(self, value: str) -> None:
        if str(value).lower() in TRUTH:
            self._is_obsolete = True
            self.name = self.name.replace('obsolete', '').strip()
        else:
            self._is_obsolete = False

    @property
    def parents(self) -> List['HPOTerm']:
        return self._parents

    @parents.setter
    def parents(self, hpo: 'HPOTerm') -> None:
        self._parents.append(hpo)

    @property
    def children(self) -> List['HPOTerm']:
        return self._children

    @children.setter
    def children(self, hpo: 'HPOTerm') -> None:
        self._children.append(hpo)

    @property
    def genes(self) -> Set[Any]:
        return self._get_annotations('genes')

    @genes.setter
    def genes(self, genes: Set[Any]) -> None:
        self._update_annotations('genes', genes)

    @property
    def omim_diseases(self) -> Set[Any]:
        return self._get_annotations('omim_diseases')

    @omim_diseases.setter
    def omim_diseases(self, diseases: Set[Any]) -> None:
        self._update_annotations('omim_diseases', diseases)

    @property
    def orpha_diseases(self) -> Set[Any]:
        return self._get_annotations('orpha_diseases')

    @orpha_diseases.setter
    def orpha_diseases(self, diseases: Set[Any]) -> None:
        self._update_annotations('orpha_diseases', diseases)

    @property
    def decipher_diseases(self) -> Set[Any]:
        return self._get_annotations('decipher_diseases')

    @decipher_diseases.setter
    def decipher_diseases(self, diseases: Set[Any]) -> None:
        self._update_annotations('decipher_diseases', diseases)

    @property
    def omim_excluded_diseases(self) -> Set[Any]:
        """
        Since excluded diseased do not follow the general model
        of ontology inheritance, the associated annotations
        are not inherited from or passed on to parents or children
        """
        return self._annotations.omim_excluded_diseases.items

    @omim_excluded_diseases.setter
    def omim_excluded_diseases(self, diseases: Set[Any]) -> None:
        """
        Since excluded diseased do not follow the general model
        of ontology inheritance, the associated annotations
        are not inherited from or passed on to parents or children
        """
        self._annotations.omim_excluded_diseases.items.update(diseases)

    @property
    def orpha_excluded_diseases(self) -> Set[Any]:
        """
        Since excluded diseased do not follow the general model
        of ontology inheritance, the associated annotations
        are not inherited from or passed on to parents or children
        """
        return self._annotations.orpha_excluded_diseases.items

    @orpha_excluded_diseases.setter
    def orpha_excluded_diseases(self, diseases: Set[Any]) -> None:
        """
        Since excluded diseased do not follow the general model
        of ontology inheritance, the associated annotations
        are not inherited from or passed on to parents or children
        """
        self._annotations.orpha_excluded_diseases.items.update(diseases)

    @property
    def decipher_excluded_diseases(self) -> Set[Any]:
        """
        Since excluded diseased do not follow the general model
        of ontology inheritance, the associated annotations
        are not inherited from or passed on to parents or children
        """
        return self._annotations.decipher_excluded_diseases.items

    @decipher_excluded_diseases.setter
    def decipher_excluded_diseases(self, diseases: Set[Any]) -> None:
        """
        Since excluded diseased do not follow the general model
        of ontology inheritance, the associated annotations
        are not inherited from or passed on to parents or children
        """
        self._annotations.decipher_excluded_diseases.items.update(diseases)

    @property
    def is_modifier(self) -> bool:
        return bool(self._modifier_ids & {int(x) for x in self.all_parents})

    def _get_annotations(self, kind: str) -> Set['pyhpo.Annotation']:
        """
        Retrieves the associated annotations from itself and all child terms

        Parameters
        ----------
        kind: str
            The type of annotation to return. Possible values:

            * **genes** Return all associated genes
            * **omim_diseases** Return all associated OMIM diseases
            * **orpha_diseases** Return all associated Orphanet diseases
            * **decipher_diseases** Return all associated Decipher diseases

        This function creates a cache (if not yet present) by
        recursively querying the annotations of all child terms through
        :func:`pyhpo.term.HPOTerm._build_annotation_cache`
        """

        if not self._annotations[kind].cached:
            # Cache not yet built
            self._build_annotation_cache(kind)
        return self._annotations[kind].items

    def _build_annotation_cache(self, kind: str) -> None:
        """
        Traverses through all child terms to retrieve their
        annotations and build a local cache of all annotations

        Parameters
        ----------
        kind: str
            The type of annotation to return. Possible values:

            * **genes** Return all associated genes
            * **omim_diseases** Return all associated OMIM diseases
            * **orpha_diseases** Return all associated Orphanet diseases
            * **decipher_diseases** Return all associated Decipher diseases

        """
        for child in self.children:
            self._annotations[kind].items.update(
                child.__getattribute__(kind)
            )

        # Set cache-flag to True
        self._annotations[kind].cached = True

    def _update_annotations(
        self,
        kind: str,
        annotations: Set['pyhpo.Annotation']
    ) -> None:
        """
        Adds additional annotations of the given kind

        Parameters
        ----------
        kind: str
            The type of annotation to return. Possible values:

            * **genes** Return all associated genes
            * **omim_diseases** Return all associated OMIM diseases
            * **orpha_diseases** Return all associated Orphanet diseases
            * **decipher_diseases** Return all associated Decipher diseases

        annotations: set
            A set of new annotations to add to the extsting ones

        If an annotation-cache is already present, this method will
        ensure that all parent-caches will be updated as well.

        """
        if not isinstance(annotations, set):
            raise RuntimeError('{} must be specified as set'.format(kind))

        self._annotations[kind].items.update(annotations)

        # If cache-flag is set we need to update the parents as well
        if self._annotations[kind].cached:
            warnings.warn(
                (
                    'It is strongly discouraged to update annotation'
                    ' associations during the runtime after setup.'
                    ' This is a very time consuming process.'
                )
            )

            # Reset the cache
            self._build_annotation_cache(kind)

            # Update all parents
            for parent in self.parents:
                parent.__setattr__(kind, self._annotations[kind].items)

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

    def parent_ids(self) -> List[int]:
        """
        List of IDs of parent HPO Terms

        Returns
        -------
        list of int
            All ids of the direct parents
        """
        return [
            HPOTerm.id_from_string(val) for val in self.is_a
        ]

    @property
    def all_parents(self) -> Set['HPOTerm']:
        if self._all_parents is None:
            self._all_parents = set()
            for path in self.hierarchy():
                self._all_parents.update(path)

        return self._all_parents

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

        # common ancestors
        return self.all_parents & other.all_parents

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

    def print_hierarchy(
        self,
        indent: int = 0,
        indent_increase: int = 2
    ) -> None:
        """
        Prints hierarchy diagram of current and
        all ancestral HPO Terms

        Parameters
        ----------
        indent: int
            Number of spaces for current indentation level

        indent_increase: int
            Number of spaces to increase the next indentation level

        Returns
        -------
        None
        """

        print('{}-{}'.format(' '*indent, self.name))
        for parent in self.parents:
            parent.print_hierarchy(indent + indent_increase, indent_increase)

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

        if self._hierarchy:
            return self._hierarchy

        if not self.parents:
            self._hierarchy = ((self,),)
            return self._hierarchy

        paths = []
        for parent in self.parents:
            for path in parent.hierarchy():
                paths.append((self,) + path)

        self._hierarchy = tuple(paths)
        return self._hierarchy

    def longest_path_to_root(self) -> int:
        """
        Calculates the longest path to root

        Returns
        -------
        int
            Maximum number of nodes until the root HPOTerm
        """
        return max([
            len(h)-1 for h in self.hierarchy()
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
            len(h)-1 for h in self.hierarchy()
        ])

    def shortest_path_to_parent(
        self,
        other: 'HPOTerm'
    ) -> Tuple[Union[int, float], Optional[Tuple['HPOTerm', ...]]]:
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
        steps = float('inf')
        shortest_path = None
        for path in self.hierarchy():
            try:
                i = path.index(other)
                if i < steps:
                    steps = i
                    shortest_path = path[:i+1]
            except ValueError:
                pass

        return (steps, shortest_path)

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

            # path1 and path2 can't be empty, since the common ancestor
            # is a parent of self and other
            assert path1[1] is not None
            assert path2[1] is not None

            total_path = path1[1] + tuple(reversed(path2[1]))[1:]
            paths.append((
                int(path1[0] + path2[0]),
                total_path,
                int(path1[0]),
                int(path2[0])
            ))
        return sorted(paths, key=lambda x: x[0])[0]

    def similarity_score(
        self,
        other: 'HPOTerm',
        kind: str = '',
        method: str = ''
    ) -> float:
        """
        According to Robinson et al, American Journal of Human Genetics, (2008)
        and Resnik et at, Proceedings of the 14th IJCAI, (1995)

        Parameters
        ----------
        kind: str, default ``omim``
            Which kind of information content should be calculated.

            Available option:

            * **omim** (Default)
            * **orpha**
            * **decipher**
            * **gene**

        method: string, default ``resnik``
            The method to use to calculate the similarity.

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

        Returns
        -------
        float
            The similarity score of the two terms.
        """
        if not method:
            method = 'resnik'

        if not kind:
            kind = 'omim'

        if method == 'resnik':
            return self._resnik_similarity_score(other, kind)

        elif method == 'lin':
            return self._lin_similarity_score(other, kind)

        elif method == 'jc':
            return self._jc_similarity_score(other, kind)

        elif method == 'jc2':
            return self._jc_similarity_score_2(other, kind)

        elif method == 'rel':
            return self. _rel_similarity_score(other, kind)

        elif method == 'ic':
            return self. _ic_similarity_score(other, kind)

        elif method == 'graphic':
            return self. _graph_ic_similarity_score(other, kind)

        elif method == 'dist':
            return self. _dist_similarity_score(other)

        else:
            raise RuntimeError('Unknown method to calculate similarity')

    def toJSON(
        self,
        verbose: bool = False
    ) -> Dict:
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
            res['synonym'] = self._synonym
            res['xref'] = self._xref
            res['is_a'] = self._is_a
            res['ic'] = self.information_content

        return res

    def _resnik_similarity_score(self, other: 'HPOTerm', kind: str) -> float:
        sim = 0.0
        for term in self.common_ancestors(other):
            ic = term.information_content[kind]
            if ic > sim:
                sim = ic

        return sim

    def _lin_similarity_score(self, other: 'HPOTerm', kind: str) -> float:
        mica = self._resnik_similarity_score(other, kind)
        ic_t1 = self.information_content[kind]
        ic_t2 = other.information_content[kind]
        try:
            return (2 * mica) / (ic_t1 + ic_t2)
        except ZeroDivisionError:
            return 0

    def _jc_similarity_score(self, other: 'HPOTerm', kind: str) -> float:
        """
        This method is the same as the source code in
        the R package ``hposim``

        .. code-block:: r

            res= - 1/ ( 1 + 2*IC[IC[,1]==an,3] - IC[IC[,1]==term1,3]
            - IC[IC[,1]==term2,3] )

        .. note::

            See :func:`pyhpo.term._jc_similarity_score_2`
            for an alternative way to calcukate Jiang & Conrath
        """
        if self == other:
            return 1

        mica = self._resnik_similarity_score(other, kind)
        ic_t1 = self.information_content[kind]
        ic_t2 = other.information_content[kind]

        return -1 / (1 + (2 * mica) - ic_t1 - ic_t2)

    def _jc_similarity_score_2(self, other: 'HPOTerm', kind: str) -> float:
        """
        This method is the same as the description
        in the paper for the R package ``hposim``

        ::

            sim[JC](t1,t2) = 1-(IC(t1)+IC(t2)−2×IC(t[MICA]))

        .. note::

            See :func:`pyhpo.term._jc_similarity_score`
            for an alternative way to calcukate Jiang & Conrath
        """
        if self == other:
            return 1

        mica = self._resnik_similarity_score(other, kind)
        ic_t1 = self.information_content[kind]
        ic_t2 = other.information_content[kind]

        return 1 - (ic_t1 + ic_t2 - (2 * mica))

    def _rel_similarity_score(self, other: 'HPOTerm', kind: str) -> float:
        mica = self._resnik_similarity_score(other, kind)
        lin = self._lin_similarity_score(other, kind)

        return lin * (1 - (math.exp(mica * -1)))

    def _ic_similarity_score(self, other: 'HPOTerm', kind: str) -> float:
        mica = self._resnik_similarity_score(other, kind)
        lin = self._lin_similarity_score(other, kind)

        return lin * (1 - (1 / (1 + mica)))

    def _graph_ic_similarity_score(self, other: 'HPOTerm', kind: str) -> float:
        common = sum([
            x.information_content[kind] for x in
            self.common_ancestors(other)
        ])
        union = sum([
            x.information_content[kind] for x in
            (self.all_parents | other.all_parents)
        ])

        try:
            return common/union
        except ZeroDivisionError:
            return 0

    def _dist_similarity_score(self, other: 'HPOTerm') -> float:
        dist = self.path_to_other(other)[0]
        return 1/(dist + 1)

    @staticmethod
    def id_from_string(hpo_string: str) -> int:
        """
        Formats the HPO-type Term-ID into an integer id

        Parameters
        ----------
        hpo_string: str
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

    @staticmethod
    def parse_synonym(synonym: str) -> str:
        """
        Extracts the synonym from the synonym data line in the obo file format

        Parameters
        ----------
        synonym: str
            value part of synonym-data line of obo file

            e.g: "Multicystic dysplastic kidney" EXACT []

        Returns
        -------
        str
            Actual synonym title

            e.g.: Multicystic dysplastic kidney
        """
        return synonym.split('"')[1]

    def __index__(self) -> int:
        return self._index

    __int__ = __index__

    def __hash__(self) -> int:
        if not self._hash:
            self._hash = hash((
                self._index,
                self.name
            ))
        return self._hash

    def __eq__(self, t2: Any) -> bool:
        return self.__hash__() == t2.__hash__() and isinstance(t2, HPOTerm)

    def __lt__(self, other: Any) -> bool:
        return self.__int__() < int(other)

    def __str__(self) -> str:
        return '{} | {}'.format(self._id, self.name)

    def __repr__(self) -> str:
        return '\n'.join([
            '\n[Term]',
            'id: {}'.format(self._id),
            'name: {}'.format(self.name),
            'def: {}'.format(self.definition),
            'comment: {}'.format(self.comment),
            '\n'.join('synonym: {}'.format(item) for item in self._synonym),
            '\n'.join('xref: {}'.format(item) for item in self._xref),
            '\n'.join('is_a: {}'.format(item) for item in self._is_a),
            '\n'
        ])
