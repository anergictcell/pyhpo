import os
import math

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
    def __init__(self, filename='hp.obo', data_folder='./'):
        self._map = {}
        self._genes = set()
        self._omim_diseases = set()
        self._omim_excluded_diseases = set()
        self._data_folder = data_folder

        if filename:
            self._load_from_file(os.path.join(
                data_folder,
                filename
            ))

    def add_annotations(self, data_folder=None):
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
        data_folder: str
            Path to location where annotation files are stored

        Returns
        -------
        None
        """

        if data_folder is None:
            data_folder = self._data_folder

        genes = HPO_Gene(path=data_folder)
        omim_diseases = HPO_Omim(path=data_folder)
        omim_excluded_diseases = HPO_negative_Omim(path=data_folder)
        for term in self:
            if term._index in genes:
                term.genes = genes[term._index]
                self._genes.update(genes[term._index])
            if term._index in omim_diseases:
                term.omim_diseases = omim_diseases[term._index]
                self._omim_diseases.update(omim_diseases[term._index])
            if term._index in omim_excluded_diseases:
                term.omim_excluded_diseases = omim_excluded_diseases[term._index]
                self._omim_excluded_diseases.update(omim_excluded_diseases[term._index])
        self.add_information_content()

    def add_information_content(self):
        total_diseases = len(self.omim_diseases)
        total_genes = len(self.genes)
        for term in self:
            p_omim = len(term.omim_diseases)/total_diseases
            p_gene = len(term.genes)/total_genes
            if p_omim == 0:
                term.information_content['omim'] = 0
            else:
                term.information_content['omim'] = -math.log10(p_omim)

            if p_gene == 0:
                term.information_content['gene'] = 0
            else:
                term.information_content['gene'] = -math.log10(p_gene)

    def get_hpo_object(self, query):
        """
        Matches a single HPO term based on its name, synonym or id

        Parameters
        ----------
        query: str, int
            HPO term, synonym or HPO-ID (HP:00001) to match
            HPO term id (Integer based)
            e.g: Abnormality of the nervous system

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
        query: str, int
            HPO term, synonym or HPO-ID (HP:00001) to match
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

    def __getitem__(self, key):
        if key in self._map:
            return self._map[key]
        else:
            return None

    def __iter__(self):
        return iter(self._map.values())

    def __len__(self):
        return len(self._map.keys())
