class HPOSet(list):
    def child_nodes(self):
        """
        Return a new HPOSet tha contains only
        the most specific HPO term for each subtree

        It basically will return only HPO terms
        that do not have descendant HPO terms
        present in the set
        """
        counter = {term.id: 0 for term in self}
        for child, parent in self.combinations():
            if child.is_child_of(parent):
                counter[parent.id] += 1
        return HPOSet([
            term for term in self if counter[term.id] == 0
        ])

    def all_genes(self):
        """
        Return the union of the genes
        attached to the HPO Terms in this set
        """
        genes = set()
        for term in self:
            genes.update(term.genes)
        return genes

    def variance(self):
        distances = []
        for term_a, term_b in self.combinations_one_way():
            distances.append(term_a.path_to_other(term_b)[0])

        if len(distances):
            return (
                sum(distances)/len(distances),
                min(distances),
                max(distances),
                distances
            )
        else:
            return (0, 0, 0, [])

    def combinations(self):
        for term_a in self:
            for term_b in self:
                if term_a == term_b:
                    continue
                yield (term_a, term_b)

    def combinations_one_way(self):
        for i, term_a in enumerate(self):
            for term_b in self[i+1:]:
                yield (term_a, term_b)
