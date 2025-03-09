Ontology
====================

The ``Ontology`` contains all ``HPOTerm`` s and thus reflects the full ontology including links and information about inheritance

    .. note::

        Starting with `pyhpo 4.0`, the Ontology will link genes non-transitive to HPO terms.
        This means it will be the same behavior as the `hpo3` library.
        See https://github.com/anergictcell/hpo/issues/44 and
        https://github.com/anergictcell/pyhpo/issues/26 for details about this.


``Ontology`` class
********************
.. autoclass:: pyhpo.ontology.OntologyClass
   :no-private-members:
   :no-special-members:


get_hpo_object
--------------
.. automethod:: pyhpo.ontology.OntologyClass.get_hpo_object

match
--------------
.. automethod:: pyhpo.ontology.OntologyClass.match

path
--------------
.. automethod:: pyhpo.ontology.OntologyClass.path

search
--------------
.. automethod:: pyhpo.ontology.OntologyClass.search

synonym_match
--------------
.. automethod:: pyhpo.ontology.OntologyClass.synonym_match

synonym_search
--------------
.. automethod:: pyhpo.ontology.OntologyClass.synonym_search

to_dataframe
--------------
.. automethod:: pyhpo.ontology.OntologyClass.to_dataframe
