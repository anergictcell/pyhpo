Welcome to PyHPO's documentation!
=================================

.. toctree::
    :maxdepth: 1
    :caption: Contents:

    hpoterm
    ontology
    annotations
    set


PyHPO is a python library to work with the Human Phenotype Ontology. It represents the ontology in a dynamic way and allows graph traversal and similarity features.

In addition, it allows to compile sets of HPO Terms and analyze them in various ways.


Examples
--------

.. code-block:: python

    # Initialize an Ontology

    ontology = pyhpo.Ontology()

    # Iterate through all HPO terms
    for term in ontology:
        # do something

    # Retrieve a term via its HPO-ID
    term = ontology.get_hpo_object('HP:0002650')

    # ...or via the Integer representation of the ID
    term = ontology.get_hpo_object(2650)

    # ...or via shortcut
    term = ontology[2650]

    # ...or by term name
    term = ontology.get_hpo_object('Scoliosis')

    # Export a Pandas Datafreame
    df = ontology.to_dataframe()

    # Fulltext search on term names and synonyms
    for term in ontology.search('Abn'):
        print(term.name)


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


Working with Sets
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

    # Calculate the similarity of two Sets
    sim_score = clinical_info.similarity(other_set)



Installation
------------
The easiest way to install PyHPO is via pip

.. code:: bash

    pip install pyhpo

.. note::

    Some features of PyHPO require ``pandas``. The standard installation via pip will not include pandas and PyHPO will work just fine. (You will get a warning on the initial import though). As long as you don't try to create a ``pandas.DataFrame``, everything should work without pandas. If you want to use all features, install ``pandas`` yourself:

    .. code:: bash

        pip install pandas


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

