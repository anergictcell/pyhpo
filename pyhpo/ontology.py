import os
import math
import warnings
from typing import Set, Tuple, Optional, Union, Dict, Iterator

try:
    import pandas as pd  # type: ignore
except ImportError:
    warnings.warn(
        'Some functionality requires pandas, which is currently not available',
        UserWarning)

import pyhpo
from pyhpo import HPOTerm
from pyhpo.annotations import HPO_Gene, parse_pheno_file


class OntologyClass():
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

    def __call__(
        self,
        filename: str = 'hp.obo',
        data_folder: Optional[str] = None
    ) -> 'OntologyClass':
        self._map: Dict[int, HPOTerm] = {}
        self._genes: Set['pyhpo.GeneSingleton'] = set()
        self._omim_diseases: Set['pyhpo.DiseaseSingleton'] = set()
        self._orpha_diseases: Set['pyhpo.DiseaseSingleton'] = set()
        self._decipher_diseases: Set['pyhpo.DiseaseSingleton'] = set()
        self._omim_excluded_diseases: Set['pyhpo.DiseaseSingleton'] = set()
        self._orpha_excluded_diseases: Set['pyhpo.DiseaseSingleton'] = set()
        self._decipher_excluded_diseases: Set['pyhpo.DiseaseSingleton'] = set()

        if data_folder is None:
            data_folder = os.path.join(os.path.dirname(__file__), 'data')
        self._data_folder = data_folder

        if filename:
            self._load_from_file(os.path.join(
                data_folder,
                filename
            ))
        return self

    def add_annotations(self, data_folder: Optional[str] = None) -> None:
        warnings.warn(
            'The method `ontology.add_annotations` is deprecated. '
            'The functionality is included by default when the Ontology '
            'is loaded from file since version 1.1.',
            DeprecationWarning,
            stacklevel=2
        )

    def _add_annotations(self, data_folder: Optional[str] = None) -> None:
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
        phenotypes = parse_pheno_file(path=data_folder)
        omim_diseases = phenotypes[0]
        omim_excluded = phenotypes[1]
        orpha_diseases = phenotypes[2]
        orpha_excluded = phenotypes[3]
        decipher_diseases = phenotypes[4]
        decipher_excluded = phenotypes[5]

        for term in self:
            if term._index in genes:
                term.genes = genes[term._index]
                self._genes.update(genes[term._index])

            if term._index in omim_diseases:
                term.omim_diseases = omim_diseases[term._index]
                self._omim_diseases.update(omim_diseases[term._index])

            if term._index in orpha_diseases:
                term.orpha_diseases = orpha_diseases[term._index]
                self._orpha_diseases.update(orpha_diseases[term._index])

            if term._index in decipher_diseases:
                term.decipher_diseases = decipher_diseases[term._index]
                self._decipher_diseases.update(decipher_diseases[term._index])

            if term._index in omim_excluded:
                term.omim_excluded_diseases = omim_excluded[term._index]
                self._omim_excluded_diseases.update(
                    omim_excluded[term._index]
                )
            if term._index in orpha_excluded:
                term.orpha_excluded_diseases = orpha_excluded[term._index]
                self._orpha_excluded_diseases.update(
                    orpha_excluded[term._index]
                )
            if term._index in decipher_excluded:
                term.decipher_excluded_diseases = decipher_excluded[
                    term._index
                ]
                self._decipher_excluded_diseases.update(
                    decipher_excluded[term._index]
                )

        self._add_information_content()

    def _add_information_content(self) -> None:
        """
        Calculates the information content for each HPO Term
        According to Robinson et al, American Journal of Human Genetics, 2008
        https://www.sciencedirect.com/science/article/pii/S0002929708005351

        Returns
        -------
        None
            None
        """
        total_omim_diseases = len(self.omim_diseases)
        total_orpha_diseases = len(self.orpha_diseases)
        total_decipher_diseases = len(self.decipher_diseases)
        total_genes = len(self.genes)
        for term in self:
            p_omim = len(term.omim_diseases)/total_omim_diseases
            p_orpha = len(term.orpha_diseases)/total_orpha_diseases
            p_decipher = len(term.decipher_diseases)/total_decipher_diseases
            p_gene = len(term.genes)/total_genes
            if p_omim == 0:
                term.information_content['omim'] = 0
            else:
                term.information_content['omim'] = -math.log(p_omim)

            if p_orpha == 0:
                term.information_content['orpha'] = 0
            else:
                term.information_content['orpha'] = -math.log(p_orpha)

            if p_decipher == 0:
                term.information_content['decipher'] = 0
            else:
                term.information_content['decipher'] = -math.log(p_decipher)

            if p_gene == 0:
                term.information_content['gene'] = 0
            else:
                term.information_content['gene'] = -math.log(p_gene)

    def get_hpo_object(self, query: Union[int, str]) -> HPOTerm:
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
        res: Optional[HPOTerm] = None
        if isinstance(query, str):
            if query.startswith('HP:'):
                res = self[HPOTerm.id_from_string(query)]
            else:
                res = self.synonym_match(query)

        elif isinstance(query, int):
            res = self[query]

        else:
            raise SyntaxError('Invalid type {} for parameter "query"'.format(
                type(query)
            ))

        if res:
            return res
        else:
            raise RuntimeError('Unknown HPO term')

    def match(self, query: str) -> HPOTerm:
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

    def path(
        self,
        query1: Union[int, str],
        query2: Union[int, str]
    ) -> Tuple[int, Tuple[HPOTerm, ...], int, int]:
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

    def search(self, query: str) -> Iterator[HPOTerm]:
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

    def synonym_match(self, query: str) -> HPOTerm:
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
        raise RuntimeError('No HPO entry with term or synonym {}'.format(
            query)
        )

    def synonym_search(self, term: HPOTerm, query: str) -> bool:
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

    def to_dataframe(self) -> 'pd.DataFrame':
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

        data: Dict = {
            'id': [],
            'name': [],
            'parents': [],
            'children': [],
            'ic_omim': [],
            'ic_orpha': [],
            'ic_decipher': [],
            'ic_gene': [],
            'dTop_l': [],
            'dTop_s': [],
            'dBottom': [],
            'genes': [],
            'omim': [],
            'orpha': [],
            'decipher': []
        }

        # This is not the most elegant way to generate a DataFrame
        # But it works
        for term in self:
            data['id'].append(term.id)
            data['name'].append(term.name)
            data['parents'].append('|'.join([x.id for x in term.parents]))
            data['children'].append('|'.join([x.id for x in term.children]))
            data['ic_omim'].append(term.information_content['omim'])
            data['ic_orpha'].append(term.information_content['orpha'])
            data['ic_decipher'].append(term.information_content['decipher'])
            data['ic_gene'].append(term.information_content['gene'])
            data['dTop_l'].append(term.longest_path_to_root())
            data['dTop_s'].append(term.shortest_path_to_root())
            data['dBottom'].append(term.longest_path_to_bottom())
            data['genes'].append('|'.join([str(x) for x in term.genes]))
            data['omim'].append('|'.join([
                str(x) for x in term.omim_diseases
            ]))
            data['orpha'].append('|'.join([
                str(x) for x in term.omim_diseases
            ]))
            data['decipher'].append('|'.join([
                str(x) for x in term.omim_diseases
            ]))

        return pd.DataFrame(data).set_index('id')

    @property
    def genes(self) -> Set['pyhpo.GeneSingleton']:
        return self._genes

    @property
    def omim_diseases(self) -> Set['pyhpo.DiseaseSingleton']:
        return self._omim_diseases

    @property
    def omim_excluded_diseases(self) -> Set['pyhpo.DiseaseSingleton']:
        return self._omim_excluded_diseases

    @property
    def orpha_diseases(self) -> Set['pyhpo.DiseaseSingleton']:
        return self._orpha_diseases

    @property
    def orpha_excluded_diseases(self) -> Set['pyhpo.DiseaseSingleton']:
        return self._orpha_excluded_diseases

    @property
    def decipher_diseases(self) -> Set['pyhpo.DiseaseSingleton']:
        return self._decipher_diseases

    @property
    def decipher_excluded_diseases(self) -> Set['pyhpo.DiseaseSingleton']:
        return self._decipher_excluded_diseases

    def _append(self, item: HPOTerm) -> None:
        """
        Adds one HPO term to the ontology
        """
        self._map[item._index] = item

    def _connect_all(self) -> None:
        """
        Connects all parent-child associations in the Ontology
        Called by default after loading the ontology from a file
        """
        for term in self._map.values():
            for parent in term.parent_ids():
                term.parents = self._map[parent]  # type: ignore[assignment]
                self._map[parent].children = term  # type: ignore[assignment]

        for term in self._map.values():
            # Build caches of hierarchy to speed
            # up performance
            term.all_parents

    def _load_from_file(self, filename: str) -> None:
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
            assert term
            self._append(term)
        self._connect_all()
        self._add_annotations()

    def __getitem__(self, key: int) -> Optional[HPOTerm]:
        if key in self._map:
            return self._map[key]
        else:
            return None

    def __iter__(self) -> Iterator[HPOTerm]:
        return iter(self._map.values())

    def __len__(self) -> int:
        return len(self._map.keys())


Ontology = OntologyClass()
