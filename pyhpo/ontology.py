import os
from pyhpo.term import HPOTerm
from pyhpo.annotations import HPO_Gene, HPO_Omim, HPO_negative_Omim


class Ontology():
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

    def _load_from_file(self, filename):
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
        path_to_annotations: str
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

    def search(self, query):
        for term in self:
            if query in term.name or self.synonym_search(term, query):
                yield term

    def synonym_search(self, term, query):
        for synonym in term.synonym:
            if query in synonym:
                return True
        return False

    def match(self, query):
        for term in self:
            if query == term.name:
                return term
        raise RuntimeError('No HPO entry with name {}'.format(query))

    def synonym_match(self, query):
        """
        Searches for actual and synonym term matches
        If a match is found in any term, that one is returned
        If no actual match is found, the first match
        with synonyms is considered
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

    def path(self, query1, query2):
        term1 = self.get_hpo_object(query1)
        term2 = self.get_hpo_object(query2)
        return term1.path_to_other(term2)

    def get_hpo_object(self, query):
        if isinstance(query, str):
            return self.synonym_match(query)

        if isinstance(query, int):
            return self[query]

        raise SyntaxError('Invalid type {} for parameter "query"'.format(
            type(query)
        ))

    @property
    def genes(self):
        return self._genes

    @property
    def omim_diseases(self):
        return self._omim_diseases

    @property
    def omim_excluded_diseases(self):
        return self._omim_excluded_diseases

    def __getitem__(self, key):
        if key in self._map:
            return self._map[key]
        else:
            return None

    def __len__(self):
        return len(self._map.keys())

    def __iter__(self):
        return iter(self._map.values())
