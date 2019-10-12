class HPOSet(list):
    def child_nodes(self):
        """
        Return a new HPOSet tha contains only
        the most specific HPO term for each subtree

        It basically will return only HPO terms
        that do not have descendant HPO terms
        present in the set

        Returns
        -------
        HPOSet
            HPOSet instance that contains only the most specific
            child nodes of the current HPOSet
        """
        counter = {term.id: 0 for term in self}
        for child, parent in self.combinations():
            if child.child_of(parent):
                counter[parent.id] += 1
        return HPOSet([
            term for term in self if counter[term.id] == 0
        ])

    def all_genes(self):
        """
        Calculates the union of the genes
        attached to the HPO Terms in this set

        Returns
        -------
        set of :class:`annotations.Gene`
            Set of all genes associated with the HPOTerms in the set
        """
        genes = set()
        for term in self:
            genes.update(term.genes)
        return genes

    def information_content(self, kind):
        """
        Gives back basic information content stats about the
        HPOTerms within the set

        Parameters
        ----------
        kind: str
            Which kind of information content should be calculated.
            Options are ['omim', 'gene']


        Returns
        -------
        dict
            Dict with the following items

            * **mean** ``float`` Mean information content
            * **max** ``float`` Maximum information content value
            * **total** ``float`` Sum of all information content values
            * **all** ``list of HPOTerm`` List with all information content values
        """
        res = {
            'mean': None,
            'total': 0,
            'max': 0,
            'all': [term.information_content[kind] for term in self]
        }
        res['total'] = sum(res['all'])
        res['max'] = max(res['all'])
        res['mean'] = res['total']/len(self)
        return res

    def variance(self):
        """
        Calculates the distances between all its term-pairs. It also provides
        basic calculations for variances among the pairs.

        Returns
        -------
        tuple of (int, int, int, list of int)
            Tuple with the variance metrices

            * **int** Average distance between pairs
            * **int** Smallest distance between pairs
            * **int** Largest distance between pairs
            * **list of int** List of all distances between pairs
        """

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
        """
        Helper generator function that returns all possible two-pair
        combination between all its terms

        This function is direction dependent. That means that every
        pair will appear twice. Once for each direction

        .. seealso:: :func:`pyhpo.set.HPOSet.combinations_one_way`

        Yields
        ------
        Tuple of :class:`term.HPOTerm`
            Tuple containing the follow items

            * **HPOTerm** instance 1 of the pair
            * **HPOTerm** instance 2 of the pair


        Examples
        --------
            ::

                ci = HPOSet([term1, term2, term3])
                ci.combinations()

                # Output:
                [
                    (term1, term2),
                    (term1, term3),
                    (term2, term1),
                    (term2, term3),
                    (term3, term1),
                    (term3, term2)
                ]

        """
        for term_a in self:
            for term_b in self:
                if term_a == term_b:
                    continue
                yield (term_a, term_b)

    def combinations_one_way(self):
        """
        Helper generator function that returns all possible two-pair
        combination between all its terms

        This methow will report each pair only once

        .. seealso:: :func:`pyhpo.set.HPOSet.combinations`

        Yields
        ------
        Tuple of :class:`term.HPOTerm`
            Tuple containing the follow items

            * **HPOTerm** instance 1 of the pair
            * **HPOTerm** instance 2 of the pair



        Example
        -------
            ::

                ci = HPOSet([term1, term2, term3])
                ci.combinations()

                # Output:
                [
                    (term1, term2),
                    (term1, term3),
                    (term2, term3)
                ]

        """
        for i, term_a in enumerate(self):
            for term_b in self[i+1:]:
                yield (term_a, term_b)

    def similarity(self, other, kind='omim'):
        """
        Calculates the similarity to another HPOSet
        According to Robinson et al, American Journal of Human Genetics, (2008)
        and Pesquita et al, BMC Bioinformatics, (2008)

        Parameters
        ----------
        other: HPOSet
            Another HPOSet to measure the similarity to

        kind: str, default ``omim``
            Which kind of information content should be calculated.
            Options are ['omim', 'gene']

        Returns
        -------
        float
            The similarity score to the other HPOSet

        """
        score1 = HPOSet._sim_score(self, other, kind)
        score2 = HPOSet._sim_score(other, self, kind)
        return (score1 + score2)/2

    @staticmethod
    def _sim_score(set1, set2, kind):
        """
        Calculates one-way similarity from one HPOSet to another HPOSet

        .. warning::

           This method should not be used by itself.
           Use :func:`pyhpo.set.HPOSet.similarity` instead.

        Parameters
        ----------
        set1: HPOSet
            One HPOSet to measure the similarity from
        set2: HPOSet
            Another HPOSet to measure the similarity to

        kind: str
            Which kind of information content should be calculated.
            Options are ['omim', 'gene']

        Returns
        -------
        float
            The one-way similarity from one to the other HPOSet

        """
        scores = []
        for set1_term in set1:
            scores.append(0)
            for set2_term in set2:
                score = set1_term.similarity_score(set2_term, kind)
                if score > scores[-1]:
                    scores[-1] = score
        return sum(scores)/len(scores)
