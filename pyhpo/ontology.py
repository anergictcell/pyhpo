from pyhpo.term import HPOTerm


class Ontology():
    def __init__(self, filename=None):
        self._map = {}

        if filename:
            self.load_from_file(filename)

    def load_from_file(self, filename):
        term = None
        with open(filename) as fh:
            for line in fh:
                line = line.strip()
                if line == '[Term]':
                    if term is not None:
                        self.append(term)
                    term = HPOTerm()
                    continue
                if not term:
                    continue
                term.add_line(line)
            self.append(term)
        self.connect_all()

    def append(self, item):
        self._map[item._index] = item

    def connect_all(self):
        for term in self._map.values():
            for parent in term.parent_ids():
                term.parents = self._map[parent]
                self._map[parent].children = term

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

    def __getitem__(self, key):
        if key in self._map:
            return self._map[key]
        else:
            return None

    def __len__(self):
        return len(self._map.keys())

    def __iter__(self):
        return iter(self._map.values())


# o = Ontology()
# for term in terms:
#     o.append(term)
# o.connect_all()
# 
# 