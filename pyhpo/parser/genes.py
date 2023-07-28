import csv
import os
from typing import Set

from pyhpo.annotations import Gene, GeneSingleton
from pyhpo.parser.generics import id_from_string, remove_outcommented_rows
import pyhpo


FILENAME = 'phenotype_to_genes.txt'
# Cloumn mappings in phenotype_to_genes file
HPO_ID = 0
HGNC_ID = 2
GENE_SYMBOL = 3


def _parse_phenotype_to_gene_file(path: str) -> None:
    Gene.clear()
    filename = os.path.join(path, FILENAME)
    with open(filename) as fh:
        reader = csv.reader(
            remove_outcommented_rows(
                remove_outcommented_rows(fh),
                ignorechar="hpo_id"
            ),
            delimiter='\t'
        )
        for cols in reader:
            gene = Gene(
                hgncid=int(cols[HGNC_ID]),
                symbol=cols[GENE_SYMBOL]
            )
            gene.hpo.add(id_from_string(cols[HPO_ID]))


def _add_genes_to_ontology(ontology: 'pyhpo.OntologyClass') -> None:
    ontology._genes = all_genes()
    for gene in ontology._genes:
        for term_id in gene.hpo:
            add_gene_to_term(gene, ontology[term_id])


def add_gene_to_term(
    gene: 'pyhpo.annotations.GeneSingleton',
    term: 'pyhpo.HPOTerm'
) -> None:
    """
    Recursive function to add Gene to an HPOTerm and all its parents

    Parameters
    ----------
    gene:
        Gene to add to term
    term:
        HPOTerm that is associated with the gene
    """
    if gene in term.genes:
        return None
    term.genes.add(gene)
    for parent in term.parents:
        add_gene_to_term(gene, parent)
    return None


def all_genes() -> Set['GeneSingleton']:
    return set(Gene.keys())
