*****
PyHPO
*****

A Python library to work with, analyze, filter and inspect the `Human Phenotype Ontology`_

Visit the `PyHPO Documentation`_ for a more detailed overview of all the functionality.


Main features
=============

It allows working on individual terms ``HPOTerm``, a set of terms ``HPOSet`` and the full ``Ontology``.

Internally the ontology is represented as a branched linked list, every term contains pointers to its parent and child terms. This allows fast tree traversal functionality.

The library is helpful for discovery of novel gene-disease associations and GWAS data analysis studies. At the same time, it can be used for oragnize clinical information of patients in research or diagnostic settings.

It provides an interface to create ``Pandas Dataframe`` from its data, allowing integration in already existing data anlysis tools.


HPOTerm
-------
An individual :class:`pyhpo.term.HPOTerm` contains all info about itself as well as pointers to its parents and its children. You can access its information-content, calculate similarity scores to other terms, find the shortest or longes connection between two terms. List all associated genes or diseases, etc.

Examples:
^^^^^^^^^

Basic functionalities of an HPO-Term

.. code:: python

    from pyhpo import Ontology

    # initilize the Ontology ()
    _ = Ontology()

    # Retrieve a term e.g. via its HPO-ID
    term = Ontology.get_hpo_object('Scoliosis')

    print(term)
    #> HP:0002650 | Scoliosis

    # Get information content from Term <--> Omim associations
    term.information_content['omim']
    #> 2.39

    # Show how many genes are associated to the term
    # (Note that this includes indirect associations, associations
    # from children terms to genes.)
    len(term.genes)
    #> 947

    # Show how many Omim Diseases are associated to the term
    # (Note that this includes indirect associations, associations
    # from children terms to diseases.)
    len(term.omim_diseases)
    #> 730

    # Get a list of all parent terms
    for p in term.parents:
        print(p)
    #> HP:0010674 | Abnormality of the curvature of the vertebral column

    # Get a list of all children terms
    for p in term.children:
        print(p)
    """
    HP:0002943 | Thoracic scoliosis
    HP:0008458 | Progressive congenital scoliosis
    HP:0100884 | Compensatory scoliosis
    HP:0002944 | Thoracolumbar scoliosis
    HP:0002751 | Kyphoscoliosis
    """

*(This script is complete, it should run "as is")*


Some basic functionality, working with more than one term

.. code:: python

    from pyhpo import Ontology
    _ = Ontology()
    term = Ontology.get_hpo_object('Scoliosis')

    # Let's get a second term, this time using it HPO-ID
    term_2 = Ontology.get_hpo_object('HP:0009121')

    print(term_2)
    #> HP:0009121 | Abnormal axial skeleton morphology

    # Check if the Scoliosis is a direct or indirect child
    # of Abnormal axial skeleton morphology

    term.child_of(term_2)
    #> True

    # or vice versa
    term_2.parent_of(term)
    #> True

    # show all nodes between two term:
    path = term.path_to_other(term_2)
    for t in path[1]:
        print(t)

    """
    HP:0002650 | Scoliosis
    HP:0010674 | Abnormality of the curvature of the vertebral column
    HP:0000925 | Abnormality of the vertebral column
    HP:0009121 | Abnormal axial skeleton morphology
    """

    print(f'Steps from Term 1 to Term 2: {path[0]}')
    #> Steps from Term 1 to Term 2: 3


    # Calculate the similarity between two terms
    term.similarity_score(term_2)
    #> 0.442

*(This script is complete, it should run "as is")*


Ontology
--------
The ``Ontology`` contains all HPO terms, their connections to each other and associations to genes and diseases.
It provides some helper functions for ``HPOTerm`` search functionality

.. note::

    The Ontology is a Singleton and must only be initiated once.
    It can be reused across several modules.

.. code:: python

    from pyhpo import Ontology, HPOSet

    # initilize the Ontology (this must be done only once)
    _ = Ontology()

    # Get a term based on its name
    term = Ontology.get_hpo_object('Scoliosis')
    print(term)
    #> HP:0002650 | Scoliosis

    # ...or based on HPO-ID
    term = Ontology.get_hpo_object('HP:0002650')
    print(term)
    #> HP:0002650 | Scoliosis

    # ...or based on its index
    term = Ontology.get_hpo_object(2650)
    print(term)
    #> HP:0002650 | Scoliosis

    # shortcut to retrieve a term based on its index
    term = Ontology[2650]
    print(term)
    #> HP:0002650 | Scoliosis

    # Search for term
    for term in Ontology.search('olios'):
        print(term)

    """
    HP:0002211 | White forelock
    HP:0002290 | Poliosis
    HP:0002650 | Scoliosis
    HP:0002751 | Kyphoscoliosis
    HP:0002943 | Thoracic scoliosis
    HP:0002944 | Thoracolumbar scoliosis
    HP:0003423 | Thoracolumbar kyphoscoliosis
    HP:0004619 | Lumbar kyphoscoliosis
    HP:0004626 | Lumbar scoliosis
    HP:0005659 | Thoracic kyphoscoliosis
    HP:0008453 | Congenital kyphoscoliosis
    HP:0008458 | Progressive congenital scoliosis
    HP:0100884 | Compensatory scoliosis
    """

*(This script is complete, it should run "as is")*


HPOSet
------
An ``HPOSet`` is a collection of :class:`pyhpo.term.HPOTerm`s and
can be used to represent e.g. a patient's clinical information. It provides APIs for filtering, comparisons to other ``HPOSet``s and term/gene/disease enrichments.


Examples:
^^^^^^^^^

.. code:: python

    from pyhpo import Ontology, HPOSet

    # initilize the Ontology
    _ = Ontology()

    # create HPOSets, corresponding to 
    # e.g. the clinical information of a patient
    # You can initiate an HPOSet using either
    # - HPO-ID: 'HP:0002943'
    # - HPO-Name: 'Scoliosis'
    # - HPO-ID (int): 2943

    ci_1 = HPOSet.from_queries([
        'HP:0002943',
        'HP:0008458',
        'HP:0100884',
        'HP:0002944',
        'HP:0002751'
    ])

    ci_2 = HPOSet.from_queries([
        'HP:0002650',
        'HP:0010674',
        'HP:0000925',
        'HP:0009121'
    ])

    # Compare the similarity
    ci_1.similarity(ci_2)
    #> 0.7593552670152157

    # Remove all non-leave nodes from a set
    ci_leaf = ci_2.child_nodes()
    len(ci_2)
    #> 4
    len(ci_leaf)
    #> 1
    ci_2
    #> HPOSet.from_serialized("925+2650+9121+10674")
    ci_leaf
    #> HPOSet.from_serialized("2650")

    # Check the information content of an HPOSet
    ci_1.information_content()
    """
    {
        'mean': 6.571224974009769,
        'total': 32.856124870048845,
        'max': 8.97979449089521,
        'all': [5.98406221734122, 8.286647310335265, 8.97979449089521, 5.5458072864100645, 4.059813565067086]
    }
    """

*(This script is complete, it should run "as is")*


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
    _ = Ontology()
    
    # Iterate through all HPO terms
    for term in Ontology:
        # do something, e.g.
        print(term.name)

There are multiple ways to retrieve a single term out of an Ontology:

.. code:: python

    # Retrieve a term via its HPO-ID
    term = Ontology.get_hpo_object('HP:0002650')

    # ...or via the Integer representation of the ID
    term = Ontology.get_hpo_object(2650)

    # ...or by term name
    term = Ontology.get_hpo_object('Scoliosis')

    # ...or via shortcut
    term = Ontology[2650]

You can also do substring search on term names and synonyms:

.. code:: python

    # Ontology.search returns an Iterator over all matches
    for term in Ontology.search('Abn'):
        print(term.name)

Find the shortest path between two terms:

.. code:: python

    Ontology.path(
        'Abnormality of the nervous system',
        'Scoliosis'
    )

    # or use HP identifiers
    Ontology.path(
        'Abnormality of the nervous system',
        'HP:0002650'
    )

Working with terms
------------------

.. code-block:: python

    # Get a single HPO Term:
    term = Ontology.get_hpo_object('HP:0002650')

    # check the relationship of two terms
    term.path_to_other(Ontology[11])

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
        Ontology[12],
        Ontology[14],
        Ontology.get_hpo_object(2650)
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

Yes, please do so. We appreciate any help, suggestions for improvement or other feedback. Just create a pull-request or open an issue.

License
=======

PyHPO is released under the `MIT license`_.


PyHPO is using the Human Phenotype Ontology. Find out more at http://www.human-phenotype-ontology.org

Sebastian Köhler, Leigh Carmody, Nicole Vasilevsky, Julius O B Jacobsen, et al. Expansion of the Human Phenotype Ontology (HPO) knowledge base and resources. Nucleic Acids Research. (2018) doi: 10.1093/nar/gky1105

.. _PyHPO Documentation: https://centogene.github.io/pyhpo/
.. _MIT license: http://www.opensource.org/licenses/mit-license.php
.. _Human Phenotype Ontology: https://hpo.jax.org/