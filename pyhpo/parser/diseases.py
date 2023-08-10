import csv
import os
from typing import Set

from pyhpo.annotations import DiseaseDict
from pyhpo.annotations import Decipher, Omim, Orpha
from pyhpo.annotations import DecipherDisease, OmimDisease, OrphaDisease
from pyhpo.parser.generics import id_from_string, remove_outcommented_rows
import pyhpo


FILENAME = 'phenotype.hpoa'
# Cloumn mappings in phenotype_to_genes file
DISEASE_ID = 0
DISEASE_NAME = 1
QUALIFIER = 2
HPO_ID = 3


def _parse_phenotype_hpoa_file(path: str) -> None:
    Omim.clear()
    Orpha.clear()
    Decipher.clear()
    filename = os.path.join(path, FILENAME)
    with open(filename) as fh:
        reader = csv.reader(
            remove_outcommented_rows(
                remove_outcommented_rows(fh),
                ignorechar="database_id"
            ),
            delimiter='\t'
        )
        for cols in reader:
            disease_class: DiseaseDict = DiseaseDict()
            phenotype_source, phenotype_id = cols[DISEASE_ID].split(':')
            if phenotype_source == 'OMIM':
                disease_class = Omim
            elif phenotype_source == 'ORPHA':
                disease_class = Orpha
            elif phenotype_source == 'DECIPHER':
                disease_class = Decipher
            else:
                continue

            disease = disease_class(
                diseaseid=int(phenotype_id),
                name=cols[DISEASE_NAME]
            )

            if cols[QUALIFIER] == '':
                disease.hpo.add(id_from_string(cols[HPO_ID]))
            elif cols[QUALIFIER] == 'NOT':
                disease.negative_hpo.add(id_from_string(cols[HPO_ID]))


def _add_decipher_to_ontology(ontology: 'pyhpo.OntologyClass') -> None:
    ontology._decipher_diseases = all_decipher_diseases()
    for decipher in ontology._decipher_diseases:
        for term_id in decipher.hpo:
            add_decipher_to_term(decipher, ontology[term_id])
        for term_id in decipher.negative_hpo:
            add_negative_decipher_to_term(decipher, ontology[term_id])


def _add_omim_to_ontology(ontology: 'pyhpo.OntologyClass') -> None:
    ontology._omim_diseases = all_omim_diseases()
    for omim in ontology._omim_diseases:
        for term_id in omim.hpo:
            add_omim_to_term(omim, ontology[term_id])
        for term_id in omim.negative_hpo:
            add_negative_omim_to_term(omim, ontology[term_id])


def _add_orpha_to_ontology(ontology: 'pyhpo.OntologyClass') -> None:
    ontology._orpha_diseases = all_orpha_diseases()
    for orpha in ontology._orpha_diseases:
        for term_id in orpha.hpo:
            add_orpha_to_term(orpha, ontology[term_id])
        for term_id in orpha.negative_hpo:
            add_negative_orpha_to_term(orpha, ontology[term_id])


def add_decipher_to_term(
    decipher: 'pyhpo.annotations.DecipherDisease',
    term: 'pyhpo.HPOTerm'
) -> None:
    """
    Recursive function to add Decipher Disease
    to an HPOTerm and all its parents

    Parameters
    ----------
    decipher:
        Disease to add to term
    term:
        HPOTerm that is associated with diseease
    """
    if decipher in term.decipher_diseases:
        return None
    term.decipher_diseases.add(decipher)
    for parent in term.parents:
        add_decipher_to_term(decipher, parent)
    return None


def add_negative_decipher_to_term(
    decipher: 'pyhpo.annotations.DecipherDisease',
    term: 'pyhpo.HPOTerm'
) -> None:
    """
    Recursive function to add excluded Decipher Disease
    to an HPOTerm and all its parents

    Parameters
    ----------
    decipher:
        Disease to exclude from term
    term:
        HPOTerm that is not associated with diseease
    """
    if decipher in term.decipher_excluded_diseases:
        return None
    term.decipher_excluded_diseases.add(decipher)
    for child in term.children:
        add_negative_decipher_to_term(decipher, child)
    return None


def add_omim_to_term(
    omim: 'pyhpo.annotations.OmimDisease',
    term: 'pyhpo.HPOTerm'
) -> None:
    """
    Recursive function to add OMIM Disease
    to an HPOTerm and all its parents

    Parameters
    ----------
    omim:
        Disease to add to term
    term:
        HPOTerm that is associated with diseease
    """
    if omim in term.omim_diseases:
        return None
    term.omim_diseases.add(omim)
    for parent in term.parents:
        add_omim_to_term(omim, parent)
    return None


def add_negative_omim_to_term(
    omim: 'pyhpo.annotations.OmimDisease',
    term: 'pyhpo.HPOTerm'
) -> None:
    """
    Recursive function to add excluded OMIM Disease
    to an HPOTerm and all its parents

    Parameters
    ----------
    omim:
        Disease to exclude from term
    term:
        HPOTerm that is not associated with diseease
   """
    if omim in term.omim_excluded_diseases:
        return None
    term.omim_excluded_diseases.add(omim)
    for child in term.children:
        add_negative_omim_to_term(omim, child)
    return None


def add_orpha_to_term(
    orpha: 'pyhpo.annotations.OrphaDisease',
    term: 'pyhpo.HPOTerm'
) -> None:
    """
    Recursive function to add Orpha Disease
    to an HPOTerm and all its parents

    Parameters
    ----------
    orpha:
        Disease to add to term
    term:
        HPOTerm that is associated with diseease
    """
    if orpha in term.orpha_diseases:
        return None
    term.orpha_diseases.add(orpha)
    for parent in term.parents:
        add_orpha_to_term(orpha, parent)
    return None


def add_negative_orpha_to_term(
    orpha: 'pyhpo.annotations.OrphaDisease',
    term: 'pyhpo.HPOTerm'
) -> None:
    """
    Recursive function to add excluded Orpha Disease
    to an HPOTerm and all its parents

    Parameters
    ----------
    orpha:
        Disease to exclude from term
    term:
        HPOTerm that is not associated with diseease
    """
    if orpha in term.orpha_excluded_diseases:
        return None
    term.orpha_excluded_diseases.add(orpha)
    for child in term.children:
        add_negative_orpha_to_term(orpha, child)
    return None


def all_decipher_diseases() -> Set['DecipherDisease']:
    return set(Decipher.keys())


def all_omim_diseases() -> Set['OmimDisease']:
    return set(Omim.keys())


def all_orpha_diseases() -> Set['OrphaDisease']:
    return set(Orpha.keys())
