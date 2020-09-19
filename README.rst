*****
PyHPO
*****

A Python library to work with, analyze, filter and inspect the `Human Phenotype Ontology`_

Visit the `PyHPO Documentation`_ for a more detailed overview of all the functionality.


Main features
=============

It allows working on individual terms ``HPOTerm``, a set of terms ``HPOSet`` and the full ``Ontology``.

Internally the ontology is represented as a branched linked list, every term contains pointers to its parent and child terms. This allows fast tree traversal functioanlity.

The library is helpful for discovery of novel gene-disease associations and GWAS data analysis studies. At the same time, it can be used for oragnize clinical information of patients in research or diagnostic settings.

It provides an interface to create ``Pandas Dataframe`` from its data, allowing integration in already existing data anlysis tools.


HPOTerm
-------
An individual ``HPOTerm`` contains all info about itself as well as pointers to its parents and its children. You can access its information-content, calculate similarity scores to other terms, find the shortest or longes connection between two terms. List all associated genes or diseases, etc.

HPOSet
------
An ``HPOSet`` can be used to represent e.g. a patient's clinical information. It allows some basic filtering and comparisons to other ``HPOSet`` s.

Ontology
--------
The ``Ontology`` represents all HPO terms and their connections and associations. It also contains pointers to associated genes and disease.


Installation / Setup
====================

The easiest way to install PyHPO is via pip

.. code:: bash

    pip install pyhpo

.. note::

    Some features of PyHPO require ``pandas``. The standard installation via pip will not include pandas and PyHPO will work just fine. (You will get a warning on the initial import though). As long as you don't try to create a ``pandas.DataFrame``, everything should work without pandas. If you want to use all features, install ``pandas`` yourself:

    .. code:: bash

        pip install pandas

Usage
=====

For a detailed description of how to use PyHPO, visit the `PyHPO Documentation`_.

Getting started
---------------

.. code:: python

    from pyhpo.ontology import Ontology

    # initilize the Ontology (you can specify config parameters if needed here)
    ontology = Ontology()
    
    # Iterate through all HPO terms
    for term in ontology:
        # do something, e.g.
        print(term.name)

There are multiple ways to retrieve a single term out of an ontology:

.. code:: python

    # Retrieve a term via its HPO-ID
    term = ontology.get_hpo_object('HP:0002650')

    # ...or via the Integer representation of the ID
    term = ontology.get_hpo_object(2650)

    # ...or via shortcut
    term = ontology[2650]

    # ...or by term name
    term = ontology.get_hpo_object('Scoliosis')

You can also do substring search on term names and synonyms:

.. code:: python

    # ontology.search returns an Iterator over all matches
    for term in ontology.search('Abn'):
        print(term.name)

Find the shortest path between two terms:

.. code:: python

    ontology.path(
        'Abnormality of the nervous system',
        'HP:0002650'
    )

Working with terms
------------------

.. code-block:: python

    # check the relationship of two terms
    term.path_to_other(ontology[11])

    # get the information content for OMIM diseases
    term.information_content['omim']

    # ...or for genes
    term.information_content['genes']

    # compare two terms
    term.similarity_score(term2, method='resnik', kind='gene')

Working with sets
-----------------

.. code-block:: python

    # Create a clinical information set of HPO Terms
    clinical_info = pyhpo.HPOSet([
        ontology[12],
        ontology[14],
        ontology.get_hpo_object(2650)
    ])

    # Extract only child nodes and leave out all parent terms
    children = clinical_info.child_nodes()

    # Remove HPO modifier terms
    new_ci = clinical_info.remove_modifier()

    # Calculate the similarity of two Sets
    sim_score = clinical_info.similarity(other_set)

Statistics
-----------------
``PyHPO`` includes some basic statics method for gene, disease and HPO-Term enrichment analysis.


.. code-block:: python

    # Let's say you have a patient with a couple of symptoms and 
    # you want to find out the most likely affected genes 
    # or most likely diseases
    
    from pyhpo import stats
    from pyhpo.ontology import Ontology
    from pyhpo.set import HPOSet, BasicHPOSet
    _ = Ontology()

    hpo_terms = [
        'Decreased circulating antibody level',
        'Abnormal immunoglobulin level',
        'Abnormality of B cell physiology',
        'Abnormal lymphocyte physiology',
        'Abnormality of humoral immunity',
        'Lymphoma',
        'Lymphopenia',
        'Autoimmunity',
        'Increased circulating IgG level',
        'Abnormal lymphocyte count'
    ]
    
    # you can either use a HPOSet for this
    hposet = HPOSet.from_queries(hpo_terms)
    
    # or just a plain list of HPO Terms
    hposet = [Ontology.match(q) for q in hpo_terms]
    
    # Initialize an Enrichment model for genes
    gene_model = stats.EnrichmentModel('gene')
    
    # You can also do enrichment for diseases
    disease_model = stats.EnrichmentModel('omim')
    
    # Calculate the Hypergeometric distribution test enrichment
    gene_results = gene_model.enrichment(
        'hypergeom',
        hposet
    )
    disease_results = disease_model.enrichment(
        'hypergeom',
        hposet
    )
    
    # and print the Top-10 results
    for x in gene_results[0:10]:
        print(x)
    for x in disease_results[0:10]:
        print(x)

and many more examples in the `PyHPO Documentation`_


Contributing
============

Yes, please do so. I would appreciate any help, suggestions for improvement or other feedback. Just create a pull-request or open an issue.

License
=======

PyHPO is released under the `MIT license`_.


PyHPO is using the Human Phenotype Ontology. Find out more at http://www.human-phenotype-ontology.org

Sebastian Köhler, Leigh Carmody, Nicole Vasilevsky, Julius O B Jacobsen, et al. Expansion of the Human Phenotype Ontology (HPO) knowledge base and resources. Nucleic Acids Research. (2018) doi: 10.1093/nar/gky1105

.. _PyHPO Documentation: https://esbme.com/pyhpo/docs/ 
.. _MIT license: http://www.opensource.org/licenses/mit-license.php
.. _Human Phenotype Ontology: https://hpo.jax.org/