HPOSet
====================
``HPOSet`` instances contains a set of HPO terms. This class is useful to represent a patient's clinical information.

It provides analytical helper functions to narrow down the actual provided clinical information.


``HPOSet`` class
*****************
.. autoclass:: pyhpo.set.HPOSet
   :no-private-members:
   :no-special-members:


child_nodes
--------------------
.. automethod:: pyhpo.set.HPOSet.child_nodes

all_genes
--------------------
.. automethod:: pyhpo.set.HPOSet.all_genes

information_content
--------------------
.. automethod:: pyhpo.set.HPOSet.information_content

variance
--------------------
.. automethod:: pyhpo.set.HPOSet.variance

combinations
--------------------
.. automethod:: pyhpo.set.HPOSet.combinations

combinations_one_way
--------------------
.. automethod:: pyhpo.set.HPOSet.combinations_one_way

similarity
--------------------
.. automethod:: pyhpo.set.HPOSet.similarity

Class methods
************************

from_ontology
--------------------
.. automethod:: pyhpo.set.HPOSet.from_ontology
