import warnings

from pyhpo.ontology import Ontology
from pyhpo.term import HPOTerm
from pyhpo.matrix import Matrix


class HPOSet(set):
    def __init__(self, items):
        set.__init__(self, items)
        self._list = list(items)

    def add(self, item):
        """
        Overwrites ``set.add`` to ensure we keep the
        ``self._list`` property updated as well.
        """
        if item not in self:
            set.add(self, item)
            self._list.append(item)

    def update(self, items):
        """
        Overwrites ``set.update`` to ensure we keep the
        ``self._list`` property updated as well.
        """
        for item in items:
            self.add(item)

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

    def remove_modifier(self):
        """
        Removes all modifier terms. By default, this includes

        * ``Mode of inheritance: 'HP:0000005'``
        * ``Clinical modifier: 'HP:0012823'``
        * ``Frequency: 'HP:0040279'``
        * ``Clinical course: 'HP:0031797'``
        * ``Blood group: 'HP:0032223'``
        * ``Past medical history: 'HP:0032443'``


        Returns
        -------
        HPOSet
            HPOSet instance that contains only
            ``Phenotypic abnormality`` HPO terms

        """

        return HPOSet([
            term for term in self if not term.is_modifier
        ])

    def replace_obsolete(self, verbose=False):
        """
        Replaces obsolete terms with the replacement term

        .. warning::

            Not all obsolete terms have a replacement

        Parameters
        ----------
        verbose: bool, default: ``False``
            Print warnings if an obsolete term does not have a replacement.

        Returns
        -------
        HPOSet
            A new HPOSet

        """
        ids = set()
        for term in self:
            if term.is_obsolete:
                try:
                    replaced = Ontology[
                        HPOTerm.id_from_string(term.replaced_by)
                    ]
                    ids.add(replaced)
                except AttributeError:
                    warnings.warn(
                        'The term {} is obsolete and has no replacement.'
                            .format(term),
                        UserWarning)

            else:
                ids.add(term)
        return HPOSet(ids)

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

    def omim_diseases(self):
        """
        Calculates the union of the Omim diseases
        attached to the HPO Terms in this set

        Returns
        -------
        set of :class:`annotations.Omim`
            Set of all Omim diseases associated with the HPOTerms in the set
        """
        omims = set()
        for term in self:
            omims.update(term.omim_diseases)
        return omims

    def orpha_diseases(self):
        """
        Calculates the union of the Omim diseases
        attached to the HPO Terms in this set

        Returns
        -------
        set of :class:`annotations.Omim`
            Set of all Omim diseases associated with the HPOTerms in the set
        """
        orphas = set()
        for term in self:
            orphas.update(term.orpha_diseases)
        return orphas

    def decipher_diseases(self):
        """
        Calculates the union of the Omim diseases
        attached to the HPO Terms in this set

        Returns
        -------
        set of :class:`annotations.Omim`
            Set of all Omim diseases associated with the HPOTerms in the set
        """
        deciphers = set()
        for term in self:
            deciphers.update(term.decipher_diseases)
        return deciphers

    def information_content(self, kind=None):
        """
        Gives back basic information content stats about the
        HPOTerms within the set

        Parameters
        ----------
        kind: str, default: ``omim``
            Which kind of information content should be calculated.
            Options are ['omim', 'orpha', 'decipher', 'gene']


        Returns
        -------
        dict
            Dict with the following items

            * **mean** - float - Mean information content
            * **max** - float - Maximum information content value
            * **total** - float - Sum of all information content values
            * **all** - list of float -
              List with all information content values
        """
        if kind is None:
            kind = 'omim'

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
        for term_a in self._list:
            for term_b in self._list:
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
        for i, term_a in enumerate(self._list):
            for term_b in self._list[i+1:]:
                yield (term_a, term_b)

    def similarity(self, other, kind=None, method=None, combine='funSimAvg'):
        """
        Calculates the similarity to another HPOSet
        According to Robinson et al, American Journal of Human Genetics, (2008)
        and Pesquita et al, BMC Bioinformatics, (2008)

        Parameters
        ----------
        other: HPOSet
            Another HPOSet to measure the similarity to

        kind: str, default ``None``
            Which kind of information content should be calculated.
            Options are ['omim', 'orpha', 'decipher', 'gene']
            See :func:`pyhpo.HPOTerm.similarity_score` for options

        method: string, default ``None``
            The method to use to calculate the similarity.
            See :func:`pyhpo.HPOTerm.similarity_score` for options

            Additional options:

            * **equal** - Calculates exact matches between both sets

        combine: string, default ``funSimAvg``
            The method to combine similarity measures.

            Available options:

            * **funSimAvg** - Schlicker A, BMC Bioinformatics, (2006)
            * **funSimMax** - Schlicker A, BMC Bioinformatics, (2006)
            * **BMA** - Deng Y, et. al., PLoS One, (2015)

        Returns
        -------
        float
            The similarity score to the other HPOSet

        """
        if method == 'equal':
            return self._equality_score(other)

        score_matrix = HPOSet._sim_score(self, other, kind, method)

        row_maxes = [
            max([v for v in row])
            for row in score_matrix.rows
        ]

        col_maxes = [
            max([v for v in col])
            for col in score_matrix.columns
        ]

        if combine == 'funSimAvg':
            return (
                sum(row_maxes)/len(row_maxes) +
                sum(col_maxes)/len(col_maxes)
            )/2

        if combine == 'funSimMax':
            return max([
                sum(row_maxes)/len(row_maxes),
                sum(col_maxes)/len(col_maxes)
            ])

        if combine == 'BMA':
            return (
                (sum(row_maxes) + sum(col_maxes)) /
                (len(row_maxes) + len(col_maxes))
            )

        raise RuntimeError('Invalid combine method specified')

    def _equality_score(self, other):
        """
        Returns an equality similarity score.
        Only exact matches between both sets are counted
        and the fraction of exact matches is returned.
        A score of 1 means both sets match 100%,
        0.5 means only half the terms have an exact match.

        This method does not take advantage of the ontology
        and does not take distance measures into account.

        Parameters
        ----------
        other: HPOSet
            Another HPOSet to measure the similarity to

        Returns
        -------
        float
            The similarity score to the other HPOSet

        """
        if not len(self) or not len(other):
            return 0

        matches = 0
        for term1 in self:
            for term2 in other:
                if term1 == term2:
                    matches += 1
        return matches / max([len(self), len(other)])

    @staticmethod
    def _sim_score(set1, set2, kind=None, method=None):
        """
        Calculates similarity matrix between HPOSets

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
            See :function:`pyhpo.HPOTerm.similarity_score` for options

        method: string
            The method to use to calculate the similarity.
            See :function:`pyhpo.HPOTerm.similarity_score` for options

        Returns
        -------
        float
            The one-way similarity from one to the other HPOSet

        """

        if not len(set1) or not len(set2):
            return Matrix(0, 0)

        scores = []
        for set1_term in set1:
            for set2_term in set2:
                scores.append(
                    set1_term.similarity_score(set2_term, kind, method)
                )

        return Matrix(len(set1), len(set2), scores)

    @classmethod
    def from_queries(cls, queries):
        """
        Builds an HPO set by specifying a list of queries to run on the
        :class:`pyhpo.ontology.Ontology`

        Parameters
        ----------
        queries: list of (string or int)
            The queries to be run the identify the HPOTerm from the ontology

        Returns
        -------
        :class:`pyhpo.set.HPOSet`
            A new HPOset

        Examples
        --------
            ::

                ci = HPOSet([
                    'Scoliosis',
                    'HP:0001234',
                    12
                ])

        """
        return cls([
            Ontology.get_hpo_object(query) for query in queries
        ])

    @classmethod
    def from_serialized(cls, pickle):
        """
        Re-Builds an HPO set from a serialized HPOSet object

        Parameters
        ----------
        pickle: str
            The serialized HPOSet object

        Returns
        -------
        :class:`pyhpo.set.HPOSet`
            A new HPOset

        Examples
        --------
            ::

                ci = HPOSet(ontology, '12+24+66628')

        """
        return cls([
            Ontology[int(query)] for query in pickle.split('+')
        ])

    def serialize(self):
        """
        Creates a string serialization that can be used to
        rebuild the same HPOSet via :func:`pyhpo.set.HPOSet.from_serialized`

        Returns
        -------
        str
            A string representation of the HPOSet

        """
        ids = [str(x) for x in sorted([int(x) for x in self])]
        return '+'.join(ids)

    def toJSON(self, verbose=False):
        """
        Creates a JSON-like object of the HPOSet

        Parameters
        ----------
        verbose: bool, default ``False``
            Include extra properties of the HPOTerm

        Returns
        -------
        list of dict
            a list of HPOTerm dict objects

        """
        return [t.toJSON(verbose) for t in self]

    def __str__(self):
        return '{}: {}'.format(
            self.__class__.__name__,
            ', '.join([x.name for x in self])
        )

    def __repr__(self):
        return '{}.from_serialized("{}")'.format(
            self.__class__.__name__,
            self.serialize()
        )


class BasicHPOSet(HPOSet):
    """
    Child of :class:`.HPOSet` that automatically:

    * removes parent terms
    * removes modifier terms
    * replaces obsolete terms
    """

    def __init__(self, items):
        HPOSet.__init__(self, [])
        for item in items:
            self.add(item)

    def add(self, item):
        """
        Overwrites ``set.add`` to ensure we keep the
        ``self._list`` property updated and
        don't add modifiers, obsolete or parent terms
        as well
        """
        if item in self:
            return self
        if item.is_modifier:
            return self
        for term in self:
            if item.parent_of(term):
                return self
        for p in item.all_parents:
            if p in self:
                self.remove(p)
        set.add(self, item)
        self._list.append(item)
