from pyhpo.parser import diseases
from pyhpo.parser import genes
import pyhpo


def build_ontology_annotations(
    data_folder: str,
    ontology: 'pyhpo.ontology.OntologyClass'
) -> None:
    genes._parse_phenotype_to_gene_file(data_folder)
    genes._add_genes_to_ontology(ontology)

    diseases._parse_phenotype_hpoa_file(data_folder)
    diseases._add_decipher_to_ontology(ontology)
    diseases._add_omim_to_ontology(ontology)
    diseases._add_orpha_to_ontology(ontology)
