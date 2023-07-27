*****
PyHPO
*****

A Python library to work with, analyze, filter and inspect the `Human Phenotype Ontology`_

Visit the `PyHPO Documentation`_ for a more detailed overview of all the functionality.

.. _Human Phenotype Ontology: https://hpo.jax.org/
.. _PyHPO Documentation: https://pyhpo.readthedocs.io/en/latest/

Main features
=============

* 👫 Identify patient cohorts based on clinical features
* 👨‍👧‍👦 Cluster patients or other clinical information for GWAS
* 🩻→🧬 Phenotype to Genotype studies
* 🍎🍊 HPO similarity analysis
* 🕸️ Graph based analysis of phenotypes, genes and diseases


**PyHPO** allows working on individual terms ``HPOTerm``, a set of terms ``HPOSet`` and the full ``Ontology``.

The library is helpful for discovery of novel gene-disease associations and GWAS data analysis studies. At the same time, it can be used for oragnize clinical information of patients in research or diagnostic settings.

Internally the ontology is represented as a branched linked list, every term contains pointers to its parent and child terms. This allows fast tree traversal functionality.

It provides an interface to create ``Pandas Dataframe`` from its data, allowing integration in already existing data anlysis tools.


Getting started
===============

The easiest way to install **PyHPO** is via pip

.. code:: bash

    pip install pyhpo

or, you can additionally install optional packages for extra functionality

.. code:: bash

    # Include pandas during install
    pip install pyhpo[pandas]

    # Include scipy
    pip install pyhpo[scipy]

    # Include all dependencies
    pip install pyhpo[all]

.. note::

    Some features of PyHPO require ``pandas`` and ``scipy``. The standard installation via pip will not include pandas or scipy and PyHPO will work just fine. (You will get a warning on the initial import though).

    Without installing ``pandas``, you won't be able to export the Ontology as a ``Dataframe``, everything else will work fine.

    Without installing ``scipy``, you won't be able to use the ``stats`` module, especially the enrichment calculations.


Usage example
=============

Basic use cases
---------------

Some examples for basic functionality of PyHPO

How similar are the phenotypes of two patients
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from pyhpo import Ontology
    from pyhpo.set import HPOSet

    # initilize the Ontology ()
    _ = Ontology()

    # Declare the clinical information of the patients
    patient_1 = HPOSet.from_queries([
        'HP:0002943',
        'HP:0008458',
        'HP:0100884',
        'HP:0002944',
        'HP:0002751'
    ])

    patient_2 = HPOSet.from_queries([
        'HP:0002650',
        'HP:0010674',
        'HP:0000925',
        'HP:0009121'
    ])

    # and compare their similarity
    patient_1.similarity(patient_2)
    #> 0.7594183905785477


How close are two HPO terms
^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code:: python

    from pyhpo import Ontology

    # initilize the Ontology ()
    _ = Ontology()

    term_1 = Ontology.get_hpo_object('Scoliosis')
    term_2 = Ontology.get_hpo_object('Abnormal axial skeleton morphology')

    path = term_1.path_to_other(term_2)
    for t in path[1]:
        print(t)

    """
    HP:0002650 | Scoliosis
    HP:0010674 | Abnormality of the curvature of the vertebral column
    HP:0000925 | Abnormality of the vertebral column
    HP:0009121 | Abnormal axial skeleton morphology
    """


HPOTerm
-------
An ``HPOTerm`` contains various metadata about the term, as well as pointers to its parents and children terms. You can access its information-content, calculate similarity scores to other terms, find the shortest or longes connection between two terms. List all associated genes or diseases, etc.

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


Some additional functionality, working with more than one term

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

Examples
^^^^^^^^

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

The Ontology is a Singleton and should only be initiated once.
It can be reused across several modules, e.g:

``main.py``

.. code:: python

    from pyhpo import Ontology, HPOSet

    import module2

    # initilize the Ontology
    _ = Ontology()

    if __name__ == '__main__':
        module2.find_term('Compensatory scoliosis')


``module2.py``

.. code:: python

    from pyhpo import Ontology

    def find_term(term):
        return Ontology.get_hpo_object(term)


HPOSet
------
An ``HPOSet`` is a collection of ``HPOTerm`` and can be used to represent e.g. a patient's clinical information. It provides APIs for filtering, comparisons to other ``HPOSet`` and term/gene/disease enrichments.


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


Get genes enriched in an ``HPOSet``
-----------------------------------

Examples:
^^^^^^^^^

.. code:: python

    from pyhpo import Ontology, HPOSet
    from pyhpo.stats import EnrichmentModel

    # initilize the Ontology
    _ = Ontology()

    ci = HPOSet.from_queries([
        'HP:0002943',
        'HP:0008458',
        'HP:0100884',
        'HP:0002944',
        'HP:0002751'
    ])

    gene_model = EnrichmentModel('gene')
    genes = gene_model.enrichment(method='hypergeom', hposet=ci)
    
    print(genes[0]['item'])
    #> PAPSS2

*(This script is complete, it should run "as is")*


For a more detailed description of how to use PyHPO, visit the `PyHPO Documentation <https://pyhpo.readthedocs.io/en/latest/>`_.



Contributing
============

Yes, please do so. We appreciate any help, suggestions for improvement or other feedback. Just create a pull-request or open an issue.

License
=======

PyHPO is released under the `MIT license`_.


PyHPO is using the Human Phenotype Ontology. Find out more at http://www.human-phenotype-ontology.org

Sebastian Köhler, Leigh Carmody, Nicole Vasilevsky, Julius O B Jacobsen, et al. Expansion of the Human Phenotype Ontology (HPO) knowledge base and resources. Nucleic Acids Research. (2018) doi: 10.1093/nar/gky1105

.. _MIT license: http://www.opensource.org/licenses/mit-license.php
