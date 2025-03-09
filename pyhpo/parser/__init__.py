import pyhpo
from pyhpo.parser import diseases
from pyhpo.parser import genes


def build_ontology_annotations(
    data_folder: str, ontology: "pyhpo.OntologyClass", transitive: bool = False
) -> None:
    """
    Builds all annotations and associated genes and diseases
    to the HPO terms in the Ontology.

    Parameters
    ----------
    data_folder:
        The full path to the folder that contains the master data files

    ontology:
        The ontology of HPO terms
    """
    if transitive:
        genes._parse_genes_transitive(data_folder)
    else:
        genes._parse_genes(data_folder)

    genes._add_genes_to_ontology(ontology)

    diseases._parse_phenotype_hpoa_file(data_folder)
    diseases._add_decipher_to_ontology(ontology)
    diseases._add_omim_to_ontology(ontology)
    diseases._add_orpha_to_ontology(ontology)
