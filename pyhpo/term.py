class HPOTerm():
    """
    Represents an HPO Term
    with all metadata

    Initilized as empty object
    add info line by line from OBO file

    Attributes
    ----------
    name: str
        HPO Term name
        Example: Abnormality of body heigh
    id: str
        HPO Term ID
        Example: HP:0000003
    _index: int
        Integer representation of ID
        Example: 3
    definition: str
        HPO Term Definition
        Example: "Multicystic dysplasia of the kidney is characterized by multiple cysts of varying size in the kidney and the absence of a normal pelvicaliceal system. The condition is associated with ureteral or ureteropelvic atresia, and the affected kidney is nonfunctional." [HPO:curators]
    comment: str
        Comments from HPO Team
        Example: Multicystic kidney dysplasia is the result of abnormal fetal renal development in which the affected kidney is replaced by multiple cysts and has little or no residual function. The vast majority of multicystic kidneys are unilateral. Multicystic kidney can be diagnosed on prenatal ultrasound.
    synonym: list(str)
        List of synonymous names
        Example: ['Multicystic dysplastic kidney', 'Multicystic kidneys', 'Multicystic renal dysplasia']
    xref: list
        List of xref attributes
    is_a: list(str)
        List of parent HPO terms
        Example: ['HP:0000107 ! Renal cyst']

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
        self._children = []

        # External annotations
        self.genes = set()
        self.omim_diseases = set()
        self.omim_excluded_diseases = set()

    def add_line(self, line):
        if line == '':
            return
        key, *values = line.split(': ')
        value = ': '.join(values)
        if key == 'def':
            key = 'definition'
        self.__setattr__(key, value)

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

    def is_parent(self, other):
        return other.is_child_of(self)

    def is_child_of(self, other):
        if self == other:
            raise RuntimeError('An HPO term cannot be parent/child of itself')

        path = self.shortest_path_to_parent(other)
        return path[0] != float('inf') and path[1] is not None

    def parent_ids(self):
        """
        List of IDs of parent HPO Terms

        Returns:
        --------
        list(int)
            Example: [107]
        """
        return [
            HPOTerm.id_from_string(val) for val in self.is_a
        ]

    def count_parents(self):
        """
        Calculates total number of ancestral HPO Terms

        Returns
        -------
        int
            The number of all ancestral HPO Terms
        """
        return sum([
            parent.count_parents()
            for parent in self.parents
        ])+1

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

        Returns
        -------
        tuple
            Tuple of paths. Each path is another tuple made up of HPOTerms
        """

        if self._hierarchy:
            return self._hierarchy

        if not self.parents:
            self._hierarchy = [[self]]
            return self._hierarchy

        paths = []
        for parent in self.parents:
            for path in parent.hierarchy():
                paths.append([self] + path)

        self._hierarchy = paths
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
            len(h) for h in self.hierarchy()
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
            len(h) for h in self.hierarchy()
        ])

    def shortest_path_to_parent(self, other):
        """
        Calculates the shortest path to another HPO Term

        Parameters
        ----------
        other: HPOTerm
            Other HPO Term

        Returns
        -------
        int
            Minimum number of nodes until the specified HPOTerm
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
        if len(self.children):
            return max([
                child.longest_path_to_bottom(level + 1) for child in self.children
            ])
        else:
            return level

    def path_to_other(self, other):
        # set of all parents for self
        parents1 = set()
        for path in self.hierarchy():
            parents1.update(path)

        # set of all parents for other
        parents2 = set()
        for path in other.hierarchy():
            parents2.update(path)

        # common ancestors
        common = parents1 & parents2

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

    @staticmethod
    def id_from_string(hpo_string):
        # removes the term (if present)
        idx = hpo_string.split('!')[0].strip()
        return int(idx.split(':')[1].strip())

    @staticmethod
    def parse_synonym(synonym):
        return synonym.split('"')[1]
