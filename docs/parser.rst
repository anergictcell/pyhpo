Parser
======

The ``parser`` section contains functions to parse the master data,
such as ``hpo.obo`` and ``phenotype...`` files. These methods should
mostly be left untouched and there is very little need for client-side
code to interact with these methods. The documentation here is mostly
for developers of the library.

Public methods
**************

build_ontology_annotations
--------------------------
.. autofunction:: pyhpo.parser.build_ontology_annotations

id_from_string
--------------
.. autofunction:: pyhpo.parser.generics.id_from_string

remove_outcommented_rows
------------------------
.. autofunction:: pyhpo.parser.generics.remove_outcommented_rows


add_decipher_to_term
--------------------
.. autofunction:: pyhpo.parser.diseases.add_decipher_to_term

add_negative_decipher_to_term
-----------------------------
.. autofunction:: pyhpo.parser.diseases.add_negative_decipher_to_term

add_omim_to_term
----------------
.. autofunction:: pyhpo.parser.diseases.add_omim_to_term

add_negative_omim_to_term
-------------------------
.. autofunction:: pyhpo.parser.diseases.add_negative_omim_to_term

add_orpha_to_term
-----------------
.. autofunction:: pyhpo.parser.diseases.add_orpha_to_term

add_negative_orpha_to_term
--------------------------
.. autofunction:: pyhpo.parser.diseases.add_negative_orpha_to_term

all_decipher_diseases
---------------------
.. autofunction:: pyhpo.parser.diseases.all_decipher_diseases

all_omim_diseases
-----------------
.. autofunction:: pyhpo.parser.diseases.all_omim_diseases

all_orpha_diseases
------------------
.. autofunction:: pyhpo.parser.diseases.all_orpha_diseases

add_gene_to_term
----------------
.. autofunction:: pyhpo.parser.genes.add_gene_to_term

all_genes
---------
.. autofunction:: pyhpo.parser.genes.all_genes

terms_from_file
---------------
.. autofunction:: pyhpo.parser.obo.terms_from_file

parse_obo_section
-----------------
.. autofunction:: pyhpo.parser.obo.parse_obo_section