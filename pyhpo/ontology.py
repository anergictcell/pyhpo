import os
import math
import warnings
from typing import List, Set, Tuple, Optional, Union, Dict, Iterator

try:
    import pandas as pd  # type: ignore
except ImportError:
    warnings.warn(
        'Some functionality requires pandas, which is currently not available',
        UserWarning)

import pyhpo
from pyhpo import HPOTerm
from pyhpo.parser import build_ontology_annotations
from pyhpo.parser.obo import terms_from_file
from pyhpo.parser.generics import id_from_string


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
        data_folder: Optional[str] = None,
        from_obo_file: bool = True
    ) -> 'OntologyClass':
        self.metadata: List[str] = []
        self._map: Dict[int, HPOTerm] = {}
        self._genes: Set['pyhpo.GeneSingleton'] = set()
        self._omim_diseases: Set['pyhpo.OmimDisease'] = set()
        self._orpha_diseases: Set['pyhpo.OrphaDisease'] = set()
        self._decipher_diseases: Set['pyhpo.DecipherDisease'] = set()

        if data_folder is None:
            data_folder = os.path.join(os.path.dirname(__file__), 'data')

        if from_obo_file:
            self._load_from_obo_file(data_folder)

        return self

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

        Raises
        ------
        RuntimeError
            No HPO term is found for the provided query
        TypeError
            The provided query is an unsupported type and can't be properly
            converted
        ValueError
            The provided HPO ID cannot be converted to the correct
            integer representation

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
                try:
                    res = self[id_from_string(query)]
                except ValueError as err:
                    raise ValueError(f'Invalid id: {query}') from err
                except KeyError:
                    pass
            else:
                try:
                    res = self.synonym_match(query)
                except RuntimeError:
                    pass

        elif isinstance(query, int):
            try:
                res = self[query]
            except KeyError:
                pass

        else:
            raise TypeError('Invalid type {} for parameter "query"'.format(
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
            if (
                query.lower() in term.name.lower()
            ) or (
                self.synonym_search(term, query)
            ):
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
            if query.lower() in synonym.lower():
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

        data: Dict[str, List[Union[float, int, str]]] = {
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
            data['ic_omim'].append(term.information_content.omim)
            data['ic_orpha'].append(term.information_content.orpha)
            data['ic_decipher'].append(term.information_content.decipher)
            data['ic_gene'].append(term.information_content.gene)
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
    def decipher_diseases(self) -> Set['pyhpo.DecipherDisease']:
        return self._decipher_diseases

    @property
    def omim_diseases(self) -> Set['pyhpo.OmimDisease']:
        return self._omim_diseases

    @property
    def orpha_diseases(self) -> Set['pyhpo.OrphaDisease']:
        return self._orpha_diseases

    def _load_from_obo_file(
        self,
        data_folder: str
    ) -> None:
        """
        Reads an obo file line by line to add
        HPO terms to the Ontology

        Attributes
        ----------
        data_folder: str
            Full path to folder where master data is stored

        """
        for term in terms_from_file(data_folder):
            self._append(HPOTerm(**term))

        self._connect_all()
        build_ontology_annotations(data_folder, self)  # type: ignore
        self._add_information_content()

    def _append(self, item: HPOTerm) -> None:
        """
        Adds one HPO term to the ontology
        """
        self._map[item.index] = item

    def _connect_all(self) -> None:
        """
        Connects all parent-child associations in the Ontology
        Called by default after loading the ontology from a file
        """
        for term in self._map.values():
            for parent_id in term.parent_ids():
                parent = self[parent_id]
                term.parents.add(parent)
                parent.children.add(term)

        # Build caches of hierarchy to speed up performance
        for term in self._map.values():
            term.all_parents

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
                term.information_content.omim = 0
            else:
                term.information_content.omim = -math.log(p_omim)

            if p_orpha == 0:
                term.information_content.orpha = 0
            else:
                term.information_content.orpha = -math.log(p_orpha)

            if p_decipher == 0:
                term.information_content.decipher = 0
            else:
                term.information_content.decipher = -math.log(p_decipher)

            if p_gene == 0:
                term.information_content.gene = 0
            else:
                term.information_content.gene = -math.log(p_gene)

    def __getitem__(self, key: int) -> HPOTerm:
        try:
            return self._map[key]
        except KeyError as e:
            raise KeyError('No HPOTerm for index {}'.format(key)) from e

    def __iter__(self) -> Iterator[HPOTerm]:
        return iter(self._map.values())

    def __len__(self) -> int:
        return len(self._map.keys())


Ontology: OntologyClass = OntologyClass()
