import os
import math
import warnings

try:
    import pandas as pd
except ImportError:
    warnings.warn(
        'Some functionality requires pandas, which is currently not available',
        UserWarning)

from pyhpo.term import HPOTerm
from pyhpo.annotations import HPO_Gene, HPO_Omim, HPO_negative_Omim


class Ontology():
    """
    A linked and indexed list of interconnected :class:`HPOTerm` s.

    Attributes
    ----------
    genes: set
        Set of all genes associated with the HPOTerms
    omim_diseases: set
        Set of all OMIM-diseases associated with the HPOTerms
    omim_excluded_diseases: set
        Set of all excluded OMIM-diseases associated with the HPOTerms

    """
    def __init__(self, filename='hp.obo', data_folder=None):
        self._map = {}
        self._genes = set()
        self._omim_diseases = set()
        self._omim_excluded_diseases = set()

        if data_folder is None:
            data_folder = os.path.join(os.path.dirname(__file__), 'data')
        self._data_folder = data_folder

        if filename:
            self._load_from_file(os.path.join(
                data_folder,
                filename
            ))

    def add_annotations(self, data_folder=None):
        warnings.warn(
            'The method `ontology.add_annotations` is deprecated. '
            'The functionality is included by default when the Ontology '
            'is loaded from file since version 1.1.',
            DeprecationWarning,
            stacklevel=2
        )

    def _add_annotations(self, data_folder=None):
        """
        Add secondary annotations to each HPO Term.
        They currently include:
        - Genes
        - OMIIM diseases
        - excluded OMIM diseases

        It only works with properly named annotation files
        from the HPO source

        Parameters
        ----------
        data_folder: str, default ``None``
            Path to location where annotation files are stored

        Returns
        -------
        None
            None
        """

        if data_folder is None:
            data_folder = self._data_folder

        genes = HPO_Gene(path=data_folder)
        omim_diseases = HPO_Omim(path=data_folder)
        omim_excluded = HPO_negative_Omim(path=data_folder)
        for term in self:
            if term._index in genes:
                term.genes = genes[term._index]
                self._genes.update(genes[term._index])
            if term._index in omim_diseases:
                term.omim_diseases = omim_diseases[term._index]
                self._omim_diseases.update(omim_diseases[term._index])
            if term._index in omim_excluded:
                term.omim_excluded_diseases = omim_excluded[term._index]
                self._omim_excluded_diseases.update(
                    omim_excluded[term._index]
                )
        self._add_information_content()

    def _add_information_content(self):
        """
        Calculates the information content for each HPO Term
        According to Robinson et al, American Journal of Human Genetics, 2008
        https://www.sciencedirect.com/science/article/pii/S0002929708005351

        Returns
        -------
        None
            None
        """
        total_diseases = len(self.omim_diseases)
        total_genes = len(self.genes)
        for term in self:
            p_omim = len(term.omim_diseases)/total_diseases
            p_gene = len(term.genes)/total_genes
            if p_omim == 0:
                term.information_content['omim'] = 0
            else:
                term.information_content['omim'] = -math.log(p_omim)

            if p_gene == 0:
                term.information_content['gene'] = 0
            else:
                term.information_content['gene'] = -math.log(p_gene)

    def get_hpo_object(self, query):
        """
        Matches a single HPO term based on its name, synonym or id

        Parameters
        ----------
        query: str or int

            * **str** HPO term ``Scoliosis``
            * **str** synonym ``Curved spine``
            * **str** HPO-ID ``HP:0002650``
            * **int** HPO term id ``2650``

        Returns
        -------
        HPOTerm
            A single matching HPO term instance

        Example
        -------
            ::

                # Search by ID (int)
                >>> ontology.get_hpo_object(3)
                HP:0000003 | Multicystic kidney dysplasia

                # Search by HPO-ID (string)
                >>> ontology.get_hpo_object('HP:0000003')
                HP:0000003 | Multicystic kidney dysplasia

                # Search by term (string)
                >>> ontology.get_hpo_object('Multicystic kidney dysplasia')
                HP:0000003 | Multicystic kidney dysplasia

                # Search by synonym (string)
                >>> ontology.get_hpo_object('Multicystic renal dysplasia')
                HP:0000003 | Multicystic kidney dysplasia

        """

        if isinstance(query, str):
            if query.startswith('HP:'):
                return self[HPOTerm.id_from_string(query)]
            else:
                return self.synonym_match(query)

        if isinstance(query, int):
            return self[query]

        raise SyntaxError('Invalid type {} for parameter "query"'.format(
            type(query)
        ))

    def match(self, query):
        """
        Matches a single HPO term based on its name

        Parameters
        ----------
        query: str
            HPO term to match
            e.g: Abnormality of the nervous system

        Returns
        -------
        HPOTerm
            A single matching HPO term instance
        """

        for term in self:
            if query == term.name:
                return term
        raise RuntimeError('No HPO entry with name {}'.format(query))

    def path(self, query1, query2):
        """
        Returns the shortest connection between
        two HPO terms

        Parameters
        ----------
        query1: str or int
            HPO term 1, synonym or HPO-ID (HP:00001) to match
            HPO term id (Integer based)
            e.g: Abnormality of the nervous system
        query2: str or int
            HPO term 2, synonym or HPO-ID (HP:00001) to match
            HPO term id (Integer based)
            e.g: Abnormality of the nervous system

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

        term1 = self.get_hpo_object(query1)
        term2 = self.get_hpo_object(query2)
        return term1.path_to_other(term2)

    def search(self, query):
        """
        Iterator function for substring search
        for terms and synonyms in the ontology

        Parameters
        ----------
        query:  str
            Term to search for

        Yields
        ------
        HPOTerm
            Every matching HPO term instance
        """
        for term in self:
            if query in term.name or self.synonym_search(term, query):
                yield term

    def synonym_match(self, query):
        """
        Searches for actual and synonym term matches
        If a match is found in any term, that one is returned
        If no actual match is found, the first match
        with synonyms is considered

        Parameters
        ----------
        query:  str
            Term to search for

        Returns
        -------
        HPOTerm
            A single HPO term instance

        """
        synonym_hit = None
        for term in self:
            if query == term.name:
                return term
            if not synonym_hit and query in term.synonym:
                synonym_hit = term

        if synonym_hit:
            return synonym_hit
        raise RuntimeError('No HPO entry with term or synonym {}'.format(query))

    def synonym_search(self, term, query):
        """
        Indicates whether a term has a synonym that contains the query.
        Substring search in synonym

        Parameters
        ----------
        term:  HPOTerm
            Term to check
        query:  str
            Synonym substring

        Returns
        -------
        bool
            Indicates if ``term`` contains ``query`` as a synonym
        """

        for synonym in term.synonym:
            if query in synonym:
                return True
        return False

    def to_dataframe(self):
        """
        Creates a Pandas DataFrame from the most important features

        Each HPO term is one row, the features are present in columns

        Returns
        -------
        :class:`DataFrame`
            The DataFrame of HPO-Terms and their
            attributes in the following columns

            * **id** ``str`` The HPO Term ID "HP:0000003" (used as index)
            * **name** ``str`` The HPO Term name "Multicystic kidney dysplasia"
            * **parents** ``str`` Concatenated list of direct parents of
              HPO terms. Separated by ``|``
            * **children** ``str`` Concatenated list of direct children of
              HPO terms. Separated by ``|``
            * **ic_omim** ``float`` Information-content
              (based on associated OMIM diseases)
            * **ic_gene** ``float`` Information-content
              (based on associated genes)
            * **dTop_l** ``int`` Maximum distance to root term
              (via :func:`pyhpo.term.longest_path_to_root`)
            * **dTop_s** ``int`` Shortest distance to root term
              (via :func:`pyhpo.term.shortest_path_to_root`)
            * **dBottom** ``int`` Longest graph of children nodes
              (via :func:`pyhpo.term.longest_path_to_bottom`)
            * **genes** ``str`` Concatenated list of associated
              genes. Separated by ``|``
            * **diseases** ``str`` Concatenated list of associated
              OMIM diseases. Separated by ``|``
        """

        data = {
            'id': [],
            'name': [],
            'parents': [],
            'children': [],
            'ic_omim': [],
            'ic_gene': [],
            'dTop_l': [],
            'dTop_s': [],
            'dBottom': [],
            'genes': [],
            'diseases': []
        }

        # This is not the most elegant way to generate a DataFrame
        # But it works
        for term in self:
            data['id'].append(term.id)
            data['name'].append(term.name)
            data['parents'].append('|'.join([x.id for x in term.parents]))
            data['children'].append('|'.join([x.id for x in term.children]))
            data['ic_omim'].append(term.information_content['omim'])
            data['ic_gene'].append(term.information_content['gene'])
            data['dTop_l'].append(term.longest_path_to_root())
            data['dTop_s'].append(term.shortest_path_to_root())
            data['dBottom'].append(term.longest_path_to_bottom())
            data['genes'].append('|'.join([str(x) for x in term.genes]))
            data['diseases'].append('|'.join([
                str(x) for x in term.omim_diseases
            ]))

        return pd.DataFrame(data).set_index('id')

    @property
    def genes(self):
        return self._genes

    @property
    def omim_diseases(self):
        return self._omim_diseases

    @property
    def omim_excluded_diseases(self):
        return self._omim_excluded_diseases

    def _append(self, item):
        """
        Adds one HPO term to the ontology
        """
        self._map[item._index] = item

    def _connect_all(self):
        """
        Connects all parent-child associations in the Ontology
        Called by default after loading the ontology from a file
        """
        for term in self._map.values():
            for parent in term.parent_ids():
                term.parents = self._map[parent]
                self._map[parent].children = term

        for term in self._map.values():
            # Build caches of hierarchy to speed
            # up performance
            term.all_parents

    def _load_from_file(self, filename):
        """
        Reads an obo file line by line to add
        HPO terms to the Ontology

        Attributes
        ----------
        filename: str
            Full path to ``obo`` file

        """

        term = None
        with open(filename) as fh:
            for line in fh:
                line = line.strip()
                if line == '[Term]':
                    if term is not None:
                        self._append(term)
                    term = HPOTerm()
                    continue
                if not term:
                    continue
                term.add_line(line)
            self._append(term)
        self._connect_all()
        self._add_annotations()

    def __getitem__(self, key):
        if key in self._map:
            return self._map[key]
        else:
            return None

    def __iter__(self):
        return iter(self._map.values())

    def __len__(self):
        return len(self._map.keys())
