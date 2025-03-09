import csv
import os
from typing import Set

from pyhpo.annotations import Gene, GeneSingleton
from pyhpo.parser.generics import id_from_string, remove_outcommented_rows
import pyhpo


FILENAME_TRANSITIVE = "phenotype_to_genes.txt"
FILENAME = "genes_to_phenotype.txt"

# Cloumn mappings in phenotype_to_genes file
# HP:6001052    Tibiotalar synostosis   8200    GDF5    OMIM:200700
HPO_ID_TRANSITIVE = 0
HGNC_ID_TRANSITIVE = 2
GENE_SYMBOL_TRANSITIVE = 3

# Cloumn mappings in genes_to_phenotype file
# 10  NAT2    HP:0000007  Autosomal recessive inheritance         -       OMIM:243400
HPO_ID = 2
HGNC_ID = 0
GENE_SYMBOL = 1


def _parse_genes(path: str) -> None:
    Gene.clear()
    filename = os.path.join(path, FILENAME)
    with open(filename) as fh:
        reader = csv.reader(
            remove_outcommented_rows(
                remove_outcommented_rows(fh), ignorechar="ncbi_gene_id"
            ),
            delimiter="\t",
        )
        for cols in reader:
            gene = Gene(hgncid=int(cols[HGNC_ID]), symbol=cols[GENE_SYMBOL])
            gene.hpo.add(id_from_string(cols[HPO_ID]))


def _parse_genes_transitive(path: str) -> None:
    Gene.clear()
    filename = os.path.join(path, FILENAME_TRANSITIVE)
    with open(filename) as fh:
        reader = csv.reader(
            # ncbi_gene_id
            remove_outcommented_rows(remove_outcommented_rows(fh), ignorechar="hpo_id"),
            delimiter="\t",
        )
        for cols in reader:
            gene = Gene(
                hgncid=int(cols[HGNC_ID_TRANSITIVE]),
                symbol=cols[GENE_SYMBOL_TRANSITIVE],
            )
            gene.hpo.add(id_from_string(cols[HPO_ID_TRANSITIVE]))


def _add_genes_to_ontology(ontology: "pyhpo.OntologyClass") -> None:
    ontology._genes = all_genes()
    for gene in ontology._genes:
        for term_id in gene.hpo:
            add_gene_to_term(gene, ontology[term_id])


def add_gene_to_term(gene: "pyhpo.GeneSingleton", term: "pyhpo.HPOTerm") -> None:
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


def all_genes() -> Set["GeneSingleton"]:
    return set(Gene.keys())
