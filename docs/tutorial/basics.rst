Basics
------

**PyHPO** provides and easy interface to work with the Human Phenotype Ontology. The main interface is the :doc:`ontology` object, which must be instantiated once. ``Ontology`` is designed as a singleton, so the same instance can be used across different modules.

Ontology
~~~~~~~~

``Ontology`` can be instantiated with the default master data, simply by calling

.. code:: python

    from pyhpo import Ontology

    _ = Ontology()

It can now be used across all modules. Imagine the following source code:

::

    /mymodule
      |- foo.py
      |- bar.py
      |- main.py


``foo.py``:

.. code:: python

    from pyhpo import Ontology

    def ontology_len():
        print(len(Ontology))


``bar.py``:

.. code:: python

    from pyhpo import Ontology

    def get_term_name(term_id: int) -> str:
        try:
            term = Ontology[term_id]
        except KeyError:
            print("Term not present in Ontology")
            return ""


``main.py``:

.. code:: python

    import foo
    import bar

    from pyhpo import Ontology

    # This is the only time where the Ontology is instantiated.
    _ = Ontology()

    foo.ontology_len()
    # ==> Prints the number of HPO terms in the Ontology

    bar.get_term_name(118) # ==> "Phenotypical abnormality"


This code works as expected, the ``Ontology`` singleton is shared across all modules and submodules. It must be instantiated only once. Other modules only need to import the ``Ontology`` object.


By default, ``Ontology()`` will load the HPO version provided along with the library (see the :doc:`data` section for details about how to update or change the masterdata.


The Ontology holds references to all HPO terms, genes and diseases. Since terms are the most common use-case, ``Ontology`` allows easy subsetting to retrieve terms. For this, use the integer form of the HPO-Term ID:

.. code:: python

    from pyhpo import Ontology
    _ = Ontology()

    term = Ontology[118] # ==> returns term `HP:0000118`
    

Alternatively, terms can be retrieved by using the full HPO-Term ID:

.. code:: python

    from pyhpo import Ontology
    _ = Ontology()

    term = Ontology.get_hpo_object("HP:0000118") # ==> returns term `HP:0000118`


The ``Ontology`` can also be used as an iterator, it iterates all HPO-Terms in random order:

.. code:: python

    from pyhpo import Ontology
    _ = Ontology()

    for term in Ontology:
        print(term)


HPOTerm
~~~~~~~

Another object that is a key part of **PyHPO** are the :doc:`terms`. HPOTerms are the building block of the ontology and provide a lot of relevant functionality. They hold references to all their ancestor and child terms, allowing a fast traversal of individual arms of the ontology.

.. code:: python

    from pyhpo import Ontology
    _ = Ontology()

    term = Ontology[118]

    for child in term.children:
        print(f"{child}")

    for parent in term.parents:
        print(f"{parent}")

    # You can also iterate over all parents and their parents and grandparents etc.
    for ancestor in term.all_parents:
        print(f"{ancestor}")

Do not try to instantiate ``HPOTerm`` s manually. Doing this would miss all important links to parents, children, genes, diseases etc.


HPOSet
~~~~~~

:doc:`sets` are an important feature of **PyHPO** for doing patient or disease based data analysis. An HPOSet is primarily just that: A set of HPOTerms. You can use it to document the clinical information or full phenotype of a patient or to describe a disease. ``HPOSet`` work on top of Pythons standard ``set`` (``Set[HPOTerm]``) and can easily be build from such. They do, however, provide a lot of additional functionality.

HPOSets can be compared to each each other to identify similar patients or diseases. The similarity comparisons can be used for clustering patient cohorts.

.. code:: python

    from pyhpo import Ontology, HPOSet
    _ = Ontology()

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

    # Determine the similarity
    ci_1.similarity(ci_2)  # ==> 0.7593552670152157


Enrichment
~~~~~~~~~~

**PyHPO** includes statistical tests to determine the hypergeometric enrichment of linked diseases or genes in a set of HPOTerms. You can use this to find genes that are relevant for the phenotype of a patient. More examples are documented in :doc:`enrichment`.
