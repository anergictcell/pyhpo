PyHPO
=====

A Python library to work with, analyze, filter and inspect the `Human Phenotype Ontology`_

Visit the `PyHPO Documentation`_ for a more detailed overview of all the functionality.

Main features
-------------
It allows working on individual terms ``HPOTerm``, a set of terms ``HPOSet`` and the full ``Ontology``.

Internally the ontology is represented as a branched linked list, every term contains pointers to its parent and child terms. This allows fast tree traversal functioanlity.

The library is helpful for discovery of novel gene-disease associations and GWAS data analysis studies. At the same time, it can be used for oragnize clinical information of patients in research or diagnostic settings.

It provides an interface to create ``Pandas Dataframe`` from its data, allowing integration in already existing data anlysis tools.


HPOTerm
-------
An individual ``HPOTerm`` contains all info about itself as well as pointers to its parents and its children. You can access its information-content, calculate similarity scores to other terms, find the shortest or longes connection between two terms. List all associated genes or diseases, etc.

HPOSet
------
An ``HPOSet`` can be used to represent e.g. a patient's clinical information. It allows some basic filtering and comparisons to other ``HPOSet``s.

Ontology
--------
The ``Ontology`` represents all HPO terms and their connections and associations. It also contains pointers to associated genes and disease.


Installation / Setup
--------------------
This is not yet defined. I'm planning on adding PyHPO to PyPy, so you can install it via pip. For now, you need to install it manually. The easiest way to do so is:

..code:: bash
    HPO_DIR=/your/desired/path
    cd ${HPO_DIR}
    git clone https://github.com/anergictcell/pyhpo.git
    virtualenv pyhpo

    ln -s pyhpo ${HPO_DIR}/lib/python/


Usage
-----
For a detailed description of how to use PyHPO, visit the documentation at https://esbme.com/pyhpo/docs/

..code: python

    ontology = Ontology()
    
    # Add genes and OMIM disease associations
    ontology.add_anotations()
    
    # Iterate through all HPO terms
    for term in ontology:
        # do something

There are multiple ways to retrieve a single term out of an ontology:

..code: python

    # Retrieve a term via its HPO-ID
    term = ontology.get_hpo_object('HP:0002650')

    # ...or via the Integer representation of the ID
    term = ontology.get_hpo_object(2650)

    # ...or via shortcut
    term = ontology[2650]

    # ...or by term name
    term = ontology.get_hpo_object('Scoliosis')

You can also do substring search on term names and synonyms:

..code: python

    # ontology.search returns an Iterator over all matches
    for term in ontology.search('Abn'):
        print(term.name)

Find the shortest path between two terms:

..code: python
    ontology.path(
        'Abnormality of the nervous system',
        'HP:0002650'
    )

and many more examples in the `PyHPO Documentation`_

Contributing
------------
Yes, please do so. I would appreciate any help, suggestions for improvement or other feedback. Just create a pull-request or open an issue.

License
-------

PyHPO is released under the `MIT license`_.


.. _PyHPO Documentation: ttps://esbme.com/pyhpo/docs/ 
.. _MIT license: http://www.opensource.org/licenses/mit-license.php
.. _Human Phenotype Ontology: https://hpo.jax.org/