import warnings


class HPOTerm():
    """
    Represents an HPO Term
    with all metadata

    .. note::

        An HPOTerm is initialized as an empty object.
        Attributes are added line by line from an OBO file

    Attributes
    ----------
    children: list of HPOTerm
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

    genes: set of :class:`annotations.Gene`
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

            HP:0000003

    name: str
        HPO Term name

        **Example:** ::

            Abnormality of body height

    omim_diseases: set of :class:`annotations.Omim`
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

    omim_excluded_diseases: set of :class:`annotations.Omim`
        All OMIM diseases that are excluded from the term

        .. warning::

            Currently, the functionality of this feature is incorrect.
            It should inherit excluded diseases from its parents,
            but it currently does not.

            **Don't use this attribute for now**

    parents: list of HPOTerm
        List of direct parent HPOTerms

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

    _index: int
        Integer representation of ID

        **Example:** ::

            3
    """
    def __init__(self):
        self.name = None
        self.definition = None
        self.comment = None
        self._id = None
        self._index = 0

        self._alt_id = []
        self._alt_index = []
        self._synonym = []
        self._xref = []
        self._is_a = []
        self._parents = []
        self._all_parents = None
        self._children = []
        self._hierarchy = None

        # External annotations
        self._genes = set()
        self._all_child_genes = None
        self._omim_diseases = set()
        self._all_child_omim_diseases = None
        self._omim_excluded_diseases = set()
        self.information_content = {
            'omim': None,
            'gene': None
        }

    def add_line(self, line):
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
        value = ': '.join(values)
        if key == 'def':
            key = 'definition'
        self.__setattr__(key, value)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        if self._id and self._id != value:
            raise RuntimeError('Unable to update existing ID')
        self._id = value
        self._index = HPOTerm.id_from_string(value)

    @property
    def alt_id(self):
        return self._alt_id

    @alt_id.setter
    def alt_id(self, value):
        self._alt_id.append(value)
        self._alt_index.append(HPOTerm.id_from_string(value))

    @property
    def synonym(self):
        return self._synonym

    @synonym.setter
    def synonym(self, value):
        self._synonym.append(HPOTerm.parse_synonym(value))

    @property
    def xref(self):
        return self._xref

    @xref.setter
    def xref(self, value):
        self._xref.append(value)

    @property
    def is_a(self):
        return self._is_a

    @is_a.setter
    def is_a(self, value):
        self._is_a.append(value)

    @property
    def parents(self):
        return self._parents

    @parents.setter
    def parents(self, hpo):
        self._parents.append(hpo)

    @property
    def children(self):
        return self._children

    @children.setter
    def children(self, hpo):
        self._children.append(hpo)

    @property
    def genes(self):
        # Check if cache is present
        if self._all_child_genes is None:

            # Update all child gene associations
            # then include all their association with self
            genes = self._genes
            for child in self.children:
                genes.update(child.genes)

            # Update the cache
            self._all_child_genes = genes
        return self._all_child_genes

    @genes.setter
    def genes(self, genes):
        if not isinstance(genes, set):
            raise RuntimeError('Genes must be specified as set')
        self._genes.update(genes)

        # If the cache was present, we have to update all parent
        # terms again
        if self._all_child_genes:
            warnings.warn(
                (
                    'It is strongly discouraged to update gene'
                    ' associations during the runtime after setup.'
                    ' This is a very time consuming process.'
                )
            )
            self._all_child_genes = None
            for parent in self.parents:
                parent.genes = self.genes

    @property
    def omim_diseases(self):
        # Check if cache is present
        if self._all_child_omim_diseases is None:

            # Update all child OMIM associations
            # then include all their association with self
            diseases = self._omim_diseases
            for child in self.children:
                diseases.update(child.omim_diseases)

            # Update the cache
            self._all_child_omim_diseases = diseases

        return self._all_child_omim_diseases

    @omim_diseases.setter
    def omim_diseases(self, diseases):
        if not isinstance(diseases, set):
            raise RuntimeError('OMIM diseases must be specified as set')
        self._omim_diseases.update(diseases)

        # If the cache was present, we have to update all parent
        # terms again
        if self._all_child_omim_diseases:
            warnings.warn(
                (
                    'It is strongly discouraged to update disease'
                    ' associations during the runtime after setup.'
                    ' This is a very time consuming process.'
                )
            )
            self._all_child_omim_diseases = None
            for parent in self.parents:
                parent.omim_diseases = self.omim_diseases

    @property
    def omim_excluded_diseases(self):
        return self._omim_excluded_diseases

    @omim_excluded_diseases.setter
    def omim_excluded_diseases(self, diseases):
        self._omim_excluded_diseases.update(diseases)

    def parent_of(self, other):
        """
        Checks if ``self`` is a direct or indirect parent of ``other``.

        Parameters
        ----------
        other: HPOTerm
            HPOTerm to check for lineage dependency

        Returns
        -------
        bool
            Is the HPOTerm a direct or indirect parent of another HPOTerms
        """
        return other.child_of(self)

    def child_of(self, other):
        """
        Checks if ``self`` is a direct or indirect child of ``other``.

        Parameters
        ----------
        other: HPOTerm
            HPOTerm to check for lineage dependency

        Returns
        -------
        bool
            Is the HPOTerm a direct or indirect child of another HPOTerms
        """
        if self == other:
            raise RuntimeError('An HPO term cannot be parent/child of itself')

        path = self.shortest_path_to_parent(other)
        return path[0] != float('inf') and path[1] is not None

    def parent_ids(self):
        """
        List of IDs of parent HPO Terms

        Returns
        -------
        list(int)
            All ids of the direct parents
        """
        return [
            HPOTerm.id_from_string(val) for val in self.is_a
        ]

    @property
    def all_parents(self):
        if self._all_parents is None:
            self._all_parents = set()
            for path in self.hierarchy():
                self._all_parents.update(path)

        return self._all_parents

    def common_ancestors(self, other):
        """
        Identifies all common ancestors
        of two HPO terms

        Parameters
        ----------
        other: HPOTerm
            Target HPO term for path finding

        Returns
        -------
        set
            Set of common ancestor HPOTerms
        """

        # common ancestors
        return self.all_parents & other.all_parents

    def count_parents(self):
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

    def print_hierarchy(self, indent=0, indent_increase=2):
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

    def hierarchy(self):
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
        tuple
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

    def longest_path_to_root(self):
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

    def shortest_path_to_root(self):
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

    def shortest_path_to_parent(self, other):
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
            for i, term in enumerate(path):
                if term == other:
                    if i < steps:
                        steps = i
                        shortest_path = path[:i+1]
        return (steps, shortest_path)

    def longest_path_to_bottom(self, level=0):
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
                child.longest_path_to_bottom(level + 1) for child in self.children
            ])
        else:
            return level

    def path_to_other(self, other):
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
                path1[0] + path2[0],
                total_path,
                path1[0],
                path2[0]
            ))
        return sorted(paths, key=lambda x: x[0])[0]

    def similarity_score(self, other, kind=None):
        """
        According to Robinson et al, American Journal of Human Genetics, (2008)
        and Resnik et at, Proceedings of the 14th IJCAI, (1995)

        Parameters
        ----------
        kind: str, default ``None``
            Which kind of information content should be calculated.
            Options are ['omim', 'gene']

        Returns
        -------
        float or dict
            The similarity score of a dict with the following items:

            * **omim** ``float`` The OMIM-based similarity score
            * **gene** ``float`` The gene association-based similarity score
        """
        sim = {
            'omim': 0,
            'gene': 0
        }
        for term in self.common_ancestors(other):
            ic = term.information_content
            if ic['omim'] > sim['omim']:
                sim['omim'] = ic['omim']
            if ic['gene'] > sim['gene']:
                sim['gene'] = ic['gene']

        if kind is None:
            return sim
        else:
            return sim[kind]

    @staticmethod
    def id_from_string(hpo_string):
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
    def parse_synonym(synonym):
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

    def __index__(self):
        return self._index

    __int__ = __index__

    __hash__ = __index__

    def __eq__(self, other):
        return isinstance(other, HPOTerm) and self.__hash__() == other.__hash__()

    def __lt__(self, other):
        return self.__int__() < int(other)

    def __str__(self):
        return '{} | {}'.format(self._id, self.name)

    def __repr__(self):
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
